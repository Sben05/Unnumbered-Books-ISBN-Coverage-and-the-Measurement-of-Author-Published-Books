"""BNP national-bibliography universe (bibliografianacional.csv, BNP open data, snapshot 2026-01-07):
classify every printed monograph (with or without ISBN) with the SAME author=publisher rule as build_pt.py,
and tabulate ISBN presence x AP by publication year. Universe is defined by BNP's national bibliography, not by ISBN."""
import sys; from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT/'src'))
import pandas as pd, numpy as np, duckdb, json
import build_pt as B
bn=pd.read_parquet(ROOT/'data/interim/bnp_csv_bibliografianacional.parquet',columns=['id','material','isbn','dl'])
ids=set(bn[bn.material=='Book'].id)
raw=pd.read_parquet(ROOT/'data/interim/pt_raw.parquet')
raw['id']=raw['id'].astype(str); d=raw[raw.id.isin(ids)].copy()
print('BN book ids',len(ids),'matched in pt_raw',len(d))
y=d.pubdate.str.extract(r'(?<!\d)(1[5-9]\d\d|20\d\d)(?!\d)')[0]; y2=pd.to_numeric(d.f100.str[9:13],errors='coerce')
d['pub_year']=pd.to_numeric(y,errors='coerce'); m=d.pub_year.isna()&y2.between(1500,2100); d.loc[m,'pub_year']=y2[m]
d=d[d.pub_year.between(2005,2025)]
d['print_like']=(d.ltype=='a')&(d.llevel=='m')&d.f106.isin(['r',''])&~d.extent.map(lambda x:bool(B.NONPRINT_EXT.match(x)))
d['pt']=d.country=='PT'
isb=d.isbn_raw.map(lambda r:B.parse_isbns(r)[0]); d['has_isbn']=isb.map(len)>0
d['isbn_first']=isb.map(lambda l:sorted(l)[0] if l else '')
d['author_ed_prefix']=d.isbn_first.str.startswith(('97898920','97898933'))
d['pt_prefix']=d.isbn_first.str.startswith(('978972','978989'))
d['foreign_prefix']=d.has_isbn&~d.pt_prefix
d['has_dl']=d.dl.str.strip()!=''
out=[]
for idx,r in d.iterrows():
    rr=r.to_dict(); rr['pub_year']=int(rr['pub_year']); f=B.flags(rr)
    out.append((idx,f['ap_consistent'],f['author_is_publisher'],f['service_imprint'],f['corporate_self'],f.get('government',False),f['unidentified_publisher']))
F=pd.DataFrame(out,columns=['idx','ap','ap_orig','service','corp_self','gov','nopub']).set_index('idx')
d=d.join(F)
keep=['id','pub_year','cat_year_raw','print_like','pt','has_isbn','isbn_first','author_ed_prefix','pt_prefix','foreign_prefix','has_dl','ap','ap_orig','service','corp_self','gov','nopub','publisher','title','extent']
d['cat_year_raw']=pd.to_numeric(d.f100.str[:4],errors='coerce')
d[keep].to_parquet(ROOT/'data/interim/pt_natbib_records.parquet')
s=d[d.print_like&d.pt]
g=s.groupby('pub_year').agg(books=('id','size'),isbn=('has_isbn','sum'),dl=('has_dl','sum'),
    ap=('ap','sum'),ap_isbn=('ap',lambda x:(x&s.loc[x.index,'has_isbn']).sum()),
    ap_noisbn=('ap',lambda x:(x&~s.loc[x.index,'has_isbn']).sum()),
    nonap_noisbn=('ap',lambda x:(~x&~s.loc[x.index,'has_isbn']).sum()),
    author_ed=('author_ed_prefix','sum'),foreign=('foreign_prefix','sum'),
    nopub_noisbn=('nopub',lambda x:(x&~s.loc[x.index,'has_isbn']).sum()),
    gov_noisbn=('gov',lambda x:(x&~s.loc[x.index,'has_isbn']).sum()))
g['noisbn']=g.books-g.isbn; g['noisbn_share']=g.noisbn/g.books
g['ap_noisbn_share_of_ap']=g.ap_noisbn/g.ap; g['nonap_noisbn_share_of_nonap']=g.nonap_noisbn/(g.books-g.ap)
g.to_csv(ROOT/'output/paper_pt/natbib_isbn_by_ap_year.csv')
pd.set_option('display.width',250); print(g.round(3).to_string())
