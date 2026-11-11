"""Exposure design: did publishers who likely had NO unused ISBNs left at end-2014 drop the ISBN more after the 2015 charge?
Capacity from APEL prefix length (11 digits=10 ISBNs, 10=100, 9=1000, 8 (989-20/-33)=single-use). Used = distinct ISBN-13 under the prefix in BNP with pub_year<=2014.
Publisher key = normalised publisher string in the BNP national bibliography (book-level, ISBN or not). Descriptive/suggestive; exposure is an ESTIMATE."""
import sys, re, unicodedata; from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import pandas as pd, numpy as np, duckdb
L=pd.read_excel(ROOT/'data/raw/apel/20251231_Prefixos_ISBN.xlsx'); L.columns=['prefix','holder']
L['p']=L.prefix.str.replace('-','',regex=False); L=L[L.p.str.startswith('978')].drop_duplicates('p')
L=L[~L.p.isin(['97898920','97898933'])]          # shared single-use bases handled separately
cap={p:10**(12-len(p)) for p in L.p}
bylen={}; [bylen.setdefault(len(p),set()).add(p) for p in cap]; lens=sorted(bylen,reverse=True)
def prefix_of(i):
    for k in lens:
        if i[:k] in bylen[k]: return i[:k]
    return None
c=duckdb.connect()
cl=c.execute("select isbn13, pub_year from 'data/interim/pt_classified.parquet' where pub_year<=2014").df()
cl['pref']=cl.isbn13.map(prefix_of); used=cl.dropna(subset=['pref']).groupby('pref').isbn13.nunique()
R=pd.read_parquet(ROOT/'data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2010,2019)].copy()
def norm(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s)).strip()
R['pk']=R.publisher.map(norm); R=R[R.pk!='']
R['pref']=R.isbn_first.map(lambda i:prefix_of(i) if i else None)
R['single']=R.author_ed_prefix
R['post']=(R.pub_year>=2015).astype(int); R['noisbn']=(~R.has_isbn).astype(int)
pre=R[(R.post==0)&R.has_isbn]
# publisher-level exposure from pre-2015 ISBN books
def expo(g):
    prefs=g.pref.dropna().unique(); singles=g.single.sum()
    if len(prefs)==0 and singles>0: return pd.Series(dict(kind='single',remaining=0.0,n_pref=0))
    rem=sum(max(0,cap[p]-used.get(p,0)) for p in prefs); return pd.Series(dict(kind='block',remaining=float(rem),n_pref=len(prefs)))
E=pre.groupby('pk').apply(expo)
pre_cnt=R[R.post==0].groupby('pk').size().rename('n_pre')
E=E.join(pre_cnt); E=E[E.n_pre<=20]            # small publishers (<=20 books 2010-14)
E['group']=np.where(E.kind=='single','single_use',np.where(E.remaining<=1,'block_exhausted',np.where(E.remaining<=4,'block_some_left','block_much_left')))
print(E.group.value_counts())
E.to_csv(ROOT/'output/paper_pt/exposure_publishers.csv')
D=R.merge(E[['group']],left_on='pk',right_index=True)
tab=D.groupby(['group','post']).agg(books=('id','size'),noisbn=('noisbn','sum'),publishers=('pk','nunique'))
tab['noisbn_share']=tab.noisbn/tab.books; print(tab.round(3).to_string())
# extensive margin: still publishing in 2015-19?
act=D[D.post==1].groupby('pk').size(); E['active_post']=E.index.isin(act.index); print(E.groupby('group').active_post.mean().round(3))
# AP-flagged subset
Dap=D[D.ap]; tap=Dap.groupby(['group','post']).agg(books=('id','size'),noisbn=('noisbn','sum')); tap['share']=tap.noisbn/tap.books; print('--- AP-flagged books only'); print(tap.round(3).to_string())
D.to_parquet(ROOT/'data/interim/pt_exposure_books.parquet')
