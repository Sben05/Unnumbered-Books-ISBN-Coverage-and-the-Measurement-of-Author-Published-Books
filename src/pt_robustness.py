"""Portugal robustness: format-invariant AP, placebo distributions, non-linear trend, year-on-year changes, baselines,
ISBN substitution / total self-publishing, Spain-Portugal gap comparison, 2013-vs-2014 record comparison."""
import math,warnings,json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy import stats
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
OUT=ROOT/'output/portugal';rng=np.random.default_rng(20260503)
def wilson(k,n):
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
def lg(k,n):p=(np.asarray(k,float)+.5)/(np.asarray(n,float)+1);return np.log(p/(1-p))
R=pd.read_parquet(ROOT/'data/interim/pt_classified.parquet');R=R[R.pub_year.between(2005,2025)].copy();R['pub_year']=R.pub_year.astype(int)
NN=pd.read_parquet(ROOT/'data/interim/pt_noisbn.parquet');NN=NN[NN.pub_year.between(2005,2025)].copy();NN['pub_year']=NN.pub_year.astype(int)
Y=list(range(2005,2026))
n_isbn=R.groupby('pub_year').size().reindex(Y)
S={}  # name -> (k, n) indexed by year
for nm,c in [('ap_original','author_is_publisher'),('ap_pure','ap_pure'),('ap_consistent','ap_consistent')]:
 S[nm]=(R.groupby('pub_year')[c].sum().reindex(Y),n_isbn)
# records-level totals (unique records with ISBN + ISBN-less)
RR=R.drop_duplicates('record_id');ni=RR.groupby('pub_year').size().reindex(Y);nn_=NN.groupby('pub_year').size().reindex(Y)
S['ap_total_consistent_all_print_records']=((RR.groupby('pub_year').ap_consistent.sum()+NN.groupby('pub_year').ap_consistent.sum()).reindex(Y),ni+nn_)
S['ap_consistent_no_isbn_records']=(NN.groupby('pub_year').ap_consistent.sum().reindex(Y),nn_)
S['ap_consistent_isbn_records']=(RR.groupby('pub_year').ap_consistent.sum().reindex(Y),ni)
apt=RR.groupby('pub_year').ap_consistent.sum().reindex(Y)+NN.groupby('pub_year').ap_consistent.sum().reindex(Y)
S['share_of_ap_records_with_isbn']=(RR.groupby('pub_year').ap_consistent.sum().reindex(Y),apt)
# ---- 1 consistency table
rows=[]
for y in Y:
 r=dict(pub_year=y,print_isbns=int(n_isbn[y]))
 for nm in ['ap_original','ap_pure','ap_consistent']:
  k=int(S[nm][0][y]);lo,hi=wilson(k,r['print_isbns']);r[nm]=k;r['share_'+nm]=k/r['print_isbns'];r[nm+'_wilson_low']=lo;r[nm+'_wilson_high']=hi
 sub=R[R.pub_year==y];r['pure_with_initial_token']=int((sub.ap_pure&sub.publisher_full.str.contains(r'(?:^|[\s;])[A-ZÁÉÍÓÚ]\.')).sum());r['pure_full_name_only']=r['ap_pure']-r['pure_with_initial_token']
 rows.append(r)
C=pd.DataFrame(rows);C.to_csv(OUT/'pt_ap_consistent_by_year.csv',index=False)
# ---- helpers
def series(nm,lo,hi):
 k,n=S[nm];yy=[y for y in Y if lo<=y<=hi];return np.array(yy),lg(k[yy],n[yy])
def supF(y,trim=.15):
 n=len(y);t=np.arange(n);r0=sm.OLS(y,sm.add_constant(t)).fit();Fs={}
 for i in range(math.ceil(n*trim),math.floor(n*(1-trim))+1):
  post=(t>=i).astype(float);r=sm.OLS(y,np.column_stack([np.ones(n),t,post,post*(t-i)])).fit();Fs[i]=((r0.ssr-r.ssr)/2)/(r.ssr/(n-4))
 return Fs,r0
