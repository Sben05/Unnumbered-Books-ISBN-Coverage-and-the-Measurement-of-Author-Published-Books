"""Extract official author-depositor counts and denominators from BnF workbooks."""
import re,json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent.parent
rows=[]
for p in sorted((ROOT/'data/raw/evidence').glob('*livres*.xls')):
 m=re.search(r'(20\d{2})',p.name)
 if not m:continue
 report_year=int(m.group());x=pd.ExcelFile(p)
 if 'Déposants' not in x.sheet_names:continue
 d=x.parse('Déposants',header=None).fillna('')
 indices=d.index[d.iloc[:,0].astype(str).str.contains('Auteurs auto-édités',regex=False)]
 if not len(indices):continue
 i=indices[0]
 # Three consecutive year blocks, with counts (depositors,new depositors,deposits).
 for offset,y in enumerate(range(report_year-2,report_year+1)):
  col=3+3*offset
  count=int(d.iloc[i,col])
  # Category-table total occurs after the author category row.
  totals=[j for j in range(i+1,min(i+25,len(d))) if str(d.iloc[j,0]).lower().startswith('total')]
  if not totals:raise ValueError((p,'No category total'))
  total=int(d.iloc[totals[0],col])
  rows.append(dict(year=y,author_depositor_books=count,total_deposited_books=total,share=count/total,report_year=report_year,workbook=p.name,sheet='Déposants',excel_row=i+1,excel_column=col+1,definition='Author-depositor category only; excludes service firms classified as publishers; deposit year, all ISBN statuses'))
d=pd.DataFrame(rows).sort_values('report_year').drop_duplicates('year',keep='last').sort_values('year');d.to_csv(ROOT/'output/selfpub/bnf_official_benchmarks.csv',index=False);print(d[['year','author_depositor_books','total_deposited_books','share']].to_string(index=False))
