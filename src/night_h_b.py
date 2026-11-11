"""H-B: ISBN prefix (registrant) structure of AP books: singleton prefixes, own-block, shared pools, block size."""
import pandas as pd, numpy as np, os, warnings; warnings.filterwarnings('ignore')
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint as wil
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); OUT='output/night_h'
D=pd.concat([pd.read_parquet(f'{OUT}/feat_{c}.parquet',columns=['country','isbn13','pub_year','ap','prefix','reglen','publen','author1']) for c in ['es','pt','nz','qc','fr']],ignore_index=True)
D=D.dropna(subset=['prefix'])
D['key']=D.country+'|'+D.prefix
g=D.groupby('key')
D['n_books']=g.isbn13.transform('size'); D['n_auth']=g.author1.transform('nunique'); D['n_ap']=g.ap.transform('sum')
D['cls']=np.select([D.n_books==1,D.n_auth==1,D.n_auth>=10],['singleton','own_block','big_pool'],'small_shared')
D['singleton']=(D.cls=='singleton').astype(float); D['own']=(D.cls=='own_block').astype(float); D['bigpool']=(D.cls=='big_pool').astype(float); D['shared']=D.cls.isin(['small_shared','big_pool']).astype(float)
D['block10']=(D.publen<=1).astype(float); D['block100']=(D.publen<=2).astype(float)
# prefixes first seen: AP books that are the first use of a prefix
D['first_use']=(D.pub_year==D.groupby('key').pub_year.transform('min')).astype(float)
maxy=D.groupby('country').pub_year.max(); print(maxy.to_dict())
# right-censor guard: drop last 2 years of each country
D=D[D.pub_year<=D.country.map(maxy)-2]
A=D[D.ap]
Y=A.groupby(['country','pub_year']).agg(n_ap=('isbn13','size'),singleton=('singleton','mean'),own=('own','mean'),small_shared=('cls',lambda s:(s=='small_shared').mean()),bigpool=('bigpool','mean'),block10=('block10','mean'),block100=('block100','mean'),reglen=('reglen','mean'),n_singleton=('singleton','sum')).reset_index()
N=D[~D.ap].groupby(['country','pub_year']).agg(nonap_singleton=('singleton','mean'),nonap_block10=('block10','mean'),nonap_reglen=('reglen','mean')).reset_index()
Y=Y.merge(N,on=['country','pub_year'],how='left'); Y.to_csv(f'{OUT}/hb_by_year.csv',index=False)
# distinct singleton-prefix authors; AP books per distinct prefix
EV={'es':2012,'pt':2015,'fr':2019}
res=[]
for k,t in EV.items():
    d=D[D.country.isin([k,'nz','qc']+(['fr'] if k!='fr' else []))&D.pub_year.between(t-3,t+2)].copy()
    d=d[~((d.country=='fr')&(d.pub_year>=2019)&(k!='fr'))]
    d['post']=(d.pub_year>=t).astype(int); d['tr']=(d.country==k).astype(int)
    ap=d[d.ap]; own=ap[ap.tr==1]; ctrl=ap[ap.tr==0]
    for f in ['singleton','own','shared','bigpool','block10','block100','first_use']:
        r=dict(event=k,feature=f,n_pre=int((own.post==0).sum()),n_post=int((own.post==1).sum()))
        for w in (0,1):
            s=own[own.post==w][f]; x=s.sum();Nn=len(s); lo,hi=wil(x,Nn,method='wilson'); r[['pre','post'][w]]=x/Nn; r[['pre','post'][w]+'_ci']=f'[{lo:.3f},{hi:.3f}]'
        for lab,df in (('did_ap',pd.concat([own,ctrl])),('vs_nonap',d[d.tr==1])):
            try:
                if lab=='did_ap': m=smf.logit(f'{f}~post+post:tr+C(country)',df).fit(disp=0,cov_type='HC1'); b='post:tr'
                else: df=df.assign(apf=df.ap.astype(int)); m=smf.logit(f'{f}~post*apf',df).fit(disp=0,cov_type='HC1'); b='post:apf'
                r[lab+'_b']=m.params[b]; r[lab+'_lo'],r[lab+'_hi']=m.conf_int().loc[b]
            except Exception as e: r[lab+'_b']=np.nan
        # non-AP trend for context
        r['nonap_pre']=d[(d.tr==1)&(~d.ap)&(d.post==0)][f].mean(); r['nonap_post']=d[(d.tr==1)&(~d.ap)&(d.post==1)][f].mean()
        res.append(r)
R=pd.DataFrame(res); R.to_csv(f'{OUT}/hb_results.csv',index=False)
pd.set_option('display.width',250); print(R[['event','feature','n_pre','n_post','pre','post','pre_ci','post_ci','nonap_pre','nonap_post','did_ap_b','did_ap_lo','did_ap_hi','vs_nonap_b','vs_nonap_lo','vs_nonap_hi']].round(3).to_string(index=False))
print(Y[Y.country.isin(['es','pt','fr'])&Y.pub_year.between(2008,2020)][['country','pub_year','n_ap','n_singleton','singleton','own','small_shared','bigpool','block10','reglen','nonap_singleton']].round(3).to_string(index=False))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,3,figsize=(15,7))
for j,(k,t) in enumerate(EV.items()):
    y=Y[(Y.country==k)&Y.pub_year.between(2006,2021)]
    axs[0,j].stackplot(y.pub_year,y.singleton,y.own,y.small_shared,y.bigpool,labels=['singleton prefix','own block (1 author)','shared <10 authors','pool >=10 authors'],alpha=.8)
    axs[0,j].axvline(t-.5,c='k',ls=':'); axs[0,j].set_title(f'{k.upper()} AP books by prefix class'); 
    axs[1,j].plot(y.pub_year,y.singleton,'o-',label='AP singleton'); axs[1,j].plot(y.pub_year,y.nonap_singleton,'s--',label='non-AP singleton'); axs[1,j].plot(y.pub_year,y.block10,'^-',label='AP block<=10'); axs[1,j].axvline(t-.5,c='k',ls=':'); axs[1,j].legend(fontsize=7)
axs[0,0].legend(fontsize=7,loc='lower left'); plt.tight_layout(); plt.savefig(f'{OUT}/hb_prefix.png',dpi=140)
