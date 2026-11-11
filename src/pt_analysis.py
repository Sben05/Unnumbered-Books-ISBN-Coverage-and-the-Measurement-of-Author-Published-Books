"""Portugal: by-year shares, sensitivity, sup-F break tests, ITS around the 1 Jan 2015 fee start, pre-trend, Amazon-prefix check."""
import math,warnings,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd,statsmodels.api as sm
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
OUT=ROOT/'output/portugal';R=pd.read_parquet(ROOT/'data/interim/pt_classified.parquet')
rng=np.random.default_rng(20260502)
FEE=2015;LO,HI=2005,2025
def wilson(k,n):
 if not n:return (np.nan,np.nan)
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
R=R[R.pub_year.between(1995,2026)].copy();R['pub_year']=R.pub_year.astype(int)
FLAG={2005:'window start: ISBN-bearing records thinner before ~2005',2008:'bump: ISBN-bearing share of records dips (retrospective cataloguing?)',2025:'edge: most recent year, cataloguing lag unknown',2026:'INCOMPLETE: file dated July 2026'}
rows=[]
for y,g in R.groupby('pub_year'):
 n=len(g);r=dict(pub_year=y,print_isbns=n,ap=int(g.author_is_publisher.sum()),service=int(g.service_imprint.sum()),combined=int(g.self_published_combined.sum()),
  both=int((g.author_is_publisher&g.service_imprint).sum()),chiado_matched=int(g.matched_services.str.contains('chiado').sum()),corporate_self_not_counted=int(g.corporate_self.sum()),
  mixed_candidates_not_counted=int(g.service_mixed.sum()),completeness_flag=FLAG.get(y,''),in_main_window=LO<=y<=HI)
 for c in ['ap','service','combined']:
  r['share_'+c]=r[c]/n;lo,hi=wilson(r[c],n);r[c+'_wilson_low']=lo;r[c+'_wilson_high']=hi
 rows.append(r)
BY=pd.DataFrame(rows);BY.to_csv(OUT/'pt_by_year.csv',index=False)
fig,ax=plt.subplots(figsize=(8.5,4.6));m=BY[BY.in_main_window]
for c,col,lab in [('combined','#1f3b73','Combined (AP or service)'),('ap','#c8572b','Author = publisher'),('service','#2a8c6e','Service imprint')]:
 ax.plot(m.pub_year,m['share_'+c]*100,marker='o',color=col,label=lab,lw=1.8,ms=4);ax.fill_between(m.pub_year,m[c+'_wilson_low']*100,m[c+'_wilson_high']*100,color=col,alpha=.12)
ax.axvline(FEE,color='k',lw=1);ax.axvline(FEE+1,color='k',lw=1,ls='--');top=ax.get_ylim()[1]
ax.text(FEE+.05,top*.97,'2015\n(fees from 1 Jan)',va='top',fontsize=8);ax.text(FEE+1.05,top*.80,'2016: first fully\nexposed year',va='top',fontsize=8)
ax.set_ylabel('% of print ISBNs');ax.set_xlabel('Publication year');ax.set_title('Portugal (BNP): self-published share of catalogued print ISBNs',fontsize=10)
ax.legend(frameon=False,fontsize=8,loc='upper left');ax.spines[['top','right']].set_visible(False)
fig.text(.01,.01,'Descriptive. 95% Wilson CIs (nominal). Service series is ~99% one imprint (Chiado). 2026 excluded. Classifier precision unknown.',fontsize=6.5)
fig.tight_layout(rect=(0,.03,1,1));fig.savefig(OUT/'pt_shares.png',dpi=160);plt.close(fig)
# sensitivity
T=pd.Series(True,index=R.index)
R['init_only']=R.author_is_publisher&(R.classification_reason=='compatible_initials')
R['ap_exact']=R.author_is_publisher&~R.classification_reason.isin(['compatible_initials'])
R['chiado']=R.matched_services.str.contains('chiado')
R['weak_svc']=R.matched_services.str.contains('chiado|cordel|epica')
R['strong_svc']=R.service_imprint&~R.weak_svc
V={'main':(T,R.self_published_combined),'author_only':(T,R.author_is_publisher),'exclude_mixed':(~R.service_mixed,R.self_published_combined),
 'exclude_vanity':(T,R.author_is_publisher|R.service_platform),'exclude_government':(~R.government,R.self_published_combined),'exclude_reprints':(~R.reprint,R.self_published_combined),
 'initial_only':(T,R.init_only),'ap_without_initial_matches':(T,R.ap_exact),'exclude_initial_matches':(T,R.self_published_combined&~R.init_only),
 'include_mixed_candidates':(T,R.self_published_combined|R.service_mixed),'exclude_weak_evidence_services':(T,R.author_is_publisher|R.strong_svc),
 'service_excluding_chiado':(T,R.service_imprint&~R.chiado),'chiado_only':(T,R.chiado),'exclude_unidentified_publisher':(~R.unidentified_publisher,R.self_published_combined)}
