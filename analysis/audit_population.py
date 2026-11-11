"""Reconcile the older extraction with the retained analytical population.

Optional source audit: requires processed source-project Parquet files and pyarrow.
Usage: python audit_population.py /path/to/ISBNResearch
The resulting CSV and TeX are frozen with the package for manuscript compilation.
"""
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=Path(sys.argv[1])
    b=pd.read_parquet(source/'data/interim/bnp_csv_bibliografianacional.parquet',columns=['id','material'])
    raw=pd.read_parquet(source/'data/interim/pt_raw.parquet',columns=['id','pubdate','f100'])
    filtered=pd.read_parquet(source/'data/interim/pt_natbib_records.parquet')
    books=b[b.material=='Book'].copy()
    books['id']=books.id.astype(str);raw['id']=raw.id.astype(str)
    matched=raw[raw.id.isin(set(books.id))].copy()
    assert books.id.is_unique and matched.id.is_unique
    year=pd.to_numeric(matched.pubdate.str.extract(r'(?<!\d)(1[5-9]\d\d|20\d\d)(?!\d)')[0],errors='coerce')
    fallback=pd.to_numeric(matched.f100.str[9:13],errors='coerce')
    take=year.isna()&fallback.between(1500,2100);year.loc[take]=fallback[take]
    assert set(matched.loc[year.between(2005,2025),'id'])==set(filtered.id.astype(str))
    retained=filtered[filtered.print_like&filtered.pt]
    frozen=pd.read_csv(ROOT/'inputs/records.csv',usecols=['id'],dtype={'id':str})
    assert set(retained.id.astype(str))==set(frozen.id)
    rows=[('Bibliography records labelled as books',len(books),None),
          ('Matched to fuller catalogue metadata',len(matched),len(books)-len(matched)),
          ('With a usable publication year',int(year.notna().sum()),int(year.isna().sum())),
          ('Publication year 2005--25',len(filtered),int((year.notna()&~year.between(2005,2025)).sum())),
          ('Pass print-monograph filter',int(filtered.print_like.sum()),int((~filtered.print_like).sum())),
          ('Portuguese country metadata: retained export',len(retained),int((filtered.print_like&~filtered.pt).sum())),
          ('Analysis history, publication years 2005--19',int(retained.pub_year.between(2005,2019).sum()),None),
          ('Main comparison, publication years 2010--19',int(retained.pub_year.between(2010,2019).sum()),None)]
    table=pd.DataFrame(rows,columns=['stage','records','excluded_at_stage'])
    table.to_csv(ROOT/'results/population_flow.csv',index=False)
    tex=[r'\begin{table}[htbp]\centering\small',
         r'\caption{From the earlier extraction to the analytical population}\label{tab:population}',
         r'\begin{tabular}{p{.64\linewidth}rr}\toprule',
         r'Stage & Records & Excluded\\\midrule']
    tex += [f'{label} & {n:,} & '+(f'{ex:,}' if ex is not None else '')+r'\\' for label,n,ex in rows]
    tex += [r'\bottomrule\end{tabular}',
            r'\notes{The first six rows are sequential restrictions. Missing catalogue matches and missing years prevent eligibility from being established. The final two rows select publication-year windows from the retained export; they are not additional quality exclusions. No selection in this flow requires ISBN presence or a positive author-publisher flag.}',
            r'\end{table}']
    (ROOT/'results/table_population.tex').write_text('\n'.join(tex)+'\n')
    print(table.to_string(index=False))


if __name__=='__main__':
    main()
