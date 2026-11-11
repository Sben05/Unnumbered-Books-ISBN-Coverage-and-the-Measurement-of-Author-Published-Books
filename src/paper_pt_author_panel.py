"""Same-author panel: authors with print books in the BNP national bibliography both 2010-14 and 2015-19.
Self-publisher status defined ONLY from pre-2015 books (>=1 AP book 2010-14). Outcome: share of the author's books without ISBN.
Within-author change, self-publishers vs other authors; author-bootstrap CI. Descriptive."""
import pandas as pd, numpy as np, json, re, unicodedata
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2010,2019)]
raw=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','a700']); raw['id']=raw.id.astype(str); R=R.merge(raw,on='id',how='left')
def key(a):
    try: l=json.loads(a)
    except Exception: return ''
    if not l: return ''
    s=unicodedata.normalize('NFKD',l[0].get('a','')+' '+l[0].get('b','')).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]','',s)).strip()
R['au']=R.a700.map(key); R=R[R.au!='']; R['post']=R.pub_year>=2015; R['noisbn']=(~R.has_isbn).astype(float)
pre_ap=set(R[(~R.post)&R.ap].au)
a=R.groupby(['au','post']).noisbn.mean().unstack().dropna()
a['sp']=a.index.isin(pre_ap); a['d']=a[True]-a[False]
nb=R.groupby('au').size(); a['nbooks']=nb.reindex(a.index)
res={}
for lab,mask in [('self-publishers (AP before 2015)',a.sp),('other authors',~a.sp)]:
    s=a[mask]; res[lab]=dict(authors=len(s),pre_noisbn=s[False].mean(),post_noisbn=s[True].mean(),within_change=s.d.mean())
rng=np.random.default_rng(3); sp=a[a.sp].d.values; ot=a[~a.sp].d.values; bs=[]
for _ in range(5000): bs.append(rng.choice(sp,len(sp)).mean()-rng.choice(ot,len(ot)).mean())
did=sp.mean()-ot.mean(); lo,hi=np.percentile(bs,[2.5,97.5])
O=pd.DataFrame(res).T; print(O.round(3).to_string()); print('DiD (within-author change, SP minus others) = %.3f  95%% author-bootstrap CI [%.3f, %.3f]'%(did,lo,hi))
# placebo: same design with fake break 2012 (pre 2008-11 vs 2012-14 would need 2008+ data) -> use 2010-12 vs 2013-14
R2=R[R.pub_year<=2014].copy(); R2['post']=R2.pub_year>=2013; pre_ap2=set(R2[(~R2.post)&R2.ap].au)
b=R2.groupby(['au','post']).noisbn.mean().unstack().dropna(); b['sp']=b.index.isin(pre_ap2); b['d']=b[True]-b[False]
print('PLACEBO break 2013 (2010-12 vs 2013-14): SP within change %.3f (n=%d) vs others %.3f (n=%d) -> DiD %.3f'%(b[b.sp].d.mean(),b.sp.sum(),b[~b.sp].d.mean(),(~b.sp).sum(),b[b.sp].d.mean()-b[~b.sp].d.mean()))
pd.DataFrame(res).T.assign(did=did,ci_lo=lo,ci_hi=hi).to_csv('output/paper_pt/author_panel_summary.csv')
