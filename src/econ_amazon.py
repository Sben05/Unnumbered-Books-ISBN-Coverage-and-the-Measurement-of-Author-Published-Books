"""Amazon-era comparisons: unknown-breakpoint tests, NZ-vs-UK interrupted time series, per-capita rates, national-bibliography capture of Amazon-issued ISBNs."""
import sys,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd,statsmodels.api as sm
OUT=ROOT/'output/selfpub';P=pd.read_csv(OUT/'panel.csv')
rng=np.random.default_rng(7)
def series(src,col,lo,hi):
    d=P[(P.source==src)&P.pub_year.between(lo,hi)].set_index('pub_year');p=d[col]/d.n;return d.index.values,np.log(p/(1-p)).values,d
def supF(y,t,trim=.15,tau_range=None):
    n=len(y);X0=sm.add_constant(t);r0=sm.OLS(y,X0).fit();best=(-1,None)
    for i in range(int(n*trim),int(n*(1-trim))):
        post=(np.arange(n)>=i).astype(float);X=np.column_stack([X0,post,post*(np.arange(n)-i)])
        r=sm.OLS(y,X).fit();F=((r0.ssr-r.ssr)/2)/(r.ssr/(n-4))
        if F>best[0]:best=(F,i)
    return best,r0
def boot_p(y,t,F,B=1000):
    X0=sm.add_constant(t);r0=sm.OLS(y,X0).fit();e=r0.resid;f=r0.fittedvalues;cnt=0
    for _ in range(B):
        yb=f+rng.choice(e,len(e),replace=True)
        if supF(yb,t)[0][0]>=F:cnt+=1
    return (cnt+1)/(B+1)
rows=[]
for src,lo,hi,label in [('nz',1995,2019,'NZ'),('uk',1995,2014,'UK'),('us',1995,2011,'US (LoC)'),('fr',2005,2018,'France'),('qc',2010,2018,'Québec')]:
    for col in ['ap','sp']:
        t,y,d=series(src,col,lo,hi);(F,i),r0=supF(y,np.arange(len(y)));
        rows.append(dict(country=label,outcome=col,window=f'{lo}-{hi}',break_year=int(t[i]),supF=F,boot_p=boot_p(y,np.arange(len(y)),F)))
B=pd.DataFrame(rows);B.to_csv(OUT/'break_tests.csv',index=False);print(B.round(3).to_string(index=False))
# Interrupted time series on NZ-UK gap
res=[]
for col in ['ap','sp']:
    tn,yn,_=series('nz',col,1995,2014);tu,yu,_=series('uk',col,1995,2014);g=yn-yu;t=tn-2008
    for brk in [2007,2008,2009]:
        post=(tn>=brk).astype(float);X=sm.add_constant(np.column_stack([tn-brk,post,post*(tn-brk)]));m=sm.OLS(g,X).fit(cov_type='HAC',cov_kwds={'maxlags':3})
        # permutation of break year over 2000..2010 (placebo distribution of slope-change t-stat)
        stats=[]
        for b2 in range(2000,2011):
            p2=(tn>=b2).astype(float);X2=sm.add_constant(np.column_stack([tn-b2,p2,p2*(tn-b2)]));m2=sm.OLS(g,X2).fit();stats.append(m2.tvalues[3])
        res.append(dict(outcome=col,break_year=brk,pre_gap_slope=m.params[1],level_shift=m.params[2],slope_change=m.params[3],slope_change_se_NW=m.bse[3],slope_change_p_NW=m.pvalues[3],rank_among_placebos=int((np.array(stats)>=m.tvalues[3]).sum())+0))
R=pd.DataFrame(res);R.to_csv(OUT/'nz_uk_its.csv',index=False);print(R.round(4).to_string(index=False))
# per-capita
pop=pd.read_csv(ROOT/'config/population_millions.csv')
def popy(s):
    d=pop[pop.source==s].set_index('year').millions;return d.reindex(range(1995,2023)).interpolate(limit_direction='both')
pc=[]
for s in ['uk','nz','fr','qc','us']:
    d=P[P.source==s].set_index('pub_year');p=popy(s);d=d.assign(pop=p.reindex(d.index).values);d['ap_per_m']=d.ap/d['pop'];d['sp_per_m']=d.sp/d['pop'];d['isbn_per_m']=d.n/d['pop'];pc.append(d.reset_index()[['source','pub_year','n','ap','sp','pop','ap_per_m','sp_per_m','isbn_per_m']])
PC=pd.concat(pc);PC.to_csv(OUT/'per_capita.csv',index=False)
print(PC[PC.pub_year.isin([2000,2005,2010,2013,2018])].pivot(index='pub_year',columns='source',values='ap_per_m').round(1))
# capture of Amazon-issued ISBNs
amz=P[P.source=='amz'].set_index('pub_year')
cap=pd.DataFrame({'amazon_sample_createspace_or_indep':amz.amazon_imprint})
for s in ['uk','us','nz','fr','qc']:cap['nb_'+s]=P[P.source==s].set_index('pub_year').amazon_imprint
cap=cap.loc[2008:2018];cap.to_csv(OUT/'amazon_issued_capture.csv');print(cap)
