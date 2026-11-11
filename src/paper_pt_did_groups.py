"""DiD with publisher-size control groups. Treated: self-published (AP) books. Controls: non-AP books grouped by the publisher's size in 2005-2012 (pre-determined): large (>=100 books), medium (20-99), small (5-19), tiny (1-4).
Outcome: book has NO ISBN (LPM). Event study vs 2014 with joint pre-trend Wald test (2008-2013), DiD 2015-18 vs 2008-14, and the same with group-specific linear trends (trend estimated on 2008-14).
Clustered by publisher. Also a reweighted (synthetic-DiD-style) control built from the size groups + large publishers' ISBN-bearing book counts indexed to 2013."""
import re, unicodedata, numpy as np, pandas as pd, statsmodels.formula.api as smf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import minimize
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2005,2019)].copy()
def norm(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s)).strip()
R['pk']=R.publisher.map(norm); R['y']=R.pub_year.astype(int); R['noisbn']=(~R.has_isbn).astype(int)
cnt=R[(R.y<=2012)&(~R.ap)&(R.pk!='')].groupby('pk').size()
def grp(r):
    if r.ap: return 'AP'
    n=cnt.get(r.pk,0)
    return 'large' if n>=100 else 'medium' if n>=20 else 'small' if n>=5 else 'tiny' if n>=1 else 'new'
R['g']=[grp(r) for r in R.itertuples()]
S=R.groupby(['g','y']).noisbn.agg(['mean','size']).unstack(0); print('no-ISBN share by group (%):'); print((100*S['mean']).loc[2008:2018].round(1).to_string()); print('books:'); print(S['size'].loc[[2010,2014,2016]].to_string())
rows=[]
def did(ctrl,trend=False):
    D=R[(R.g.isin(['AP']+ctrl))&R.y.between(2008,2018)].copy(); D['trt']=(D.g=='AP').astype(int); D['post']=(D.y>=2015).astype(int); D['t']=D.y-2014
    f='noisbn ~ trt + trt:post + C(y)'+(' + trt:t' if trend else ''); m=smf.ols(f,data=D).fit(cov_type='cluster',cov_kwds={'groups':D.pk.astype('category').cat.codes})
    # pre-trend test: event-study dummies 2008-2013 vs 2014
    D2=D.copy(); 
    for yv in range(2008,2019):
        if yv!=2014: D2[f'e{yv}']=((D2.trt==1)&(D2.y==yv)).astype(int)
    pre=[f'e{y}' for y in range(2008,2014)]; m2=smf.ols('noisbn ~ trt + '+' + '.join(f'e{y}' for y in range(2008,2019) if y!=2014)+' + C(y)',data=D2).fit(cov_type='cluster',cov_kwds={'groups':D2.pk.astype('category').cat.codes})
    w=m2.wald_test(' , '.join(f'{c} = 0' for c in pre),scalar=True); return m,m2,float(w.pvalue)
for name,ctrl in [('large publishers',['large']),('large + medium',['large','medium']),('medium',['medium']),('small + tiny',['small','tiny']),('all non-AP with history',['large','medium','small','tiny'])]:
    m,m2,pw=did(ctrl); mt,_,_=did(ctrl,True)
    rows.append(dict(control=name,did_pp=100*m.params['trt:post'],se_pp=100*m.bse['trt:post'],pretrend_joint_p=pw,did_with_group_trend_pp=100*mt.params['trt:post'],se_trend_pp=100*mt.bse['trt:post']))
T=pd.DataFrame(rows); T.to_csv('output/paper_pt/did_groups.csv',index=False); print('\nDiD (AP vs control group), post 2015-18, percentage points, clustered by publisher:'); print(T.round(3).to_string(index=False))
# event study vs large publishers
m,m2,pw=did(['large']); ev=pd.DataFrame({'y':[y for y in range(2008,2019) if y!=2014],'b':[100*m2.params[f'e{y}'] for y in range(2008,2019) if y!=2014],'se':[100*m2.bse[f'e{y}'] for y in range(2008,2019) if y!=2014]})
ev.loc[len(ev)]=[2014,0,0]; ev=ev.sort_values('y'); print('\nEvent study AP vs large publishers (pp, ref 2014):'); print(ev.round(1).to_string(index=False)); ev.to_csv('output/paper_pt/did_event_large.csv',index=False)
fig,ax=plt.subplots(1,2,figsize=(12,3.9))
for g,c in [('AP','#c0392b'),('large','#2c7fb8'),('medium','#27ae60'),('small','#8e44ad'),('tiny','#e67e22')]: ax[0].plot(S['mean'].loc[2008:2018].index,100*S['mean'].loc[2008:2018][g],'o-',c=c,label=g,lw=2.4 if g=='AP' else 1.2)
ax[0].axvline(2014.5,c='k',ls=':'); ax[0].set_ylabel('% of books with no ISBN'); ax[0].legend(fontsize=8); ax[0].set_title('No-ISBN share by group')
ax[1].errorbar(ev.y,ev.b,yerr=1.96*ev.se,fmt='o-',c='#c0392b',capsize=3); ax[1].axhline(0,c='#999'); ax[1].axvline(2014.5,c='k',ls=':'); ax[1].set_title('Event study: AP minus large publishers (pp, 95% CI)')
plt.tight_layout(); plt.savefig('output/paper_pt/fig_did_groups.png',dpi=150)
