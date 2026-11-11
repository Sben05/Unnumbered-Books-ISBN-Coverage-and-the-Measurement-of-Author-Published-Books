"""Build US_2025.csv, Canada_2025.csv and Conflicts_2025.csv from the raw Open Library editions dump.

Step 1 (DuckDB): scan data/raw/ and keep every edition whose publish_date mentions 2025.
               Saved untouched to data/interim/editions_2025.parquet so exclusions can be revisited.
Step 2 (Python): clean ISBNs, classify country, dedupe, write the CSVs to output/.

Canada has no ISBN group of its own: English-Canadian publishers use 978-0/978-1 (shared with the
US, UK, ...) and French-Canadian publishers use 978-2 (shared with France, Belgium, ...). So a
Canadian ISBN can only be placed in Canada via publication metadata.
"""
import json
import re
from pathlib import Path

import duckdb
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent
RAW_GLOB = str(ROOT / "data/raw/open-library/data/editions/*.parquet")
INTERIM = ROOT / "data/interim/editions_2025.parquet"
OUT = ROOT / "output"

COLUMNS = ["isbn13", "title", "publisher", "publication_date",
           "publication_country", "isbn_country", "openlibrary_id"]

US, CANADA = "United States", "Canada"
ISBN_US = US
ISBN_SHARED_EN, ISBN_SHARED_FR = "Shared English (978-0/978-1)", "Shared French (978-2)"
ISBN_OTHER = "Other"

# MARC country codes: US states, DC and "xxu"; Canadian provinces/territories and "xxc".
MARC = {
    US: set("""alu aku azu aru cau cou ctu deu dcu flu gau hiu idu ilu inu iau ksu kyu lau meu mdu
mau miu mnu msu mou mtu neu nvu nhu nju nmu nyu ncu ndu ohu oku oru pau riu scu sdu tnu txu utu vtu
vau wau wvu wiu wyu xxu""".split()),
    CANADA: set("abc bcc mbc nkc nfc nsc ntc nuc onc pic quc snc ykc xxc".split()),
}

# Fallback when publish_country is missing: match free-text publish_places.
US_STATES = ("alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|"
             "georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|"
             "massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|"
             "new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|"
             "oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|"
             "texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming")
PLACE_PATTERNS = {
    US: [
        re.compile(
            r"\b(united states|u\.s\.a?\.?|usa|" + US_STATES + r"|"
            r"los angeles|san francisco|chicago|boston|philadelphia|seattle|houston|dallas|austin|"
            r"atlanta|miami|denver|minneapolis|nashville|brooklyn|manhattan|san diego)\b", re.I),
        # ", NY" style postal abbreviations; case-sensitive. "IN" left out: matches "in" too often.
        re.compile(
            r",\s*(AL|AK|AZ|AR|CA|CO|CT|DE|DC|FL|GA|HI|ID|IL|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|"
            r"NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b"),
    ],
    CANADA: [
        re.compile(
            r"\b(canada|ontario|qu[eé]bec|british columbia|alberta|manitoba|saskatchewan|"
            r"nova scotia|new brunswick|newfoundland|labrador|prince edward island|yukon|"
            r"northwest territories|nunavut|toronto|montr[eé]al|vancouver|ottawa|calgary|edmonton|"
            r"winnipeg|halifax|saskatoon|regina|gatineau|laval|sherbrooke|trois-rivi[eè]res|"
            r"mississauga|brampton|kingston, on|victoria, b\.?c\.?)\b", re.I),
        re.compile(r",\s*(ON|QC|BC|AB|MB|SK|NS|NB|NL|PE|YT|NT|NU|B\.C\.|Ont\.|Qué\.|Que\.)(\b|\s|$)"),
    ],
}


def extract_2025():
    INTERIM.parent.mkdir(parents=True, exist_ok=True)
    duckdb.sql(f"""
        COPY (
            SELECT * FROM read_parquet('{RAW_GLOB}')
            WHERE regexp_matches(publish_date, '(^|[^0-9])2025([^0-9]|$)')
        ) TO '{INTERIM}' (FORMAT parquet)
    """)


