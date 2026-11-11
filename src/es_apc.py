"""Add the format-invariant AP rule (ap_pure / ap_consistent) to the Spain classification."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from build_es import CORP,low
from classify_selfpub import norm
from ap_consistent import ap_consistent,PART_ES
R=pd.read_parquet(ROOT/'data/interim/es_classified.parquet',columns=['isbn13','pub_year','publisher','authors_personal','author_is_publisher','service_imprint','service_mixed','self_published_combined','unidentified_publisher','corporate_self'])
cache={}
def pt(pub):
 if pub not in cache:
  pl=low(pub);cache[pub]=norm(CORP.sub(' ',norm(pl,True)),True).split() if pl else []
 return cache[pub]
pure=[]
for pub,au,un in zip(R.publisher,R.authors_personal,R.unidentified_publisher):
 t=pt(pub)
 pure.append(bool(t) and not un and any(ap_consistent(a,t,PART_ES) for a in json.loads(au)))
R['ap_pure']=pure;R['ap_consistent']=R.author_is_publisher|R.ap_pure
R.to_parquet(ROOT/'data/interim/es_classified_apc.parquet',compression='zstd');print(R[R.pub_year.between(2007,2021)].groupby('pub_year')[['author_is_publisher','ap_pure','ap_consistent']].sum().T.to_string())
