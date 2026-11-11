"""Robustness against rival explanations for the 2015 change in Portugal. Each block tests one alternative.
B substitution to author-service imprints; C substitution to foreign (US etc.) ISBNs; D forecasts that ignore the 2014 spike; E placebo outcomes that should NOT move;
F catalogue coverage/recording checks. Level-shift stat: mean deviation 2015-18 from OLS trend fitted 2005-14 (logit for shares, log for counts/pages); rank among placebo breaks 2010-13 with >=5 pre-years."""
import numpy as np, pandas as pd, duckdb
lg=lambda p:np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4)))
c=duckdb.connect()
def stat(y,B=2015,lo=2005,H=4):
    yy=y.loc[lo:B-1].dropna(); b=np.polyfit(yy.index,yy.values,1); post=[t for t in range(B,B+H) if t in y.index]; return float(np.mean([y.loc[t]-np.polyval(b,t) for t in post]))
def rank(y):
    s=stat(y); pl=[stat(y,B=b) for b in range(2010,2014)]; return s,1+sum(abs(v)>=abs(s) for v in pl),len(pl)+1
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2005,2019)].copy(); R['y']=R.pub_year.astype(int)
raw=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','edition']); raw['id']=raw.id.astype(str); R=R.merge(raw,on='id',how='left')
R['pages']=pd.to_numeric(R.extent.astype(str).str.extract(r'(\d{1,4})')[0],errors='coerce'); R['first_ed']=~R.edition.fillna('').str.contains(r'[2-9]\s*[ªa.]|segunda|terceira|2\.?\s*ed',case=False,regex=True)
out=[]
# main for reference
share=lambda m,f:R[m].groupby(R.y[m]).apply(lambda d:f(d))
ap=R[R.ap]; main=ap.groupby('y').has_isbn.apply(lambda x:(~x).mean()); mainA=lg(R.groupby('y').apply(lambda d:(d.ap&d.has_isbn).sum()/d.has_isbn.sum()))
for name,y in [('MAIN B: AP books without ISBN, share',lg(main)),('MAIN A: AP share of ISBN-bearing books',mainA)]: s,r,n=rank(y); out.append((name,s,r,n))
# B substitution to services
sv=c.execute("select pub_year y, count(*) n, sum(ap_consistent::int) ap, sum(service_imprint::int) sv, sum((ap_consistent or service_imprint)::int) both_ from 'data/interim/pt_classified.parquet' where pub_year between 2005 and 2019 group by 1 order by 1").df().set_index('y')
print('B. ISBN-bearing books: AP, service imprints, combined (counts) and shares'); T=sv.assign(ap_sh=sv.ap/sv.n*100,sv_sh=sv.sv/sv.n*100,both_sh=sv.both_/sv.n*100).loc[2010:2018].round(2); print(T.to_string())
for name,y in [('B: service-imprint share of ISBN books',lg(sv.sv/sv.n)),('B: AP-or-service share of ISBN books',lg(sv.both_/sv.n))]: s,r,n=rank(y); out.append((name,s,r,n))
# C foreign ISBN substitution
fa=R.groupby('y').apply(lambda d:pd.Series({'ap_foreign_prefix':(d.ap&d.foreign_prefix).sum(),'ap_pt_prefix':(d.ap&d.pt_prefix).sum(),'ap_any_isbn':(d.ap&d.has_isbn).sum(),'ap_all':d.ap.sum()}))
print('\nC. self-published books by ISBN type'); print(fa.loc[2012:2018].to_string())
for name,y in [('C: AP with Portuguese-prefix ISBN, log count',np.log(fa.ap_pt_prefix)),('C: AP with ANY ISBN (PT or foreign), log count',np.log(fa.ap_any_isbn)),('C: AP total incl. no ISBN, log count',np.log(fa.ap_all))]: s,r,n=rank(y); out.append((name,s,r,n))
# D forecasts ignoring 2014 (fit on <=2013, predict 2015-18)
y=mainA; tr=y.loc[2005:2013]; fcst={}
for k in (5,7,9):
    yy=tr.loc[2013-k+1:2013]; b=np.polyfit(yy.index,yy.values,1); fcst[f'trend_last{k}_excl2014']=np.mean([y.loc[t]-np.polyval(b,t) for t in range(2015,2019)])
fcst['mean_2011_13_excl2014']=np.mean([y.loc[t]-y.loc[2011:2013].mean() for t in range(2015,2019)])
print('\nD. gap of actual 2015-18 vs forecasts fitted WITHOUT 2014 (logit, outcome A):',{k:round(v,2) for k,v in fcst.items()})
# E placebo outcomes
nonap=R[~R.ap].groupby('y').has_isbn.apply(lambda x:(~x).mean()); gov=R[R.gov].groupby('y').has_isbn.apply(lambda x:(~x).mean())
apfe=ap.groupby('y').first_ed.mean(); appg=np.log(ap.groupby('y').pages.median()); apdl=ap.groupby('y').has_dl.mean(); apnopub=ap.groupby('y').nopub.mean()
allpg=np.log(R.groupby('y').pages.median())
print('\nE/F placebo and recording outcomes (self-published books unless stated):')
for name,y in [('E: OTHER books without ISBN, share (logit)',lg(nonap)),('E: government books without ISBN, share (logit)',lg(gov)),('E: AP first-edition share (logit)',lg(apfe)),('E: AP median pages (log)',appg),
               ('E: all books median pages (log)',allpg),('F: AP books with a legal-deposit number, share (logit)',lg(apdl.clip(0.001,0.999))),('F: AP books with unidentified publisher (s.n.), share (logit)',lg(apnopub.clip(0.001,0.999)))]:
    s,r,n=rank(y); out.append((name,s,r,n))
O=pd.DataFrame(out,columns=['outcome','mean deviation 2015-18 from 2005-14 trend','rank of 2015 among placebo breaks','of']); O['moves_distinctively']=O['rank of 2015 among placebo breaks']==1
pd.set_option('display.width',250); print('\n',O.round(3).to_string(index=False)); O.to_csv('output/paper_pt/alternatives_battery.csv',index=False); T.to_csv('output/paper_pt/alt_services.csv')
