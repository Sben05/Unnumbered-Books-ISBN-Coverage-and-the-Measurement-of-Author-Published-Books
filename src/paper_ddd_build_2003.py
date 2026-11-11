"""Build a consistent country-year panel: books by (self-published AP vs other) x (has ISBN vs none), 2008-2022.
ISBN side: one row per ISBN in <cc>_classified (slightly over-counts multi-ISBN books everywhere). ISBN-less side: <cc>_noisbn (PL,EE,LV,ES,PT) or ISBN-less print records
in <cc>_catalogue classified here with the SAME flags() rule (FR,NZ,UK). Rules differ by country (AP definition) -> only within-country AP-vs-other gaps are compared."""
import sys; from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT/'src'))
import duckdb, pandas as pd, numpy as np
import classify_selfpub as CS
c=duckdb.connect(); rows=[]
def add(cc,df_isbn,df_no):
    a=df_isbn.groupby('y').agg(ap_isbn=('ap','sum'),n_isbn=('ap','size')); b=df_no.groupby('y').agg(ap_noisbn=('ap','sum'),n_no=('ap','size'))
    d=a.join(b,how='outer').fillna(0); d['nonap_isbn']=d.n_isbn-d.ap_isbn; d['nonap_noisbn']=d.n_no-d.ap_noisbn; d['country']=cc; rows.append(d.reset_index())
for cc,apcol,f in [('PT','ap_consistent','pt'),('PL','ap_consistent','pl'),('EE','ap_consistent','ee'),('LV','ap_consistent','lv'),('ES','author_is_publisher','es')]:
    cf=f"data/interim/{f}_classified{'_apc' if f=='es' else ''}.parquet"
    i=c.execute(f"select cast(pub_year as int) y, {apcol} ap from '{cf}' where pub_year between 2003 and 2022").df()
    n=c.execute(f"select cast(pub_year as int) y, {apcol} ap from 'data/interim/{f}_noisbn.parquet' where pub_year between 2003 and 2022").df()
    add(cc,i,n)
for cc in ['fr','nz','uk']:
    i=c.execute(f"select pub_year y, author_is_publisher ap from 'data/interim/{cc}_classified.parquet' where pub_year between 2003 and 2022").df()
    q=c.execute(f"select * from 'data/interim/{cc}_catalogue.parquet' where is_print and country_eligible and is_published and len(isbn13s)=0 and pub_year between 2003 and 2022").df()
    out=[]
    for r in q.to_dict('records'):
        r['isbn13']=''; r['isbn_print']=True; f=CS.flags(r); out.append((int(r['pub_year']),bool(f['author_is_publisher'])))
    n=pd.DataFrame(out,columns=['y','ap']); print(cc,'isbn-less print records classified:',len(n)); add(cc.upper(),i,n)
P=pd.concat(rows); P.to_csv('output/paper_pt/ddd_panel_2003.csv',index=False)
pd.set_option('display.width',220)
P['ap_no_sh']=P.ap_noisbn/(P.ap_isbn+P.ap_noisbn); P['non_no_sh']=P.nonap_noisbn/(P.nonap_isbn+P.nonap_noisbn)
print(P[P.y.between(2010,2019)].pivot(index='y',columns='country',values='ap_no_sh').round(3).to_string())
print(P[P.y.between(2010,2019)].pivot(index='y',columns='country',values='non_no_sh').round(3).to_string())
print(P[P.y.between(2010,2019)].assign(apn=lambda d:d.ap_isbn+d.ap_noisbn).pivot(index='y',columns='country',values='apn').to_string())