S=[]
for k,(den,num) in V.items():
 for y,idx in R[den].groupby('pub_year').groups.items():
  n=len(idx);kk=int(num.loc[idx].sum());lo,hi=wilson(kk,n);S.append(dict(variant=k,pub_year=y,denominator=n,numerator=kk,share=kk/n,wilson_low=lo,wilson_high=hi))
S=pd.DataFrame(S);S.to_csv(OUT/'pt_sensitivity.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(11.5,4.4));Sm=S[S.pub_year.between(LO,HI)]
for k in V:
 if k in('initial_only','ap_without_initial_matches','chiado_only','service_excluding_chiado'):continue
 d=Sm[Sm.variant==k];axs[0].plot(d.pub_year,d.share*100,label=k,lw=1.8 if k=='main' else 1.0,color='k' if k=='main' else None)
for k in ('author_only','initial_only','ap_without_initial_matches','chiado_only','service_excluding_chiado'):
 d=Sm[Sm.variant==k];axs[1].plot(d.pub_year,d.share*100,label=k,lw=1.3)
axs[0].set_title('Sensitivity variants (% of print ISBNs)',fontsize=10);axs[0].legend(fontsize=6,frameon=False);axs[1].set_title('Composition: AP by match type; service by imprint',fontsize=10);axs[1].legend(fontsize=6.5,frameon=False)
for a in axs:a.axvline(FEE,color='k',lw=.8);a.axvline(FEE+1,color='k',lw=.8,ls='--');a.set_xlabel('Publication year');a.spines[['top','right']].set_visible(False)
fig.tight_layout();fig.savefig(OUT/'pt_sensitivity.png',dpi=160);plt.close(fig)
# tests
def series(col,lo,hi,df=None):
 d=BY[BY.pub_year.between(lo,hi)];p=((d[col]+.5)/(d.print_isbns+1)).values;return d.pub_year.values,np.log(p/(1-p))  # +0.5 continuity correction (zero counts pre-2009)
def fit_break(y,i):
 n=len(y);t=np.arange(n);post=(t>=i).astype(float);X=np.column_stack([np.ones(n),t,post,post*(t-i)]);return sm.OLS(y,X).fit()
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
  c+=max(supF(f+eb)[0].values())>=Fobs
 return (c+1)/(B+1)
BR=[]
extra={'ap_without_initial_matches':'ap_exact','initial_only':'init_only'}
def add_series(name,mask):
 g=R.groupby('pub_year').apply(lambda d:pd.Series({'k':int(mask.loc[d.index].sum()),'n':len(d)}));BY[name]=BY.pub_year.map(g.k)
add_series('ap_exact',R.ap_exact);add_series('init_only',R.init_only)
for lo,hi in [(LO,HI),(2009,2024)]:
 for col in ['ap','service','combined','ap_exact']:
  yrs,y=series(col,lo,hi);Fs,_=supF(y);best=max(Fs,key=Fs.get);Fm=Fs[best]
  rank=lambda yr:(1+sum(v>Fs[yr-lo] for v in Fs.values())) if yr-lo in Fs else None
  r0=sm.OLS(y,sm.add_constant(np.arange(len(y)))).fit()
  BR.append(dict(outcome=col,window=f'{lo}-{hi}',n_years=len(y),candidate_range=f'{lo+min(Fs)}-{lo+max(Fs)}',best_break_year=int(yrs[best]),supF=Fm,boot_p_iid=boot(y,Fm,'iid'),boot_p_block3=boot(y,Fm,'block'),
   F_at_2015=Fs.get(2015-lo),rank_2015=rank(2015),F_at_2016=Fs.get(2016-lo),rank_2016=rank(2016),n_candidates=len(Fs),is_2015_best=bool(yrs[best]==2015),is_2016_best=bool(yrs[best]==2016),linear_trend_slope_logit=r0.params[1],
   note='null=linear trend in logit share; alt=level shift+slope change at unknown year; trim 15% (ceil/floor); residual bootstrap B=2000; iid bootstrap ignores serial correlation and likely understates p; block (L=3) is a rough check'))
pd.DataFrame(BR).to_csv(OUT/'pt_break_tests.csv',index=False)
IT=[]
for col in ['ap','service','combined','ap_exact']:
 yrs,y=series(col,LO,HI)
 for B in range(2010,2021):
  post=(yrs>=B).astype(float);npre=int((yrs<B).sum());npost=int((yrs>=B).sum())
  row=dict(outcome=col,break_year=B,label='requested break (fees from 1 Jan 2015)' if B==2015 else 'first fully exposed year' if B==2016 else 'placebo',is_placebo=B not in(2015,2016),n_pre=npre,n_post=npost)
  X=sm.add_constant(np.column_stack([yrs-B,post,post*(yrs-B)]));m=sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':3},use_t=True)
  row.update(pre_slope=m.params[1],pre_slope_se=m.bse[1],level_shift=m.params[2],level_shift_se=m.bse[2],level_shift_p=m.pvalues[2],slope_change=m.params[3],slope_change_se=m.bse[3],slope_change_p=m.pvalues[3],
   level_shift_t=m.tvalues[2],slope_change_t=m.tvalues[3],post_slope=m.params[1]+m.params[3],note='logit(share); Newey-West 3 lags, t(df) p-values; n=21, HAC unreliable at this size');IT.append(row)
IT=pd.DataFrame(IT)
for c in['level_shift_t','slope_change_t']:IT['rank_abs_'+c]=IT.groupby('outcome')[c].transform(lambda s:s.abs().rank(ascending=False,method='min'))
IT.to_csv(OUT/'pt_its.csv',index=False)
PT=[]
for col in['ap','service','combined','ap_exact']:
 for lo,hi,lab in[(2010,2014,'2010-2014 (5 pts)'),(2005,2013,'2005-2013 (9 pts; excludes 2014 cataloguing-style change year)'),(2005,2014,'2005-2014 (10 pts)')]:
  yrs,y=series(col,lo,hi);m=sm.OLS(y,sm.add_constant(yrs-lo)).fit()
  PT.append(dict(outcome=col,window=lab,n=len(y),slope_logit_per_year=m.params[1],se=m.bse[1],p=m.pvalues[1],approx_pct_change_in_odds_per_year=100*(math.exp(m.params[1])-1)))
pd.DataFrame(PT).to_csv(OUT/'pt_pretrend.csv',index=False)
# pre vs post descriptive means
Z=BY.set_index('pub_year');desc=[]
for col in['ap','service','combined']:
 desc.append(dict(outcome=col,mean_share_2010_2014=(Z.loc[2010:2014,col].sum()/Z.loc[2010:2014,'print_isbns'].sum()),mean_share_2016_2025=(Z.loc[2016:2025,col].sum()/Z.loc[2016:2025,'print_isbns'].sum()),share_2014=Z.loc[2014,col]/Z.loc[2014,'print_isbns'],share_2015=Z.loc[2015,col]/Z.loc[2015,'print_isbns'],share_2016=Z.loc[2016,col]/Z.loc[2016,'print_isbns']))
pd.DataFrame(desc).to_csv(OUT/'pt_pre_post_means.csv',index=False)
# prefixes / Amazon
G=R[R.pub_year.between(2005,2026)].groupby(['pub_year','isbn_group']).size().unstack(fill_value=0);G['total']=G.sum(axis=1)
G['amazon_named_imprint']=R[R.pub_year.between(2005,2026)].groupby('pub_year').amazon_imprint.sum();G.reset_index().to_csv(OUT/'pt_isbn_prefix_by_year.csv',index=False)
NN=pd.read_parquet(ROOT/'data/interim/pt_noisbn.parquet');NN=NN[NN.pub_year.between(2005,2026)]
nn=NN.groupby('pub_year').agg(print_records_without_valid_isbn=('pub_year','size'),ap=('author_is_publisher','sum'),service=('service_imprint','sum'),combined=('self_published_combined','sum')).reset_index();nn['pub_year']=nn.pub_year.astype(int)
nn=nn.merge(BY[['pub_year','print_isbns']],on='pub_year');nn['no_isbn_share_of_print_records']=nn.print_records_without_valid_isbn/(nn.print_records_without_valid_isbn+nn.print_isbns);nn.to_csv(OUT/'pt_noisbn_by_year.csv',index=False)
# does self-publishing move off ISBNs? AP among ISBN-bearing vs ISBN-less print records
RR=R[R.pub_year.between(2005,2026)].drop_duplicates('record_id');a=RR.groupby('pub_year').agg(isbn_records=('record_id','size'),ap_isbn=('author_is_publisher','sum')).reset_index()
a=a.merge(nn[['pub_year','print_records_without_valid_isbn','ap']].rename(columns={'ap':'ap_no_isbn'}),on='pub_year')
a['ap_total']=a.ap_isbn+a.ap_no_isbn;a['share_of_ap_records_with_isbn']=a.ap_isbn/a.ap_total;a['ap_rate_isbn_records']=a.ap_isbn/a.isbn_records;a['ap_rate_no_isbn_records']=a.ap_no_isbn/a.print_records_without_valid_isbn
a['ap_rate_all_print_records']=a.ap_total/(a.isbn_records+a.print_records_without_valid_isbn);a.to_csv(OUT/'pt_ap_isbn_substitution_check.csv',index=False);print(a.round(4).to_string(index=False))
L=R[R.pub_year.between(2005,2026)&R.cat_year.between(2000,2026)].groupby(['pub_year','cat_year']).size().unstack(fill_value=0);L.to_csv(OUT/'pt_pubyear_by_catyear.csv')
with pd.option_context('display.width',250):
 print(BY[['pub_year','print_isbns','ap','service','combined','share_ap','share_combined']].query('pub_year>=2005').round(4).to_string(index=False))
 print(pd.DataFrame(BR).drop(columns='note').round(4).to_string(index=False))
 print(IT[IT.outcome.isin(['ap','combined'])&IT.break_year.between(2013,2017)].drop(columns=['note','pre_slope_se','level_shift_se','slope_change_se','level_shift_t','slope_change_t']).round(4).to_string(index=False))
 print(pd.DataFrame(PT).round(4).to_string(index=False));print(pd.DataFrame(desc).round(4).to_string(index=False));print(G.to_string());print(nn.round(4).to_string(index=False))
