"""Pooled country-year binomial DiD around the Amazon/POD shock (2007): free-ISBN NZ vs paid-ISBN UK and US (LoC). Year-clustered SEs + year-block bootstrap."""
import sys,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd,statsmodels.api as sm,statsmodels.formula.api as smf
OUT=ROOT/'output/selfpub';P=pd.read_csv(OUT/'panel.csv')
rng=np.random.default_rng(3)
def fit(d,outcome,brk,trend):
    d=d.copy();d['nz']=(d.source=='nz').astype(int);d['post']=(d.pub_year>=brk).astype(int);d['p']=d[outcome]/d.n;d['yr']=d.pub_year.astype(str);d['t']=d.pub_year-brk
    f='p~C(yr)+nz+nz:post'+('+nz:t' if trend else '')
    return smf.glm(f,d,family=sm.families.Binomial(),freq_weights=d.n).fit(scale='X2',cov_type='cluster',cov_kwds={'groups':d.pub_year})
out=[]
for comp,ctrl,lo,hi in [('NZ vs UK','uk',1995,2014),('NZ vs US(LoC)','us',1995,2011),('NZ vs UK+US(LoC)',['uk','us'],1995,2011)]:
    for outcome in ['ap','sp']:
        for brk in [2007,2008]:
            for trend in [False,True]:
                srcs=['nz']+([ctrl] if isinstance(ctrl,str) else ctrl);d=P[P.source.isin(srcs)&P.pub_year.between(lo,hi)]
                m=fit(d,outcome,brk,trend);c=m.params['nz:post'];se=m.bse['nz:post']
                # year-block bootstrap
                yrs=d.pub_year.unique();bs=[]
                for _ in range(300):
                    ys=rng.choice(yrs,len(yrs),replace=True);db=pd.concat([d[d.pub_year==y].assign(pub_year=i+10000*0+i) for i,y in enumerate(ys)])
                    # re-index years to preserve time order for FE: use sampled year as label for FE, and original for post indicator
                    db=pd.concat([d[d.pub_year==y].assign(yb=k) for k,y in enumerate(ys)]);db['post']=(db.pub_year>=brk).astype(int);db['nz']=(db.source=='nz').astype(int);db['p']=db[outcome]/db.n
                    try:mb=smf.glm('p~C(yb)+nz+nz:post',db,family=sm.families.Binomial(),freq_weights=db.n).fit();bs.append(mb.params['nz:post'])
                    except Exception:pass
                lo_,hi_=np.percentile(bs,[2.5,97.5]) if not trend else (np.nan,np.nan)
                out.append(dict(comparison=comp,window=f'{lo}-{hi}',outcome=outcome,break_year=brk,country_trends=trend,log_odds_ratio=c,odds_ratio=np.exp(c),se_cluster_year=se,p_cluster=m.pvalues['nz:post'],boot_ci_low_or=np.exp(lo_),boot_ci_high_or=np.exp(hi_)))
R=pd.DataFrame(out);R.to_csv(OUT/'did_amazon_era.csv',index=False)
pd.set_option('display.width',250);print(R.round(3).to_string(index=False))
