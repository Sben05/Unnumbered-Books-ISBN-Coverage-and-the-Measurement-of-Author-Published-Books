"""Period summary tables for the extra countries (reads output/<dir>/<cc>_by_year.csv). Prints markdown."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import pandas as pd
def per(B,lo,hi,col='combined'):
 g=B[B.pub_year.between(lo,hi)]
 return (g[col].sum()/g.print_isbns.sum()*100,int(g.print_isbns.sum())) if len(g) else (float('nan'),0)
rows=[]
for d,cc,name in [x.split(':') for x in sys.argv[1:]]:
 B=pd.read_csv(ROOT/f'output/{d}/{cc}_by_year.csv')
 r=dict(country=name)
 for lo,hi in [(1995,2004),(2005,2009),(2010,2014),(2015,2019),(2020,2023)]:
  v,n=per(B,lo,hi);r[f'{lo}-{hi}']=f'{v:.2f}% (n={n:,})' if n else 'n/a'
 y=B[B.pub_year==2023].iloc[0] if (B.pub_year==2023).any() else None
 r['2023 combined']=f"{y.share_combined*100:.2f}% [{y.combined_wilson_low*100:.2f},{y.combined_wilson_high*100:.2f}]" if y is not None else ''
 m=B[B.pub_year.between(2005,2023)];r['print ISBNs per million (2015-19 mean)']=f"{B[B.pub_year.between(2015,2019)].print_isbns_per_million.mean():.0f}"
 r['self-pub per million (2015-19 mean)']=f"{B[B.pub_year.between(2015,2019)].combined_per_million.mean():.1f}"
 rows.append(r)
D=pd.DataFrame(rows);print('| '+' | '.join(D.columns)+' |');print('|'+'---|'*len(D.columns))
for _,r in D.iterrows():print('| '+' | '.join(str(x) for x in r)+' |')
