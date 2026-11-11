"""Spain: by-year shares, sensitivity, sup-F break tests, ITS, pre-trend, 979-8 check."""
import sys,math,warnings,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd,statsmodels.api as sm
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
OUT=ROOT/'output/spain';R=pd.read_parquet(ROOT/'data/interim/es_classified.parquet')
rng=np.random.default_rng(20260501)
def wilson(k,n):
 if not n:return (np.nan,np.nan)
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
YEARS=range(2007,2023)
R=R[R.pub_year.between(2007,2022)].copy();R['pub_year']=R.pub_year.astype(int)
FLAG={2007:'edge: no bibliography-2006 file (early-catalogued forward records missing)',2021:'edge: bibliography-2022 file only partial',2022:'INCOMPLETE: bibliography-2022 partial, 2023 absent'}
# ---- by year
rows=[]
for y,g in R.groupby('pub_year'):
 n=len(g);r=dict(pub_year=y,print_isbns=n,ap=int(g.author_is_publisher.sum()),service=int(g.service_imprint.sum()),combined=int(g.self_published_combined.sum()),
  both=int((g.author_is_publisher&g.service_imprint).sum()),corporate_self_not_counted=int(g.corporate_self.sum()),mixed_not_counted=int(g.service_mixed.sum()),completeness_flag=FLAG.get(y,''),in_main_window=2007<=y<=2021)
 for c in ['ap','service','combined']:
  r['share_'+c]=r[c]/n;lo,hi=wilson(r[c],n);r[c+'_wilson_low']=lo;r[c+'_wilson_high']=hi
 rows.append(r)
BY=pd.DataFrame(rows);BY.to_csv(OUT/'es_by_year.csv',index=False)
# ---- figure
fig,ax=plt.subplots(figsize=(8,4.6));m=BY[BY.in_main_window]
for c,col,lab in [('combined','#1f3b73','Combined (AP or service)'),('ap','#c8572b','Author = publisher'),('service','#2a8c6e','Service imprint')]:
 ax.plot(m.pub_year,m['share_'+c]*100,marker='o',color=col,label=lab,lw=1.8,ms=4)
 ax.fill_between(m.pub_year,m[c+'_wilson_low']*100,m[c+'_wilson_high']*100,color=col,alpha=.12)
ax.axvline(2011,color='k',lw=1);ax.axvline(2011.95,color='k',lw=1,ls='--')
ax.text(2011.05,ax.get_ylim()[1]*.97,'2011',va='top',fontsize=8);ax.text(2012.0,ax.get_ylim()[1]*.97,'fees charged\nfrom 12 Dec 2011',va='top',fontsize=8)
ax.set_ylabel('% of print ISBNs');ax.set_xlabel('Publication year');ax.set_title('Spain (BNE): self-published share of catalogued print ISBNs',fontsize=10)
ax.legend(frameon=False,fontsize=8,loc='upper left');ax.spines[['top','right']].set_visible(False)
fig.text(.01,.01,'Descriptive. Shading: nominal 95% Wilson CIs. 2007 and 2021 are edge years; 2022 excluded. Classifier precision unknown.',fontsize=6.5)
fig.tight_layout(rect=(0,.03,1,1));fig.savefig(OUT/'es_shares.png',dpi=160);plt.close(fig)
# ---- sensitivity
R['init_only']=R.author_is_publisher&(R.classification_reason=='compatible_initials')
R['ver_svc']=R.service_imprint&~R.svc_unverified
V={'main':(R.index==R.index,R.self_published_combined),'author_only':(R.index==R.index,R.author_is_publisher),
 'exclude_mixed':(~R.service_mixed,R.self_published_combined),'exclude_vanity':(R.index==R.index,R.author_is_publisher|R.service_platform),
 'exclude_government':(~R.government,R.self_published_combined),'exclude_reprints':(~R.reprint,R.self_published_combined),
 'initial_only':(R.index==R.index,R.init_only),'exclude_initial_matches':(R.index==R.index,R.self_published_combined&~R.init_only),
 'include_mixed':(R.index==R.index,R.self_published_combined|R.service_mixed),'exclude_unverified_services':(R.index==R.index,R.author_is_publisher|R.ver_svc),
 'exclude_unidentified_publisher':(~R.unidentified_publisher,R.self_published_combined)}
