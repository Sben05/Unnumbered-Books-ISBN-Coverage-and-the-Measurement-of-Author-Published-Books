"""Exposure design v3 = v2 with ALL publishers and size strata (MAXN env).
Exposure design v2 (no mechanical selection): exposure defined from ISBN books published <=2012 (prefix type + estimated remaining numbers at end-2012);
outcome = no-ISBN share of SEPARATE books published 2013-2014 (pre) vs 2015-2019 (post) by the same publisher key. Small publishers (<=15 books 2005-12)."""
import re, unicodedata; from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import pandas as pd, numpy as np, duckdb, statsmodels.formula.api as smf
L=pd.read_excel(ROOT/'data/raw/apel/20251231_Prefixos_ISBN.xlsx'); L.columns=['prefix','holder']
L['p']=L.prefix.str.replace('-','',regex=False); L=L[L.p.str.startswith('978')].drop_duplicates('p'); L=L[~L.p.isin(['97898920','97898933'])]
cap={p:10**(12-len(p)) for p in L.p}; bylen={}; [bylen.setdefault(len(p),set()).add(p) for p in cap]; lens=sorted(bylen,reverse=True)
def prefix_of(i):
    for k in lens:
        if i[:k] in bylen[k]: return i[:k]
c=duckdb.connect()
cl=c.execute("select isbn13, pub_year from 'data/interim/pt_classified.parquet' where pub_year<=2012").df(); cl['pref']=cl.isbn13.map(prefix_of)
used=cl.dropna(subset=['pref']).groupby('pref').isbn13.nunique()
R=pd.read_parquet(ROOT/'data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2005,2019)].copy()
def norm(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s)).strip()
R['pk']=R.publisher.map(norm); R=R[R.pk!='']; R['pref']=R.isbn_first.map(lambda i:prefix_of(i) if i else None)
R['noisbn']=(~R.has_isbn).astype(int)
early=R[R.pub_year<=2012]; n_early=early.groupby('pk').size()
ib=early[early.has_isbn]
rows=[]
for pk,g in ib.groupby('pk'):
    prefs=g.pref.dropna().unique()
    if len(prefs)==0 and g.author_ed_prefix.any(): rows.append((pk,'single_use',0.0))
    elif len(prefs)>0:
        rem=sum(max(0,cap[p]-used.get(p,0)) for p in prefs); rows.append((pk,'block_exhausted' if rem<=1 else 'block_some_left' if rem<=4 else 'block_much_left',float(rem)))
E=pd.DataFrame(rows,columns=['pk','group','remaining']).set_index('pk'); E['n_early']=n_early.reindex(E.index).values; E['size']=pd.cut(E.n_early,[0,3,15,1e9],labels=['1-3','4-15','16+']); print(E.group.value_counts().to_dict())
out=R[R.pub_year>=2013].merge(E[['group']],left_on='pk',right_index=True); out['post']=(out.pub_year>=2015).astype(int)
t=out.groupby(['group','post']).agg(books=('id','size'),noisbn=('noisbn','sum'),publishers=('pk','nunique')); t['share']=t.noisbn/t.books; print(t.round(3).to_string())
ts=out.merge(E[['size']],left_on='pk',right_index=True).groupby(['size','group','post'],observed=True).agg(books=('id','size'),noisbn=('noisbn','sum')); ts['share']=ts.noisbn/ts.books; print(ts.round(3).to_string()); ts.to_csv(ROOT/'output/paper_pt/exposure_v3_by_size.csv')
# does anyone publish again? extensive margin: share of early publishers with any book 2015-19, by group
act15=set(R[R.pub_year>=2015].pk); E['active_post']=E.index.isin(act15); E['active_pre']=E.index.isin(set(R[R.pub_year.between(2013,2014)].pk))
print(E.groupby('group')[['active_pre','active_post']].mean().round(3))
# regression: noisbn ~ post*group, ref=block_much_left, cluster by publisher
out['grp']=pd.Categorical(out.group,categories=['block_much_left','block_some_left','block_exhausted','single_use'])
m=smf.logit('noisbn ~ post*C(grp)',data=out).fit(disp=0,cov_type='cluster',cov_kwds={'groups':out.pk.astype('category').cat.codes})
res=pd.DataFrame({'coef':m.params,'se':m.bse,'p':m.pvalues}); print(res.round(3).to_string())
res.to_csv(ROOT/'output/paper_pt/exposure_v3_logit.csv'); t.to_csv(ROOT/'output/paper_pt/exposure_v3_table.csv'); E.to_csv(ROOT/'output/paper_pt/exposure_v3_publishers.csv')
# same, AP-flagged books only
a=out[out.ap]; ta=a.groupby(['group','post']).agg(books=('id','size'),noisbn=('noisbn','sum')); ta['share']=ta.noisbn/ta.books; print('--- AP-flagged'); print(ta.round(3).to_string())
