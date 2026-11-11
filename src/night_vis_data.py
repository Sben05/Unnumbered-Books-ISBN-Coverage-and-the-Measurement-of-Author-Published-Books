"""Night-vis step 1: build year x outcome count tables for PT and ES (AP, non-AP) over full files to 2025. Output output/night_vis/vis_counts.csv, vis_total_ap.csv."""
import os,sys,warnings; warnings.filterwarnings('ignore')
import numpy as np,pandas as pd
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.insert(0,'src')
from night_h_features import add_prefix
OUT='output/night_vis'; os.makedirs(OUT,exist_ok=True)
Y=range(2005,2025)
rows=[]; tot=[]
def books(c):
    if c=='pt':
        d=pd.read_parquet('data/interim/pt_classified.parquet',columns=['isbn13','record_id','pub_year','ap_consistent','authors_personal'])
        d['ap']=d.ap_consistent
    else:
        d=pd.read_parquet('data/interim/es_classified_apc.parquet',columns=['isbn13','pub_year','ap_consistent','author_is_publisher','authors_personal'])
        d['ap']=d.ap_consistent
    d=d.dropna(subset=['pub_year']); d['pub_year']=d.pub_year.astype(int); d=d.drop_duplicates('isbn13')
    d=add_prefix(d.reset_index(drop=True)); d=d.dropna(subset=['prefix'])
    d['a']=d.authors_personal.astype(str)
    g=d.groupby('prefix')
    d['n_auth']=g.a.transform('nunique'); d['first_year']=g.pub_year.transform('min')
    d['multi']=d.n_auth>=2; d['small']=d.publen<=1; d['firstuse']=d.pub_year==d.first_year
    return d
for c in ['pt','es']:
    d=books(c); print(c,len(d),d.pub_year.min(),flush=True)
    if c=='pt':
        R=pd.read_parquet('data/interim/pt_classified.parquet',columns=['record_id','pub_year','ap_consistent']).drop_duplicates('record_id')
        N=pd.read_parquet('data/interim/pt_noisbn.parquet',columns=['pub_year','ap_consistent'])
        flagN='ap_consistent'; flagR='ap_consistent'
    else:
        R=pd.read_parquet('data/interim/es_classified_apc.parquet',columns=['pub_year','author_is_publisher']).dropna(subset=['pub_year'])
        N=pd.read_parquet('data/interim/es_noisbn.parquet',columns=['pub_year','author_is_publisher'])
        flagN=flagR='author_is_publisher'
    for df in (R,N): df.dropna(subset=['pub_year'],inplace=True); df['pub_year']=df.pub_year.astype(int)
    for y in Y:
        b=d[d.pub_year==y]
        r_=R[R.pub_year==y]; n_=N[N.pub_year==y]
        for grp,ap in (('AP',True),('nonAP',False)):
            bb=b[b.ap==ap]
            ri=int((r_[flagR]==ap).sum()); rn=int((n_[flagN]==ap).sum())
            rows.append(dict(country=c,group=grp,year=y,isbn_rec=ri,noisbn_rec=rn,n_books=len(bb),small=int(bb.small.sum()),firstuse=int(bb.firstuse.sum()),multi=int(bb.multi.sum())))
pd.DataFrame(rows).to_csv(f'{OUT}/vis_counts.csv',index=False); print('done')