def boot(y,Fobs,kind,B=1500,L=3):
 n=len(y);t=np.arange(n);r0=sm.OLS(y,sm.add_constant(t)).fit();e=r0.resid-r0.resid.mean();f=r0.fittedvalues;c=0
 for _ in range(B):
  if kind=='iid':eb=rng.choice(e,n,replace=True)
  else:
   k=math.ceil(n/L);st=rng.integers(0,n,k);eb=np.concatenate([e[(s+np.arange(L))%n] for s in st])[:n]
  c+=max(supF(f+eb)[0].values())>=Fobs
 return (c+1)/(B+1)
def its(yrs,y,B,lags=3):
 post=(yrs>=B).astype(float);X=sm.add_constant(np.column_stack([yrs-B,post,post*(yrs-B)]));return sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':lags},use_t=True)
# ---- 2 break tests
BR=[]
for nm in ['ap_original','ap_pure','ap_consistent','ap_total_consistent_all_print_records','share_of_ap_records_with_isbn']:
 for lo,hi in [(2005,2025),(2009,2024)]:
  yrs,y=series(nm,lo,hi);Fs,_=supF(y);best=max(Fs,key=Fs.get);Fm=Fs[best];rk=lambda yr:(1+sum(v>Fs[yr-lo] for v in Fs.values())) if yr-lo in Fs else None
  BR.append(dict(outcome=nm,window=f'{lo}-{hi}',best_break_year=int(yrs[best]),supF=Fm,boot_p_iid=boot(y,Fm,'iid'),boot_p_block3=boot(y,Fm,'block'),F_at_2014=Fs.get(2014-lo),F_at_2015=Fs.get(2015-lo),rank_2015=rk(2015),F_at_2016=Fs.get(2016-lo),rank_2016=rk(2016),n_candidates=len(Fs)))
pd.DataFrame(BR).to_csv(OUT/'pt_break_tests_consistent.csv',index=False)
# ---- 3 ITS scans + placebo distributions
IT=[];PL=[]
for nm in ['ap_original','ap_pure','ap_consistent','ap_total_consistent_all_print_records','share_of_ap_records_with_isbn']:
 yrs,y=series(nm,2005,2025)
 for B in range(2008,2021):
  m=its(yrs,y,B);IT.append(dict(outcome=nm,break_year=B,n_pre=int((yrs<B).sum()),pre_slope=m.params[1],level_shift=m.params[2],level_shift_p=m.pvalues[2],level_shift_t=m.tvalues[2],slope_change=m.params[3],slope_change_p=m.pvalues[3],slope_change_t=m.tvalues[3],post_slope=m.params[1]+m.params[3]))
 yp,ypv=series(nm,2005,2014)  # pre-fee data only
 for B in range(2008,2013):
  m=its(yp,ypv,B);PL.append(dict(outcome=nm,placebo_break=B,n_pre=int((yp<B).sum()),n_post=int((yp>=B).sum()),level_shift=m.params[2],level_shift_t=m.tvalues[2],slope_change=m.params[3],slope_change_t=m.tvalues[3]))
