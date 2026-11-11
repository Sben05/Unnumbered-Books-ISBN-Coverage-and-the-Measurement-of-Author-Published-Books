"""Synthetic control for Portugal 2015. Outcomes (logit): (A) AP share of ISBN-bearing books [many donors]; (B) gap = logit(AP no-ISBN share) - logit(other no-ISBN share) [donors with ISBN-less records].
Donors: FR (to 2018, before its fee), PL, NZ, EE (+DE, NO for A). Pre-period 2005-2014 (EE/PL/NZ/FR; DE/NO from isbn files). Weights >=0 sum to 1 (standard) and demeaned/'level-free' version
(subtract each unit's pre-mean; equivalent to SC with intercept). Holdout: fit 2005-2011, predict 2012-14. Placebo in space: each donor as treated. Inference resolution = 1/(donors+1)."""
import numpy as np, pandas as pd, duckdb, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import minimize
P=pd.read_csv('output/paper_pt/ddd_panel_2003.csv'); lg=lambda p:np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4)))
def piv(f): return P.assign(v=f(P)).pivot(index='y',columns='country',values='v')
A=piv(lambda d:lg(d.ap_isbn/(d.ap_isbn+d.nonap_isbn)))
c=duckdb.connect()
de=pd.read_csv('output/germany/de_by_year.csv').set_index('year'); A['DE']=lg(de.ap_consistent/de.isbns)
no=c.execute("select pub_year y, avg(author_is_publisher::int) p from 'data/interim/no_classified.parquet' group by 1").df().set_index('y'); A['NO']=lg(no.p)
B=piv(lambda d:lg(d.ap_noisbn/(d.ap_isbn+d.ap_noisbn))-lg(d.nonap_noisbn/(d.nonap_isbn+d.nonap_noisbn)))
def sc(Y,treated,donors,pre,post,demean=True,restrict=None):
    pre=[y for y in pre if y in Y.index]; X=Y.loc[pre,donors].dropna(axis=1); donors=list(X.columns); y=Y.loc[pre,treated]
    mu_y=y.mean() if demean else 0; mu=X.mean() if demean else 0
    Xd=X-mu; yd=y-mu_y; f=lambda w:((yd-Xd@w)**2).sum(); n=len(donors)
    r=minimize(f,np.ones(n)/n,bounds=[(0,1)]*n,constraints={'type':'eq','fun':lambda w:w.sum()-1},method='SLSQP'); w=pd.Series(r.x,index=donors)
    full=Y.loc[:,donors]; syn=(full-mu)@w+mu_y if demean else full@w
    return w,syn,np.sqrt(f(r.x)/len(pre))
def run(Y,donors,label,fee=2015,end=2018):
    pre=range(2005,fee); post=range(fee,end+1); out={}
    w,syn,rm=sc(Y,'PT',donors,pre,post); gap=(Y['PT']-syn); eff=gap.loc[list(post)].mean()
    # holdout
    w2,syn2,_=sc(Y,'PT',donors,range(2005,2012),range(2012,2015)); hold=(Y['PT']-syn2).loc[2012:2014]
    pl=[]
    for d in w.index:
        oth=[k for k in w.index if k!=d]
        if len(oth)<2: continue
        w3,s3,rm3=sc(Y,d,oth,pre,post); g3=Y[d]-s3; pl.append((d,g3.loc[list(post)].mean(),rm3))
    print(f'== {label}: donors {list(w.index)}'); print('weights',w.round(2).to_dict())
    print('pre-RMSE %.3f | effect (mean gap %d-%d) %.3f | holdout (fit 2005-11) mean gap 2012-14 %.3f'%(rm,fee,end,eff,hold.mean()))
    print('placebo-donor effects:',{d:round(e,2) for d,e,_ in pl},'| rank of |PT| among',len(pl)+1,':',1+sum(abs(e)>=abs(eff) for _,e,_ in pl))
    print('post/pre RMSPE ratio PT %.2f ; donors'%(np.sqrt((gap.loc[list(post)]**2).mean())/rm),{d:round(np.sqrt(((Y[d]-sc(Y,d,[k for k in w.index if k!=d],pre,post)[1]).loc[list(post)]**2).mean())/r,2) for d,_,r in pl})
    return w,syn,gap,eff
wA,sA,gA,eA=run(A,['FR','PL','NZ','EE','DE','NO'],'A: AP share of ISBN books')
wB,sB,gB,eB=run(B,['FR','PL','NZ','EE'],'B: AP vs other no-ISBN gap')
fig,ax=plt.subplots(1,2,figsize=(12,3.8))
for a,(Y,syn,t) in zip(ax,[(A,sA,'A: AP share of ISBN books (logit)'),(B,sB,'B: no-ISBN gap, AP vs other (logit)')]):
    a.plot(Y.loc[2005:2019].index,Y.loc[2005:2019,'PT'],'o-',c='#c0392b',label='Portugal'); a.plot(syn.loc[2005:2019].index,syn.loc[2005:2019],'s--',c='#555',label='synthetic Portugal')
    a.axvline(2014.5,c='k',ls=':'); a.set_title(t); a.legend(fontsize=8)
plt.tight_layout(); plt.savefig('output/paper_pt/fig_synthetic_control.png',dpi=150)
pd.DataFrame({'A_actual':A['PT'],'A_synth':sA,'B_actual':B['PT'],'B_synth':sB}).loc[2005:2019].to_csv('output/paper_pt/synthetic_control_paths.csv')
