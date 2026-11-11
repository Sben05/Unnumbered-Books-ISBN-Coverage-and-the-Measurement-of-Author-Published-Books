"""Build NZ_2025.csv from the National Library of New Zealand's Publications NZ MARCXML dump.

Step 1: stream every record out of data/raw/natlibnz/pubsnzmetadataxml.zip (left untouched) into
        data/interim/nlnz_records.parquet, one row per record, all years.
Step 2: keep records with 008 place-of-publication "nz" and year 2025, one row per valid ISBN.

Publications NZ is a national bibliography, so it also lists works about NZ or by NZ authors that were
published abroad; the 008 country code is what separates those out.

Run with: .venv/bin/python -I build_nz.py
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))  # -I drops the script dir from sys.path; we need build_2025's helpers

import pandas as pd  # noqa: E402

import build_2025 as b  # noqa: E402

ZIP = ROOT / "data/raw/natlibnz/pubsnzmetadataxml.zip"
INTERIM = ROOT / "data/interim/nlnz_records.parquet"
OUT = b.OUT
COLUMNS = ["isbn13", "title", "publisher", "publication_date",
           "publication_country", "isbn_country", "nlnz_id"]

M = "{http://www.loc.gov/MARC21/slim}"
NZ = "New Zealand"


def subfields(field, codes):
    return [sf.text or "" for sf in field.findall(f"{M}subfield") if sf.get("code") in codes]


def tidy(s):
    """Strip MARC's trailing punctuation (' :', ' ;', ',', '.') and brackets from a 26x subfield."""
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[\s:;,/=]+$", "", s)
    return s.strip("[] ").strip()


def parse_record(rec):
    leader = (rec.findtext(f"{M}leader") or "").ljust(24)
    ctrl = {cf.get("tag"): cf.text or "" for cf in rec.findall(f"{M}controlfield")}
    f008 = ctrl.get("008", "").ljust(40)
    isbns, titles, places, pubs, dates = [], [], [], [], []
    for df in rec.findall(f"{M}datafield"):
        tag = df.get("tag")
        if tag == "020":
            isbns += subfields(df, "a")
        elif tag == "245" and not titles:
            titles.append(" ".join(subfields(df, "ab")))
        # 260 = older publication statement; 264 ind2 "1" = publication (not distribution/copyright)
        elif tag == "260" or (tag == "264" and df.get("ind2") == "1"):
            places += subfields(df, "a")
            pubs += subfields(df, "b")
            dates += subfields(df, "c")
    return {
        "nlnz_id": ctrl.get("001", ""),
        "entered": f008[0:6],         # yymmdd the record was created (measures cataloguing lag)
        "record_type": leader[6],     # a = language material, m = computer file, e = map, ...
        "bib_level": leader[7],       # m = monograph, s = serial
        "date_type": f008[6],
        "date1": f008[7:11],
        "country_008": f008[15:18].strip(),
        "isbn_raw": isbns,
        "title": tidy(titles[0]) if titles else "",
        "places": [tidy(p) for p in places],
        "publishers": [tidy(p) for p in pubs],
        "date_26x": "; ".join(tidy(d) for d in dates),
    }


def extract_records():
    INTERIM.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with zipfile.ZipFile(ZIP) as z, z.open(z.namelist()[0]) as fh:
        for _, el in ET.iterparse(fh, events=("end",)):
            if el.tag == f"{M}record":
                rows.append(parse_record(el))
                el.clear()
                if len(rows) % 200_000 == 0:
                    print(f"  parsed {len(rows):,} records", flush=True)
    pd.DataFrame(rows).to_parquet(INTERIM, index=False)
    print(f"Wrote {INTERIM} ({len(rows):,} records)")


def build():
    df = pd.read_parquet(INTERIM)
    print(f"All records: {len(df):,}")
    y = df[df.date1 == "2025"]
    print(f"Dated 2025 (008): {len(y):,}   of which published in NZ: {(y.country_008 == 'nz').sum():,}")

    rows = []
    for r in y.itertuples(index=False):
        isbns = b.clean_isbns(list(r.isbn_raw), [])
        pc = NZ if r.country_008 == "nz" else r.country_008
        publisher = "; ".join(dict.fromkeys(p for p in r.publishers if p))
        for isbn in isbns:
            rows.append({
                "isbn13": isbn,
                "title": r.title,
                "publisher": publisher,
                "publication_date": r.date_26x or r.date1,
                "publication_country": pc,
                "isbn_country": b.isbn_country(isbn),
                "nlnz_id": r.nlnz_id,
            })
    rows = pd.DataFrame(rows, columns=COLUMNS)
    print(f"ISBN rows: {len(rows):,}")

    # One row per ISBN: prefer an NZ-published record with a publisher, then the lowest record id.
    rows = (rows.assign(_nz=rows.publication_country == NZ, _pub=rows.publisher != "")
                .sort_values(["_nz", "_pub", "nlnz_id"], ascending=[False, False, True])
                .drop_duplicates("isbn13").drop(columns=["_nz", "_pub"]))

    nz = rows[rows.publication_country == NZ]
    # NZ ISBNs sit inside the shared English groups; anything else on an NZ-published book disagrees.
    ok = nz.isbn_country == b.ISBN_SHARED_EN
    for part, name in [(nz[ok], "NZ_2025.csv"), (nz[~ok], "NZ_Conflicts_2025.csv")]:
        part.sort_values("isbn13")[COLUMNS].to_csv(OUT / name, index=False)
        print(f"{name}: {len(part):,}")
    print(f"Excluded (2025 ISBNs published outside NZ): {(rows.publication_country != NZ).sum():,}")


if __name__ == "__main__":
    if not INTERIM.exists():
        extract_records()
    build()