IT=pd.DataFrame(IT)
for c in ['level_shift_t','slope_change_t']:IT['rank_abs_'+c]=IT.groupby('outcome')[c].transform(lambda s:s.abs().rank(ascending=False,method='min'))
IT.to_csv(OUT/'pt_its_consistent.csv',index=False)
PL=pd.DataFrame(PL)
act=IT[IT.break_year==2015].set_index('outcome')
PL['actual_2015_level_shift']=PL.outcome.map(act.level_shift);PL['actual_2015_level_shift_t']=PL.outcome.map(act.level_shift_t)
PL['placebo_t_more_extreme_than_2015']=PL.level_shift_t.abs()>=PL.actual_2015_level_shift_t.abs()
PL.to_csv(OUT/'pt_placebo_distribution.csv',index=False)
# ---- 4 non-linear pre-trend (quadratic on 2005-2014) and 5 yoy changes
NL=[];YY=[]
for nm in ['ap_original','ap_consistent','ap_total_consistent_all_print_records']:
 yrs,y=series(nm,2005,2025);pre=yrs<=2014
 for deg,lab in [(1,'linear'),(2,'quadratic')]:
  t=yrs-2005;X=np.column_stack([t**d for d in range(deg+1)]);m=sm.OLS(y[pre],X[pre]).fit();pr=m.get_prediction(X[~pre]).summary_frame(alpha=.05)
  for yr,a,mu,lo,hi in zip(yrs[~pre],y[~pre],pr['mean'],pr['obs_ci_lower'],pr['obs_ci_upper']):
   NL.append(dict(outcome=nm,pretrend_model=lab,year=int(yr),actual_logit=a,predicted_logit=mu,pred_int_low=lo,pred_int_high=hi,outside_95_pred_interval=bool(a<lo or a>hi),actual_share=1/(1+math.exp(-a)),predicted_share=1/(1+math.exp(-mu))))
 # quadratic-baseline ITS
 t=yrs-2005;post=(yrs>=2015).astype(float);X=sm.add_constant(np.column_stack([t,t**2,post,post*(yrs-2015)]));m=sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':3},use_t=True)
 NL.append(dict(outcome=nm,pretrend_model='quadratic ITS (t,t^2,post,post*(t-2015)), all years',year=2015,actual_logit=m.params[3],predicted_logit=np.nan,pred_int_low=m.params[3]-2*m.bse[3],pred_int_high=m.params[3]+2*m.bse[3],outside_95_pred_interval=bool(m.pvalues[3]<.05),actual_share=m.pvalues[3],predicted_share=np.nan))
 d=np.diff(y);dy=yrs[1:];pre_d=d[dy<=2014]
 for yr,v in zip(dy,d):
  YY.append(dict(outcome=nm,year=int(yr),delta_logit=v,delta_pp=100*(1/(1+math.exp(-y[list(yrs).index(yr)]))-1/(1+math.exp(-y[list(yrs).index(yr)-1]))),z_vs_pre2015_changes=(v-pre_d.mean())/pre_d.std(ddof=1),rank_most_negative=int((d<v).sum()+1)))
pd.DataFrame(NL).to_csv(OUT/'pt_nonlinear_trend.csv',index=False);pd.DataFrame(YY).to_csv(OUT/'pt_yoy_changes.csv',index=False)
# ---- 6 baselines
BL=[]
def pooled(nm,a,b):k,n=S[nm];return k[a:b].sum() if False else (k.loc[a:b].sum(),n.loc[a:b].sum())
for nm in ['ap_original','ap_consistent','ap_total_consistent_all_print_records']:
 post=pooled(nm,2016,2025)
 for lab,(a,b) in {'2005-2009':(2005,2009),'2010-2014':(2010,2014),'2012-2014':(2012,2014),'2005-2014':(2005,2014)}.items():
  k1,n1=pooled(nm,a,b);k2,n2=post;p1,p2=k1/n1,k2/n2;pp=(k1+k2)/(n1+n2);z=(p2-p1)/math.sqrt(pp*(1-pp)*(1/n1+1/n2))
  BL.append(dict(outcome=nm,baseline=lab,baseline_share=p1,post_2016_2025_share=p2,diff_pp=100*(p2-p1),z_nominal_iid=z,note='nominal binomial z; ignores year-to-year dependence and classifier error'))
pd.DataFrame(BL).to_csv(OUT/'pt_baseline_comparison.csv',index=False)
# ---- 7 substitution table
SB=pd.DataFrame({'pub_year':Y,'ap_consistent_isbn_records':S['ap_consistent_isbn_records'][0].values,'ap_consistent_no_isbn_records':S['ap_consistent_no_isbn_records'][0].values,'ap_consistent_total':apt.values,
 'share_of_ap_records_with_isbn':(S['ap_consistent_isbn_records'][0]/apt).values,'ap_rate_isbn_records':(S['ap_consistent_isbn_records'][0]/ni).values,'ap_rate_no_isbn_records':(S['ap_consistent_no_isbn_records'][0]/nn_).values,
 'ap_rate_all_print_records':(apt/(ni+nn_)).values,'isbn_records':ni.values,'no_isbn_records':nn_.values});SB.to_csv(OUT/'pt_total_selfpub_consistent.csv',index=False)
