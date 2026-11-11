"""H-A: composition of AP books before vs after fee dates (ES 2012, PT 2015, FR 2019)."""
import pandas as pd, numpy as np, os, warnings; warnings.filterwarnings('ignore')
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint as wil
from scipy.stats import chi2_contingency
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); OUT='output/night_h'
D=pd.concat([pd.read_parquet(f'{OUT}/feat_{c}.parquet') for c in ['es','pt','nz','qc','fr']],ignore_index=True)
D['short']=np.where(D.pages.notna(),(D.pages<80).astype(float),np.nan); D['lpages']=np.log(D.pages.where(D.pages.between(1,3000)))
D['nonfic']=np.where(D.has_genre&D.country.isin(['es','pt']),(~D.lit&~D.biog).astype(float),np.nan)
for f in ['illus','first_ed','nonmaj_lang','lit','poetry','biog']: D[f]=D[f].astype(float)
for f in ['lit','poetry','biog']: D.loc[~D.country.isin(['es','pt']),f]=np.nan
D.loc[D.country.isin(['es','pt'])&~D.has_genre,['lit','poetry','biog']]=np.nan
EV={'es':2012,'pt':2015,'fr':2019}
BIN=['short','illus','first_ed','nonmaj_lang','lit','poetry','biog','nonfic']
res=[]
for k,t in EV.items():
    d=D[(D.country.isin([k,'nz','qc']+(['fr'] if k!='fr' else [])))&D.pub_year.between(t-3,t+2)].copy()
    if k!='fr': d=d[~((d.country=='fr')&(d.pub_year>=2019))]
    d['post']=(d.pub_year>=t).astype(int); d['tr']=(d.country==k).astype(int); d['ap']=d.ap.astype(int)
    ctrl=d[(d.country!=k)&(d.ap==1)]; own=d[d.country==k]
    for f in BIN+['lpages']:
        a=own[own.ap==1].dropna(subset=[f]); 
        if len(a)<30 or a[f].nunique()<2: continue
        r=dict(event=k,year=t,feature=f,n_pre=int((a.post==0).sum()),n_post=int((a.post==1).sum()))
        if f=='lpages':
            r['pre']=a[a.post==0][f].mean(); r['post']=a[a.post==1][f].mean()
            m=smf.ols('lpages~post',a).fit(cov_type='HC1'); r['within_b']=m.params['post']; r['within_lo'],r['within_hi']=m.conf_int().loc['post']
        else:
            for w in (0,1):
                s=a[a.post==w][f]; x=s.sum();N=len(s); lo,hi=wil(x,N,method='wilson'); r[['pre','post'][w]]=x/N; r[['pre','post'][w]+'_ci']=f'[{lo:.3f},{hi:.3f}]'
            tab=pd.crosstab(a.post,a[f]); r['chi2_p']=chi2_contingency(tab)[1]
            m=smf.logit(f'{f}~post',a).fit(disp=0,cov_type='HC1'); r['within_b']=m.params['post']; r['within_lo'],r['within_hi']=m.conf_int().loc['post']
        # DiD vs control-country AP
        c=pd.concat([own[own.ap==1],ctrl]).dropna(subset=[f])
        if (c.tr==0).sum()>30 and c[c.tr==0][f].nunique()>1:
            fm=f'{f}~post+post:tr+C(country)'
            try:
                m=(smf.ols(fm,c) if f=='lpages' else smf.logit(fm,c)).fit(disp=0,cov_type='HC1') if f!='lpages' else smf.ols(fm,c).fit(cov_type='HC1')
                r['did_b']=m.params['post:tr']; r['did_lo'],r['did_hi']=m.conf_int().loc['post:tr']
            except Exception as e: pass
        # within-country AP vs non-AP triple-type: post*ap
        w=own.dropna(subset=[f])
        if w.groupby('ap')[f].nunique().min()>1 and w.ap.sum()>30:
            try:
                m=(smf.ols(f'{f}~post*ap',w) if f=='lpages' else smf.logit(f'{f}~post*ap',w)).fit(disp=0,cov_type='HC1')
                r['vs_nonap_b']=m.params['post:ap']; r['vs_nonap_lo'],r['vs_nonap_hi']=m.conf_int().loc['post:ap']
            except Exception: pass
        res.append(r)
R=pd.DataFrame(res); R.to_csv(f'{OUT}/ha_results.csv',index=False)
pd.set_option('display.width',250); print(R[['event','feature','n_pre','n_post','pre','post','chi2_p','within_b','did_b','did_lo','did_hi','vs_nonap_b','vs_nonap_lo','vs_nonap_hi']].round(3).to_string(index=False))
# trend of AP page counts etc by year for context
Y=D[D.ap].groupby(['country','pub_year']).agg(n=('isbn13','size'),med_pages=('pages','median'),short=('short','mean'),illus=('illus','mean'),first_ed=('first_ed','mean'),poetry=('poetry','mean'),lit=('lit','mean')).reset_index(); Y.to_csv(f'{OUT}/ha_ap_by_year.csv',index=False)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,3,figsize=(15,5),sharex=False)
for ax,k in zip(axs,EV):
    r=R[(R.event==k)&R.within_b.notna()&(R.feature!='lpages')].reset_index(drop=True)
    ys=np.arange(len(r))
    ax.errorbar(r.within_b,ys+.15,xerr=[r.within_b-r.within_lo,r.within_hi-r.within_b],fmt='o',label='within-country AP post vs pre',c='C0',capsize=2)
    dd=r.dropna(subset=['did_b'])
    ax.errorbar(dd.did_b,dd.index.values-.15,xerr=[dd.did_b-dd.did_lo,dd.did_hi-dd.did_b],fmt='s',label='DiD vs control AP',c='C3',capsize=2)
    ax.axvline(0,c='k',lw=.7); ax.set_yticks(ys); ax.set_yticklabels(r.feature); ax.set_title(f'{k.upper()} {EV[k]}: log-odds change in AP feature'); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(f'{OUT}/ha_forest.png',dpi=140)
