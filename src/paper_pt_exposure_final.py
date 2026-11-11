"""Exposure design (grandfathering). At cutoff year C, classify each producer (publisher key) using only ISBN books published <= C:
  EXPOSED = (a) author-edition-only holder (989-20/-33: every new ISBN is a new request) or (b) block holder with <=1 estimated unused number (capacity from APEL prefix length minus distinct ISBNs seen in BNP <= C);
  NOT EXPOSED = block holder with >=5 estimated unused numbers. (2-4 left = 'borderline', reported separately.)
Outcome: share of the producer's books published in C+1..C+3 that have NO ISBN. Real cutoff C=2014 (outcome 2015-17); placebo cutoffs C=2008..2011 (no fee). Gap = exposed - not exposed.
Difference-in-gaps = real gap minus mean placebo gap; producer-level bootstrap CIs. Exposure measured with error (APEL usage counts not public). Exposed = needing a new request = fee AND online form together."""
import re, unicodedata, numpy as np, pandas as pd, duckdb
L=pd.read_excel('data/raw/apel/20251231_Prefixos_ISBN.xlsx'); L.columns=['prefix','holder']; L['p']=L.prefix.str.replace('-','',regex=False)
L=L[L.p.str.startswith('978')].drop_duplicates('p'); L=L[~L.p.isin(['97898920','97898933'])]
cap={p:10**(12-len(p)) for p in L.p}; bylen={}; [bylen.setdefault(len(p),set()).add(p) for p in cap]; lens=sorted(bylen,reverse=True)
def prefix_of(i):
    if not i: return None
    for k in lens:
        if i[:k] in bylen[k]: return i[:k]
c=duckdb.connect(); cl=c.execute("select isbn13, pub_year from 'data/interim/pt_classified.parquet' where pub_year between 1990 and 2018").df(); cl['pref']=cl.isbn13.map(prefix_of); cl=cl.dropna(subset=['pref'])
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2005,2018)].copy(); R['y']=R.pub_year.astype(int)
def norm(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s)).strip()
R['pk']=R.publisher.map(norm); R=R[R.pk!='']; R['noisbn']=(~R.has_isbn).astype(int); R['pref']=R.isbn_first.map(prefix_of)
def build(C,win=3):
    used=cl[cl.pub_year<=C].groupby('pref').isbn13.nunique()
    pre=R[(R.y<=C)&R.has_isbn]; kinds={}
    for pk,g in pre.groupby('pk'):
        prefs=g.pref.dropna().unique()
        if len(prefs)==0:
            if g.author_ed_prefix.any(): kinds[pk]=('exposed','single_use',0.0)
            continue
        rem=sum(max(0,cap[p]-used.get(p,0)) for p in prefs); kinds[pk]=('exposed' if rem<=1 else 'borderline' if rem<5 else 'not_exposed','block',float(rem))
    K=pd.DataFrame(kinds,index=['grp','kind','rem']).T
    post=R[R.y.between(C+1,C+win)].merge(K[['grp','kind']],left_on='pk',right_index=True)
    K['active']=K.index.isin(set(R[R.y.between(C+1,C+win)].pk)); return K,post
res=[]; rng=np.random.default_rng(9)
def gap_stats(post,nb=800):
    out={}
    for g in ['exposed','borderline','not_exposed']:
        d=post[post.grp==g]; out[g]=(d.noisbn.mean() if len(d) else np.nan,len(d),d.pk.nunique())
    # producer bootstrap of the gap exposed - not_exposed
    e=post[post.grp=='exposed'].groupby('pk').noisbn.agg(['sum','size']); n=post[post.grp=='not_exposed'].groupby('pk').noisbn.agg(['sum','size'])
    bs=[]
    for _ in range(nb):
        ie=rng.integers(0,len(e),len(e)); iN=rng.integers(0,len(n),len(n)); bs.append(e['sum'].values[ie].sum()/e['size'].values[ie].sum()-n['sum'].values[iN].sum()/n['size'].values[iN].sum())
    gap=out['exposed'][0]-out['not_exposed'][0]; return out,gap,np.percentile(bs,[2.5,97.5]),np.array(bs)
boots={}
for C in [2008,2009,2010,2011,2014]:
    K,post=build(C); out,gap,ci,bs=gap_stats(post); boots[C]=bs
    act=K.groupby('grp').active.mean().round(3).to_dict()
    res.append(dict(cutoff=C,window=f'{C+1}-{C+3}',producers_exposed=int((K.grp=='exposed').sum()),producers_not_exposed=int((K.grp=='not_exposed').sum()),
        noisbn_exposed=out['exposed'][0],books_exposed=out['exposed'][1],noisbn_not_exposed=out['not_exposed'][0],books_not_exposed=out['not_exposed'][1],gap_pp=100*gap,ci_low=100*ci[0],ci_high=100*ci[1],
        still_publishing_exposed=act.get('exposed'),still_publishing_not_exposed=act.get('not_exposed'),FEE='yes' if C==2014 else 'no (placebo)'))
T=pd.DataFrame(res); pd.set_option('display.width',260); print(T.round(3).to_string(index=False)); T.to_csv('output/paper_pt/exposure_final.csv',index=False)
plc=[boots[C] for C in (2008,2009,2010,2011)]; plm=np.mean([T[T.cutoff==C].gap_pp.iloc[0] for C in (2008,2009,2010,2011)])
diff=100*(boots[2014]-np.mean(plc,axis=0)); dg=T[T.cutoff==2014].gap_pp.iloc[0]-plm
print('\nDifference-in-gaps (real gap 2015-17 minus mean placebo gap): %.1f pp  (95%% producer-bootstrap CI %.1f to %.1f)'%(dg,*np.percentile(diff,[2.5,97.5])))
# where is the exposed group concentrated: authors (single_use) vs exhausted blocks
K,post=build(2014); print('\nCutoff 2014 exposed composition:',K[K.grp=='exposed'].kind.value_counts().to_dict(),'| books by kind (2015-17):',post[post.grp=='exposed'].groupby('kind').size().to_dict())
for kd in ['single_use','block']:
    d=post[(post.grp=='exposed')&(post.kind==kd)]; print(' exposed',kd,'no-ISBN share %.3f (n=%d books)'%(d.noisbn.mean(),len(d)))