# ---- 8 Spain comparison
E=pd.read_parquet(ROOT/'data/interim/es_classified_apc.parquet');E=E[E.pub_year.between(2007,2021)].copy();E['pub_year']=E.pub_year.astype(int);EY=list(range(2007,2022))
nE=E.groupby('pub_year').size().reindex(EY)
ES={nm:(E.groupby('pub_year')[c].sum().reindex(EY),nE) for nm,c in [('ap_original','author_is_publisher'),('ap_pure','ap_pure'),('ap_consistent','ap_consistent')]}
rows=[];SP=[]
for nm in ['ap_original','ap_pure','ap_consistent']:
 yE=lg(ES[nm][0],nE);yP=lg(S[nm][0].loc[EY],n_isbn.loc[EY]);yrs=np.array(EY)
 # Spain alone
 Fs,_=supF(yE);best=max(Fs,key=Fs.get)
 rows.append(dict(unit='Spain alone',outcome=nm,test='sup-F (2007-2021)',best_break_year=int(yrs[best]),stat=Fs[best],p=boot(yE,Fs[best],'block'),F_at_2015=Fs.get(2015-2007),rank_2015=1+sum(v>Fs[2015-2007] for v in Fs.values()) if 2015-2007 in Fs else None))
 Fs,_=supF(yP);best=max(Fs,key=Fs.get)
 rows.append(dict(unit='Portugal same window',outcome=nm,test='sup-F (2007-2021)',best_break_year=int(yrs[best]),stat=Fs[best],p=boot(yP,Fs[best],'block'),F_at_2015=Fs.get(2015-2007),rank_2015=1+sum(v>Fs[2015-2007] for v in Fs.values()) if 2015-2007 in Fs else None))
 gap=yP-yE
 for unit,yy in [('Spain alone',yE),('Portugal same window',yP),('GAP Portugal minus Spain',gap)]:
  for B in range(2010,2020):
   m=its(yrs,yy,B);SP.append(dict(unit=unit,outcome=nm,break_year=B,n_pre=int((yrs<B).sum()),pre_slope=m.params[1],level_shift=m.params[2],level_shift_p=m.pvalues[2],level_shift_t=m.tvalues[2],slope_change=m.params[3],slope_change_p=m.pvalues[3],slope_change_t=m.tvalues[3],post_slope=m.params[1]+m.params[3]))
 pre=yrs<=2014;mg=sm.OLS(gap[pre],sm.add_constant(yrs[pre]-2007)).fit();rows.append(dict(unit='GAP Portugal minus Spain',outcome=nm,test='pre-2015 gap trend (2007-2014)',stat=mg.params[1],p=mg.pvalues[1]))
