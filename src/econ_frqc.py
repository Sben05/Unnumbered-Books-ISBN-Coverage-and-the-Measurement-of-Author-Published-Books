"""France vs Québec. Unit of analysis: year-level gap in log-odds, d_t = logit(p_FR) - logit(p_QC), with binomial variance.
With only two units, clustered/DiD asymptotics are unreliable, so inference is OLS on the gap series with Newey-West and exact permutation checks."""
import sys,warnings,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd,statsmodels.api as sm
OUT=ROOT/'output/selfpub';P=pd.read_csv(OUT/'panel.csv')
def gap(outcome):
    f=P[(P.source=='fr')&P.pub_year.between(2010,2021)].set_index('pub_year');q=P[(P.source=='qc')&P.pub_year.between(2010,2021)].set_index('pub_year')
    lf=np.log(f[outcome]/(f.n-f[outcome]));lq=np.log(q[outcome]/(q.n-q[outcome]))
    v=1/f[outcome]+1/(f.n-f[outcome])+1/q[outcome]+1/(q.n-q[outcome])
    return pd.DataFrame({'gap':lf-lq,'var':v,'lf':lf,'lq':lq,'pf':f[outcome]/f.n,'pq':q[outcome]/q.n})
def ols(y,X,lag=2):
    m=sm.OLS(y,sm.add_constant(X)).fit();return m,m.get_robustcov_results('HAC',maxlags=lag)
res=[];series=[]
for outcome,label in [('ap','author=publisher only'),('sp','combined (main)'),('svc_only','services only')]:
    g=gap(outcome);g['outcome']=outcome;series.append(g.reset_index())
    pre=g.loc[2010:2018];t=np.arange(len(pre))
    m,r=ols(pre.gap.values,t)
    pre_slope=m.params[1];pre_p_hac=r.pvalues[1];pre_se=r.bse[1]
    # permutation (exact): shuffle order of the pre-period gaps; stat = |OLS slope|
    perm=[abs(np.polyfit(t,np.array(p),1)[0]) for p in itertools.permutations(pre.gap.values)] if False else None
    rng=np.random.default_rng(1);vals=pre.gap.values;sl=abs(np.polyfit(t,vals,1)[0]);pp=np.mean([abs(np.polyfit(t,rng.permutation(vals),1)[0])>=sl for _ in range(20000)])
    # annual co-movement pre-period
    r_co=np.corrcoef(np.diff(pre.lf),np.diff(pre.lq))[0,1]
    resid_sd_pre=np.std(m.resid,ddof=2)
    # break: linear gap trend 2010-2021 with level shift + slope change at 2019
    full=g.copy();tt=np.arange(2010,2022)-2018;post=(np.arange(2010,2022)>=2019).astype(float)
    X=np.column_stack([tt,post,post*(np.arange(2010,2022)-2019)]);mf,rf=ols(full.gap.values,X)
    # level-only post effect after removing pre-trend extrapolation: gap_t - (a+b t) for post years
    pred=m.params[0]+m.params[1]*(np.arange(2019,2022)-2010);dev=g.loc[2019:2021].gap.values-pred
    z=dev/resid_sd_pre  # compared with pre residual sd
    res.append(dict(outcome=outcome,label=label,gap_2010=g.gap[2010],gap_2018=g.gap[2018],pre_slope_gap_per_year=pre_slope,pre_slope_se_NW=pre_se,pre_slope_p_NW=pre_p_hac,pre_slope_p_perm=pp,
        pre_resid_sd=resid_sd_pre,comovement_r_pre=r_co,
        post_dev_2019=dev[0],post_dev_2020=dev[1],post_dev_2021=dev[2],post_dev_mean=dev.mean(),post_dev_in_pre_sd=dev.mean()/resid_sd_pre,
        level_shift_2019=mf.params[2],level_shift_p_NW=rf.pvalues[2],slope_change=mf.params[3],slope_change_p_NW=rf.pvalues[3]))
pd.concat(series).to_csv(OUT/'frqc_gap_series.csv',index=False)
R=pd.DataFrame(res);R.to_csv(OUT/'frqc_parallel_trends_did.csv',index=False)
pd.set_option('display.width',250,'display.max_columns',50);print(R.round(4).T.to_string())
print(pd.concat(series).pivot(index='pub_year',columns='outcome',values='gap').round(3))