S=[]
for k,(den,num) in V.items():
 for y,idx in R[den].groupby('pub_year').groups.items():
  n=len(idx);kk=int(num.loc[idx].sum());lo,hi=wilson(kk,n);S.append(dict(variant=k,pub_year=y,denominator=n,numerator=kk,share=kk/n,wilson_low=lo,wilson_high=hi))
S=pd.DataFrame(S);S.to_csv(OUT/'es_sensitivity.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(11,4.4))
Sm=S[S.pub_year.between(2007,2021)]
for k in V:
 d=Sm[Sm.variant==k];axs[0 if k not in('initial_only',) else 1].plot(d.pub_year,d.share*100,label=k,lw=1.6 if k=='main' else 1.1,color='k' if k=='main' else None)
axs[0].set_title('Sensitivity variants (% of print ISBNs)',fontsize=10);axs[0].legend(fontsize=6.5,frameon=False)
d=Sm[Sm.variant=='initial_only'];axs[1].plot(d.pub_year,d.share*100,color='#c8572b');axs[1].set_title('initial_only: AP matches that rest on initials only',fontsize=10)
for a in axs:a.axvline(2011,color='k',lw=.8);a.axvline(2011.95,color='k',lw=.8,ls='--');a.set_xlabel('Publication year');a.spines[['top','right']].set_visible(False)
fig.tight_layout();fig.savefig(OUT/'es_sensitivity.png',dpi=160);plt.close(fig)
# ---- series for tests
def series(col,lo,hi):
 d=BY[BY.pub_year.between(lo,hi)];p=(d[col]/d.print_isbns).values;return d.pub_year.values,np.log(p/(1-p))
def fit_break(y,i):
 n=len(y);t=np.arange(n);post=(t>=i).astype(float);X=np.column_stack([np.ones(n),t,post,post*(t-i)]);r=sm.OLS(y,X).fit();return r
def supF(y,trim=.15):
 n=len(y);t=np.arange(n);r0=sm.OLS(y,sm.add_constant(t)).fit();Fs={}
 for i in range(math.ceil(n*trim),math.floor(n*(1-trim))+1):
  r=fit_break(y,i);Fs[i]=((r0.ssr-r.ssr)/2)/(r.ssr/(n-4))
 return Fs,r0
def boot(y,Fobs,kind,B=2000,L=3):
 n=len(y);t=np.arange(n);r0=sm.OLS(y,sm.add_constant(t)).fit();e=r0.resid-r0.resid.mean();f=r0.fittedvalues;c=0
 for _ in range(B):
  if kind=='iid':eb=rng.choice(e,n,replace=True)
  else:
   k=math.ceil(n/L);st=rng.integers(0,n,k);eb=np.concatenate([e[(s+np.arange(L))%n] for s in st])[:n]
  Fb=supF(f+eb)[0];c+=max(Fb.values())>=Fobs
 return (c+1)/(B+1)
BR=[]
for lo,hi in [(2007,2021),(2008,2020)]:
 for col in ['ap','service','combined']:
  yrs,y=series(col,lo,hi);Fs,_=supF(y);best=max(Fs,key=Fs.get);Fm=Fs[best]
  rank=lambda yr:1+sum(v>Fs[yr-lo] for v in Fs.values()) if yr-lo in Fs else None
  r0=sm.OLS(y,sm.add_constant(np.arange(len(y)))).fit()
  BR.append(dict(outcome=col,window=f'{lo}-{hi}',n_years=len(y),candidate_range=f'{lo+min(Fs)}-{lo+max(Fs)}',best_break_year=int(yrs[best]),supF=Fm,
   boot_p_iid=boot(y,Fm,'iid'),boot_p_block3=boot(y,Fm,'block'),F_at_2011=Fs.get(2011-lo),rank_2011=rank(2011),F_at_2012=Fs.get(2012-lo),rank_2012=rank(2012),
   n_candidates=len(Fs),is_2011_best=bool(yrs[best]==2011),is_2012_best=bool(yrs[best]==2012),linear_trend_slope_logit=r0.params[1],
   note='null=linear trend; alt=level shift+slope change at unknown year; trim 15% (ceil/floor); residual bootstrap B=2000; iid bootstrap ignores serial correlation and likely understates p; block bootstrap (L=3) is a rough check'))
pd.DataFrame(BR).to_csv(OUT/'es_break_tests.csv',index=False)
# ---- ITS + placebos
IT=[]
for col in ['ap','service','combined']:
 yrs,y=series(col,2007,2021)
 for B in range(2007,2016):
  post=(yrs>=B).astype(float);npre=int((yrs<B).sum());npost=int((yrs>=B).sum())
  row=dict(outcome=col,break_year=B,is_placebo=B not in (2011,2012),label='requested break' if B==2011 else 'fee-start year (charging began 12 Dec 2011)' if B==2012 else 'placebo',n_pre=npre,n_post=npost)
  if npre<3:
   row['note']='not estimable: fewer than 3 pre-break years (data start 2007)'
  else:
   X=sm.add_constant(np.column_stack([yrs-B,post,post*(yrs-B)]));m=sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':3},use_t=True)
   row.update(pre_slope=m.params[1],pre_slope_se=m.bse[1],level_shift=m.params[2],level_shift_se=m.bse[2],level_shift_p=m.pvalues[2],slope_change=m.params[3],slope_change_se=m.bse[3],slope_change_p=m.pvalues[3],
    level_shift_t=m.tvalues[2],slope_change_t=m.tvalues[3],post_slope=m.params[1]+m.params[3],note='logit(share); Newey-West 3 lags, t(df) p-values; n=15, HAC unreliable at this size')
  IT.append(row)
IT=pd.DataFrame(IT)
for c in ['level_shift_t','slope_change_t']:
 IT['rank_abs_'+c]=IT.groupby('outcome')[c].transform(lambda s:s.abs().rank(ascending=False,method='min'))
IT.to_csv(OUT/'es_its.csv',index=False)
# ---- pre-trend
PT=[]
for col in ['ap','service','combined']:
 for lo,hi,lab in [(2007,2010,'2007-2010 (4 pts; last full pre-fee years)'),(2007,2011,'2007-2011 (5 pts; fees began 12 Dec 2011 so 2011 pub-year is pre-fee; no half-year data exist)')]:
  yrs,y=series(col,lo,hi);m=sm.OLS(y,sm.add_constant(yrs-lo)).fit()
  PT.append(dict(outcome=col,window=lab,n=len(y),slope_logit_per_year=m.params[1],se=m.bse[1],p=m.pvalues[1],approx_pct_change_in_odds_per_year=100*(math.exp(m.params[1])-1)))
pd.DataFrame(PT).to_csv(OUT/'es_pretrend.csv',index=False)
# ---- 979-8 / Amazon
G=R.groupby(['pub_year','isbn_group']).size().unstack(fill_value=0)
G['total']=G.sum(axis=1);G['amazon_imprint_createspace_or_independently']=R.groupby('pub_year').amazon_imprint.sum()
G['service_platform_tier_all_names']=R.groupby('pub_year').service_platform.sum()
G.reset_index().to_csv(OUT/'es_isbn_prefix_by_year.csv',index=False)
NN=pd.read_parquet(ROOT/'data/interim/es_noisbn.parquet');NN=NN[NN.pub_year.between(2007,2022)]
nn=NN.groupby('pub_year').agg(print_records_without_valid_isbn=('pub_year','size'),ap=('author_is_publisher','sum'),service=('service_imprint','sum'),combined=('self_published_combined','sum')).reset_index()
nn['pub_year']=nn.pub_year.astype(int);nn=nn.merge(BY[['pub_year','print_isbns']],on='pub_year');nn['no_isbn_share_of_print_records']=nn.print_records_without_valid_isbn/(nn.print_records_without_valid_isbn+nn.print_isbns)
nn['combined_share_among_no_isbn']=nn.combined/nn.print_records_without_valid_isbn;nn.to_csv(OUT/'es_noisbn_by_year.csv',index=False)
# ---- lag completeness
L=R.groupby(['pub_year','bib_year']).size().unstack(fill_value=0);L.to_csv(OUT/'es_pubyear_by_bibyear.csv')
print(BY[['pub_year','print_isbns','ap','service','combined','share_combined']].round(4).to_string(index=False))
print(pd.DataFrame(BR).drop(columns='note').round(4).to_string(index=False))
print(IT[IT.outcome=='combined'].drop(columns=['note']).round(4).to_string(index=False))
print(pd.DataFrame(PT).round(4).to_string(index=False));print(G.to_string());print(nn.round(4).to_string(index=False))
