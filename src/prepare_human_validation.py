"""Create a blinded pilot sample for human validation of Portugal AP labels.

The coding sheet omits the programmatic self-publishing flag and ISBN status.
The key is stored separately for later error-rate calculations.
"""
from pathlib import Path
import json
import unicodedata
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "archive" / "validation-pilot-200" / "HUMAN_LABEL_SAMPLE.csv"
KEY = ROOT / "output" / "validation" / "human_label_key_2026.csv"
SEED = 20261109
N_PER_CELL = 25


def authors_from_json(value):
    try:
        people = json.loads(value) if isinstance(value, str) else value
    except (ValueError, TypeError):
        people = []
    names = []
    for person in people or []:
        if isinstance(person, dict):
            name = " ".join(str(person.get(k, "")).strip(" ,") for k in ("a", "b"))
            name = " ".join(name.split())
            if name:
                names.append(name)
    return "; ".join(names)


def clean_text(value):
    if pd.isna(value):
        return ""
    return "".join(ch for ch in str(value) if unicodedata.category(ch) not in {"Cc", "Cf"}).strip()


def main():
    records = pd.read_parquet(ROOT / "data" / "interim" / "pt_natbib_records.parquet")
    records = records[records.print_like & records.pt & records.pub_year.between(2010, 2019)].copy()
    records["period"] = records.pub_year.map(lambda y: "pre" if y <= 2014 else "post")
    records["predicted_ap"] = records.ap.astype(bool)
    records["isbn_present"] = records.has_isbn.astype(bool)
    cells = []
    for (_, _, _), group in records.groupby(["period", "predicted_ap", "isbn_present"]):
        if len(group) < N_PER_CELL:
            raise ValueError("A validation stratum has fewer than 25 records")
        cells.append(group.sample(N_PER_CELL, random_state=SEED))
    sample = pd.concat(cells).sample(frac=1, random_state=SEED + 1).reset_index(drop=True)
    sample["sample_id"] = [f"PT-{i:03d}" for i in range(1, len(sample) + 1)]

    raw = pd.read_parquet(ROOT / "data" / "interim" / "pt_raw.parquet",
                          columns=["id", "a700", "a701", "a702", "resp", "subtitle"])
    sample["id"] = sample.id.astype(str)
    raw["id"] = raw.id.astype(str)
    sample = sample.merge(raw, on="id", how="left", validate="one_to_one")
    sample["listed_authors"] = sample.a700.map(authors_from_json)
    for col in ("a701", "a702"):
        extra = sample[col].map(authors_from_json)
        sample["listed_authors"] = sample["listed_authors"].fillna("") + extra.map(lambda x: "; " + x if x else "")
    sample["listed_authors"] = sample.listed_authors.str.strip("; ")

    SHEET.parent.mkdir(parents=True, exist_ok=True)
    KEY.parent.mkdir(parents=True, exist_ok=True)
    sheet = sample[["sample_id", "title", "subtitle", "listed_authors",
                    "resp", "publisher"]].rename(columns={"resp": "statement_of_responsibility"})
    for col in ["title", "subtitle", "listed_authors", "statement_of_responsibility", "publisher"]:
        sheet[col] = sheet[col].map(clean_text)
    sheet["human_label"] = ""
    sheet["confidence"] = ""
    sheet["reason_or_uncertainty"] = ""
    sheet.to_csv(SHEET, index=False)

    key = sample[["sample_id", "id", "pub_year", "period", "predicted_ap", "isbn_present"]]
    key.to_csv(KEY, index=False)
    print(f"Wrote {len(sheet)} blinded records to {SHEET}")
    print(key.groupby(["period", "predicted_ap", "isbn_present"]).size().to_string())


if __name__ == "__main__":
    main()
