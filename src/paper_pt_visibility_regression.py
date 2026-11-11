"""Visibility regression: is a Portuguese book without an ISBN less likely to be found in Google Books, holding observables fixed?
Sample: stratified Google Books checks (data/interim/gb_cache.jsonl), both groups searched by title + author (no ISBN used in matching).
Outcome: found (strict title/author/year match). Covariates: no ISBN, self-published (AP), their interaction, log pages, UDC main class, title length (words),
publisher type (government / unidentified), place Lisbon or Porto, publication-year FE. LPM with HC1 SE (+ logit check). Stratified sample -> also report weighted estimates (inverse sampling prob.)."""
import json, re, numpy as np, pandas as pd, statsmodels.formula.api as smf
G=pd.read_json('data/interim/gb_cache.jsonl',lines=True).drop_duplicates('id'); G['id']=G.id.astype(str); G=G[~G.err]
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R['id']=R.id.astype(str)
raw=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','udc','place']); raw['id']=raw.id.astype(str)
D=G.merge(R[['id','pub_year','ap','has_isbn','gov','nopub','extent','title']],on='id',how='left').merge(raw,on='id',how='left')
D['noisbn']=(~D.has_isbn).astype(int); D['sp']=D.ap.astype(int)
D['pages']=pd.to_numeric(D.extent.astype(str).str.extract(r'(\d{1,4})')[0],errors='coerce'); D['lpages']=np.log1p(D.pages.fillna(D.pages.median()))
D['udc1']=D.udc.fillna('').str.extract(r'^(\d)')[0].fillna('na'); D['title_words']=D.title.fillna('').str.split().map(len).clip(upper=20)
D['bigcity']=D.place.fillna('').str.contains('Lisboa|Porto',case=False).astype(int); D['gov']=D.gov.astype(int); D['nopub']=D.nopub.astype(int); D['yr']=D.pub_year.astype(int)
print('books',len(D),'| by cell:',D.groupby(['sp','noisbn']).size().to_dict())
# population counts per cell (2010-19 Portuguese print books in the national bibliography) for weights
Rp=R[R.print_like&R.pt&R.pub_year.between(2010,2019)]; pop=Rp.groupby([Rp.ap.astype(int),(~Rp.has_isbn).astype(int)]).size()
D['w']=D.apply(lambda r:pop[(r.sp,r.noisbn)],axis=1)/D.groupby(['sp','noisbn']).id.transform('size')
specs={'M1 raw':'found ~ noisbn*sp','M2 + year FE':'found ~ noisbn*sp + C(yr)','M3 + book controls':'found ~ noisbn*sp + C(yr) + lpages + title_words + C(udc1) + gov + nopub + bigcity'}
rows=[]
for name,f in specs.items():
    m=smf.ols(f,data=D).fit(cov_type='HC1')
    for k in ['noisbn','noisbn:sp']: rows.append(dict(model=name,term=k,coef_pp=100*m.params[k],se_pp=100*m.bse[k],p=m.pvalues[k],n=int(m.nobs)))
mw=smf.wls(specs['M3 + book controls'],data=D,weights=D.w).fit(cov_type='HC1')
for k in ['noisbn','noisbn:sp']: rows.append(dict(model='M3 weighted to population',term=k,coef_pp=100*mw.params[k],se_pp=100*mw.bse[k],p=mw.pvalues[k],n=int(mw.nobs)))
ml=smf.logit(specs['M3 + book controls'].replace('C(yr)','yr'),data=D).fit(disp=0,cov_type='HC1')
me=ml.get_margeff(at='overall').summary_frame().loc[['noisbn']]; print('logit average marginal effect of no ISBN: %.3f (SE %.3f)'%(me['dy/dx'].iloc[0],me['Std. Err.'].iloc[0]))
for name,f in specs.items():
    m=smf.ols(f,data=D).fit(cov_type='HC1'); tt=m.t_test('noisbn + noisbn:sp = 0')
    rows.append(dict(model=name,term='noisbn + noisbn:sp (effect for self-published)',coef_pp=100*float(tt.effect),se_pp=100*float(tt.sd),p=float(tt.pvalue),n=int(m.nobs)))
T=pd.DataFrame(rows); T['effect_for_self_published_pp']=np.nan
for name in T.model.unique():
    a=T[(T.model==name)&(T.term=='noisbn')].coef_pp.iloc[0]; b=T[(T.model==name)&(T.term=='noisbn:sp')].coef_pp.iloc[0]; T.loc[(T.model==name)&(T.term=='noisbn'),'effect_for_self_published_pp']=a+b
pd.set_option('display.width',200); print(T.round(3).to_string(index=False)); T.to_csv('output/paper_pt/visibility_regression.csv',index=False)
print('found rate by cell:'); print(D.groupby(['sp','noisbn']).found.agg(['mean','size']).round(3))
