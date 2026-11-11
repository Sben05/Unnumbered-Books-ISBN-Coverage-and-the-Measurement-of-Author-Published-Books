"""Counterfactual forecasting for Portugal (outcome A: logit AP share of ISBN books). Rolling-origin validation on PRE-fee data only (origins 2008-2011, horizon 3, test years up to 2014);
models: mean of last 5, random walk, OLS trend on last 5 / 7 / all years, ridge regression on donor series, synthetic control. Ensemble = inverse-MSE weights from validation.
Then forecast 2015-18 and compare. Placebo: same pipeline for each donor country (treated = donor, predictors = other donors). Selection of models/windows uses only pre-2015 data."""
import numpy as np, pandas as pd, duckdb
from scipy.optimize import minimize
P=pd.read_csv('output/paper_pt/ddd_panel_2003.csv'); lg=lambda p:np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4)))
A=P.assign(v=lg(P.ap_isbn/(P.ap_isbn+P.nonap_isbn))).pivot(index='y',columns='country',values='v')
c=duckdb.connect(); de=pd.read_csv('output/germany/de_by_year.csv').set_index('year'); A['DE']=lg(de.ap_consistent/de.isbns)
no=c.execute("select pub_year y, avg(author_is_publisher::int) p from 'data/interim/no_classified.parquet' group by 1").df().set_index('y'); A['NO']=lg(no.p)
A=A.loc[2003:2018,['PT','FR','PL','NZ','EE','DE','NO']]
D=['FR','PL','NZ','EE','DE','NO']
def trend(y,T,H,k):
    yy=y.loc[T-k+1:T] if k else y.loc[:T]; b=np.polyfit(yy.index,yy.values,1); return np.polyval(b,np.arange(T+1,T+H+1))
def ridge(Y,t,donors,T,H,lam=2.0):
    tr=Y.loc[:T]; X=tr[donors]; mu,sd=X.mean(),X.std()+1e-9; Z=(X-mu)/sd; yy=tr[t]; ym=yy.mean()
    beta=np.linalg.solve(Z.T@Z+lam*np.eye(len(donors)),Z.T@(yy-ym)); Zf=(Y.loc[T+1:T+H,donors]-mu)/sd; return ym+(Zf@beta).values
def sc(Y,t,donors,T,H):
    tr=Y.loc[:T]; X=tr[donors]; mu=X.mean(); yy=tr[t]; ym=yy.mean(); Xd=X-mu; n=len(donors)
    r=minimize(lambda w:((yy-ym-Xd@w)**2).sum(),np.ones(n)/n,bounds=[(0,1)]*n,constraints={'type':'eq','fun':lambda w:w.sum()-1},method='SLSQP')
    return ym+((Y.loc[T+1:T+H,donors]-mu)@r.x).values
def models(Y,t,donors,T,H):
    y=Y[t]; return {'mean_last5':np.repeat(y.loc[T-4:T].mean(),H),'random_walk':np.repeat(y.loc[T],H),'trend_last5':trend(y,T,H,5),'trend_last7':trend(y,T,H,7),'trend_all':trend(y,T,H,None),
                    'ridge_donors':ridge(Y,t,donors,T,H),'synthetic_control':sc(Y,t,donors,T,H)}
def validate(Y,t,donors,origins=(2008,2009,2010,2011),H=3):
    err={}
    for T in origins:
        f=models(Y,t,donors,T,H); act=Y.loc[T+1:T+H,t].values
        for m,v in f.items(): err.setdefault(m,[]).extend(list(act-v))
    return pd.Series({m:np.sqrt(np.mean(np.square(e))) for m,e in err.items()}),err
def pipeline(Y,t,donors,T=2014,H=4):
    rm,err=validate(Y,t,donors,origins=tuple(range(T-6,T-2)),H=3); w=(1/rm**2); w/=w.sum()
    f=models(Y,t,donors,T,H); ens=sum(w[m]*f[m] for m in f); act=Y.loc[T+1:T+H,t].values
    return rm,w,f,ens,act,err
rm,w,f,ens,act,err=pipeline(A,'PT',D)
print('Validation RMSE (logit) on pre-2015 rolling origins:'); print(rm.round(3).to_string()); print('ensemble weights:',w.round(2).to_dict())
print('\n2015-18 actual PT:',act.round(2),'\nensemble forecast:',ens.round(2))
G=pd.DataFrame({m:act-v for m,v in f.items()}); G['ENSEMBLE']=act-ens; G.index=range(2015,2019); print('\ngap (actual - forecast) by year:'); print(G.round(2).to_string()); print('\nmean gap by model:'); print(G.mean().round(3).to_string())
# crude predictive band from validation errors
sd=np.std(err['synthetic_control']); print('validation error SD (synthetic control): %.2f'%sd)
# placebo: donors
pl={}
for d in D:
    oth=[k for k in D if k!=d]+[]; 
    try:
        rmd,wd,fd,ensd,actd,_=pipeline(A.assign(**{}),d,oth,2014,4); pl[d]=np.mean(actd-ensd)
    except Exception as e: pl[d]=np.nan
print('\nplacebo (donor treated) ensemble mean gap:',{k:round(v,2) for k,v in pl.items()},'| PT %.2f | rank of |PT| among %d: %d'%(G.ENSEMBLE.mean(),len(pl)+1,1+sum(abs(v)>=abs(G.ENSEMBLE.mean()) for v in pl.values() if not np.isnan(v))))
# fake origins for PT (pipeline run as if fee started 2012 / 2013)
fk={}
for T in (2011,2012,2013):
    r2,w2,f2,e2,a2,_=pipeline(A,'PT',D,T=T,H=3); fk[T+1]=np.mean(a2-e2)
print('PT pipeline at fake fee years (mean gap next 3 yrs):',{k:round(v,2) for k,v in fk.items()})
G.to_csv('output/paper_pt/ml_counterfactual_gaps.csv'); rm.to_csv('output/paper_pt/ml_validation_rmse.csv')
