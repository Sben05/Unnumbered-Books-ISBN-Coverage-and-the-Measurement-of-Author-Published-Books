"""Entrant vs incumbent self-publishers: AP books whose author has NO earlier book in the national bibliography (since 2005) = first-time.
First-time applicants must register (and, from 2015, pay); incumbents may hold earlier ISBNs/prefixes. No-ISBN share by status x year."""
import pandas as pd, numpy as np, json, re, unicodedata
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2005,2021)]
raw=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','a700']); raw['id']=raw.id.astype(str); R=R.merge(raw,on='id',how='left')
def key(a):
    try: l=json.loads(a)
    except Exception: return ''
    if not l: return ''
    s=unicodedata.normalize('NFKD',l[0].get('a','')+' '+l[0].get('b','')).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]','',s)).strip()
R['au']=R.a700.map(key); R=R[R.au!='']
first=R.groupby('au').pub_year.min(); R['first_time']=R.pub_year==R.au.map(first)
R['noisbn']=(~R.has_isbn).astype(int)
A=R[R.ap&R.pub_year.between(2009,2021)]   # 2005-08 used as burn-in for "first-time"
t=A.groupby(['pub_year','first_time']).agg(books=('id','size'),noisbn=('noisbn','mean')).unstack()
print(t.round(3).to_string())
A=A.assign(post=A.pub_year>=2015)
s=A.groupby(['first_time','post']).agg(books=('id','size'),noisbn=('noisbn','mean')); print(s.round(3))
did=(s.loc[(True,True),'noisbn']-s.loc[(True,False),'noisbn'])-(s.loc[(False,True),'noisbn']-s.loc[(False,False),'noisbn'])
rng=np.random.default_rng(5); bs=[]
g=A.groupby(['first_time','post'])
groups={k:v.noisbn.values for k,v in g}
for _ in range(5000):
    m={k:rng.choice(v,len(v)).mean() for k,v in groups.items()}
    bs.append((m[(True,True)]-m[(True,False)])-(m[(False,True)]-m[(False,False)]))
print('DiD first-time minus incumbent (post-pre) = %.3f, 95%% book-bootstrap CI [%.3f, %.3f]'%(did,*np.percentile(bs,[2.5,97.5])))
# same for NON-AP books (placebo group)
N=R[(~R.ap)&R.pub_year.between(2009,2021)].assign(post=lambda x:x.pub_year>=2015)
sn=N.groupby(['first_time','post']).noisbn.mean(); print('non-AP books: first-time pre %.3f post %.3f | incumbent pre %.3f post %.3f'%(sn[(True,False)],sn[(True,True)],sn[(False,False)],sn[(False,True)]))
t.to_csv('output/paper_pt/entrants_by_year.csv')