SP=pd.DataFrame(SP)
for c in ['level_shift_t','slope_change_t']:SP['rank_abs_'+c]=SP.groupby(['unit','outcome'])[c].transform(lambda s:s.abs().rank(ascending=False,method='min'))
SP.to_csv(OUT/'pt_es_its_and_gap.csv',index=False);pd.DataFrame(rows).to_csv(OUT/'pt_es_break_tests.csv',index=False)
cmp=pd.DataFrame({'year':EY,'PT_ap_consistent_pct':100*S['ap_consistent'][0].loc[EY].values/n_isbn.loc[EY].values,'ES_ap_consistent_pct':100*ES['ap_consistent'][0].values/nE.values,'PT_ap_original_pct':100*S['ap_original'][0].loc[EY].values/n_isbn.loc[EY].values,'ES_ap_original_pct':100*ES['ap_original'][0].values/nE.values});cmp.to_csv(OUT/'pt_es_ap_shares.csv',index=False)
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
for c,lab,st in [('PT_ap_consistent_pct','Portugal (consistent AP)','-'),('ES_ap_consistent_pct','Spain (consistent AP)','-'),('PT_ap_original_pct','Portugal (original AP)',':'),('ES_ap_original_pct','Spain (original AP)',':')]:ax[0].plot(cmp.year,cmp[c],st,marker='o',ms=3,label=lab)
ax[0].axvline(2015,color='k',lw=.8);ax[0].set_title('Author = publisher, % of print ISBNs',fontsize=10);ax[0].legend(fontsize=7,frameon=False)
g=lg(S['ap_consistent'][0].loc[EY],n_isbn.loc[EY])-lg(ES['ap_consistent'][0],nE);ax[1].plot(EY,g,marker='o');ax[1].axvline(2015,color='k',lw=.8);ax[1].set_title('Gap in logit share: Portugal minus Spain (consistent AP)',fontsize=10)
for a in ax:a.spines[['top','right']].set_visible(False)
fig.tight_layout();fig.savefig(OUT/'pt_es_ap_comparison.png',dpi=160);plt.close(fig)
# ---- 9 2013 vs 2014 AP records
raw=pd.read_parquet(ROOT/'data/interim/pt_raw.parquet',columns=['id','manufacturer','udc','size'])
A=R[R.ap_consistent&R.pub_year.isin([2013,2014])].merge(raw,left_on='record_id',right_on='id',how='left')
A['pages']=pd.to_numeric(A.extent.str.extract(r'(\d+)\s*p')[0],errors='coerce');A['udc1']=A.udc.str[:1];A['first_author']=A.authors_personal.map(lambda s:(json.loads(s) or [''])[0])
A['init_style']=A.publisher_full.str.contains(r'(?:^|[\s;])[A-ZÁÉÍÓÚ]\.')
cmpr=A.groupby('pub_year').agg(n=('isbn13','size'),distinct_authors=('first_author','nunique'),median_pages=('pages','median'),pct_first_edition_or_blank=('reprint',lambda s:100*(~s).mean()),pct_with_printer=('manufacturer',lambda s:100*(s.fillna('')!='').mean()),pct_initials_style_publisher=('init_style',lambda s:100*s.mean()),pct_original_rule_flagged=('author_is_publisher',lambda s:100*s.mean()),pct_pure_rule_flagged=('ap_pure',lambda s:100*s.mean()),pct_in_service_or_gov=('government',lambda s:100*s.mean()))
cmpr.round(2).to_csv(OUT/'pt_ap_2013_vs_2014_record_profile.csv')
udc=pd.crosstab(A.pub_year,A.udc1,normalize='index').round(3);udc.to_csv(OUT/'pt_ap_2013_vs_2014_udc.csv')
# authors flagged in both formats across the change
pre=R[R.ap_consistent&R.pub_year.between(2010,2013)].copy();post=R[R.ap_consistent&R.pub_year.between(2014,2017)].copy()
for d in (pre,post):d['fa']=d.authors_personal.map(lambda s:(json.loads(s) or [''])[0])
both=set(pre.fa)&set(post.fa)-{''};cont=dict(authors_2010_13=pre.fa.nunique(),authors_2014_17=post.fa.nunique(),authors_in_both=len(both))
json.dump(cont,open(OUT/'pt_ap_author_continuity.json','w'))
samp=[]
for y in (2013,2014):
 d=A[A.pub_year==y].copy();d['h']=d.isbn13.map(lambda s:hashlib.sha1(('pt-style-v1|'+s).encode()).hexdigest());samp.append(d.sort_values('h').head(50))
S2=pd.concat(samp)[['pub_year','isbn13','record_id','title','authors_personal','publisher_full','classification_reason','author_is_publisher','ap_pure','extent','manufacturer','udc','cat_year']];S2['gold_label']='';S2.to_csv(OUT/'ap_2013_vs_2014_sample_for_hand_labelling.csv',index=False)
with pd.option_context('display.width',260,'display.max_columns',40):
 print(C[['pub_year','print_isbns','ap_original','ap_pure','ap_consistent','share_ap_original','share_ap_pure','share_ap_consistent','pure_with_initial_token','pure_full_name_only']].round(4).to_string(index=False))
 print(pd.DataFrame(BR).round(4).to_string(index=False))
 print(IT[IT.break_year.isin([2013,2014,2015,2016,2017])].round(4).to_string(index=False))
 print(PL.round(3).to_string(index=False))
 print(pd.DataFrame(NL).query("pretrend_model!='linear'").round(4).to_string(index=False))
 print(pd.DataFrame(YY).query("year in [2012,2013,2014,2015,2016]").round(3).to_string(index=False))
 print(pd.DataFrame(BL).round(4).to_string(index=False));print(SB.round(4).to_string(index=False))
 print(pd.DataFrame(rows).round(4).to_string(index=False));print(SP[SP.break_year.isin([2014,2015,2016])&SP.outcome.isin(['ap_original','ap_consistent'])].round(4).to_string(index=False))
 print(cmp.round(3).to_string(index=False));print(cmpr.round(2).T.to_string());print(udc.to_string());print(cont)