def as_list(v):
    """Open Library list fields arrive as JSON strings; tolerate real lists and nulls."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return []
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except json.JSONDecodeError:
            return [v]
    return [x for x in v if isinstance(x, str)] if isinstance(v, (list, tuple)) else []


def isbn13_valid(s):
    if not re.fullmatch(r"97[89]\d{10}", s):
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(s[:12]))
    return (10 - total % 10) % 10 == int(s[12])


def isbn10_to_13(s):
    if not re.fullmatch(r"\d{9}[\dX]", s):
        return None
    if sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(s)) % 11:
        return None
    core = "978" + s[:9]
    check = (10 - sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(core)) % 10) % 10
    return core + str(check)


def clean_isbns(isbn13s, isbn10s):
    out = []
    for raw in isbn13s + isbn10s:
        s = re.sub(r"[^0-9Xx]", "", raw).upper()
        if len(s) == 10:
            s = isbn10_to_13(s)
        if s and isbn13_valid(s) and s not in out:
            out.append(s)
    return out


def isbn_country(isbn):
    if isbn.startswith("9798"):
        return ISBN_US
    if isbn.startswith(("9780", "9781")):
        return ISBN_SHARED_EN
    if isbn.startswith("9782"):
        return ISBN_SHARED_FR
    return ISBN_OTHER


def pub_country(code, places):
    """Publication country from MARC code first, publish_places as fallback. '' if unknown."""
    code = (code or "").strip().lower()
    for country, codes in MARC.items():
        if code in codes:
            return country
    if code:
        return code  # some other country; keep the MARC code
    text = " ; ".join(places)
    hits = [c for c, pats in PLACE_PATTERNS.items() if any(p.search(text) for p in pats)]
    return hits[0] if len(hits) == 1 else ""  # both or neither -> unknown


def classify(ic, pc):
    """Return 'US', 'Canada', 'Conflict' or None (excluded)."""
    if ic == ISBN_US:
        return "US" if pc in ("", US) else "Conflict"
    if ic == ISBN_SHARED_EN:
        return {US: "US", CANADA: "Canada"}.get(pc)
    if ic == ISBN_SHARED_FR:
        # French group is legitimately used by Canada (Québec); a US-published 978-2 disagrees.
        return {CANADA: "Canada", US: "Conflict"}.get(pc)
    # ic == Other: only relevant when the metadata says US or Canada
    return "Conflict" if pc in (US, CANADA) else None


def clean_publishers(v):
    names = [re.sub(r"\s+", " ", p).strip() for p in as_list(v)]
    seen = []
    for n in names:
        if n and n not in seen:
            seen.append(n)
    return "; ".join(seen)


def build():
    df = pd.read_parquet(INTERIM, columns=[
        "key", "title", "isbn_10", "isbn_13", "publishers", "publish_date",
        "publish_country", "publish_places"])
    print(f"2025 editions: {len(df):,}")

    rows = []
    for r in df.itertuples(index=False):
        isbns = clean_isbns(as_list(r.isbn_13), as_list(r.isbn_10))
        if not isbns:
            continue
        pc = pub_country(r.publish_country, as_list(r.publish_places))
        publisher = clean_publishers(r.publishers)
        for isbn in isbns:
            rows.append({
                "isbn13": isbn,
                "title": re.sub(r"\s+", " ", r.title or "").strip(),
                "publisher": publisher,
                "publication_date": (r.publish_date or "").strip(),
                "publication_country": pc,
                "isbn_country": isbn_country(isbn),
                "openlibrary_id": r.key,
            })
    rows = pd.DataFrame(rows, columns=COLUMNS)
    print(f"ISBN rows (valid, one per ISBN per edition): {len(rows):,}")

    # One row per ISBN: prefer records with a known country, then a publisher, then the lowest OL id.
    rows["_has_pc"] = rows.publication_country != ""
    rows["_has_pub"] = rows.publisher != ""
    rows["_olnum"] = rows.openlibrary_id.str.extract(r"OL(\d+)M", expand=False).astype(float)
    rows = (rows.sort_values(["_has_pc", "_has_pub", "_olnum"], ascending=[False, False, True])
                .drop_duplicates("isbn13")
                .drop(columns=["_has_pc", "_has_pub", "_olnum"]))
    print(f"Unique ISBNs: {len(rows):,}")

    rows["_class"] = [classify(ic, pc) for ic, pc in zip(rows.isbn_country, rows.publication_country)]
    OUT.mkdir(exist_ok=True)
    for cls, name in [("US", "US_2025.csv"), ("Canada", "Canada_2025.csv"), ("Conflict", "Conflicts_2025.csv")]:
        part = rows[rows._class == cls].sort_values("isbn13")[COLUMNS]
        part.to_csv(OUT / name, index=False)
        print(f"{name}: {len(part):,}")
    print(f"Excluded (neither US nor Canada): {rows._class.isna().sum():,}")


if __name__ == "__main__":
    if not INTERIM.exists():
        extract_2025()
    build()
