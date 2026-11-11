"""Book-level regressions (BNP national bibliography, Portuguese print books 2008-2019): outcome = book has NO ISBN.
M1 DiD: noisbn ~ ap*post + year FE (+controls). M2 adds ap x linear pre-trend (lets self-publishers have their own trend).
M3 event study: ap x year dummies (ref 2014 = last pre-fee year). Linear probability model, SE clustered by publisher. Descriptive."""
import re, unicodedata, pandas as pd, numpy as np, statsmodels.formula.api as smf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2008,2019)].copy()
def norm(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s)).strip()
R['pk']=R.publisher.map(norm); R.loc[R.pk=='','pk']='unknown_'+R.id.astype(str)
R['noisbn']=(~R.has_isbn).astype(int); R['apx']=R.ap.astype(int); R['post']=(R.pub_year>=2015).astype(int); R['yr']=R.pub_year.astype(int)
R['t']=R.yr-2014; R['pages']=pd.to_numeric(R.extent.astype(str).str.extract(r'(\d{1,4})')[0],errors='coerce'); R['lp']=np.log1p(R.pages.fillna(R.pages.median()))
R['gov']=R.gov.astype(int); R['nopub']=R.nopub.astype(int)
g=R.pk.astype('category').cat.codes
def fit(f): return smf.ols(f,data=R).fit(cov_type='cluster',cov_kwds={'groups':g})
m1=fit('noisbn ~ apx + apx:post + C(yr) + gov + nopub + lp')
m2=fit('noisbn ~ apx + apx:post + apx:t + C(yr) + gov + nopub + lp')
m3=fit('noisbn ~ apx*C(yr, Treatment(reference=2014)) + gov + nopub + lp')
rows=[]
for name,m,key in [('M1: self-published x post-2015',m1,'apx:post'),('M2: same, allowing own pre-trend for self-published',m2,'apx:post')]:
    b,se=m.params[key],m.bse[key]; rows.append(dict(model=name,coef_pp=100*b,se_pp=100*se,ci_low_pp=100*(b-1.96*se),ci_high_pp=100*(b+1.96*se),n=int(m.nobs)))
rows.append(dict(model='M2 pre-trend term (pp per year, self-published)',coef_pp=100*m2.params['apx:t'],se_pp=100*m2.bse['apx:t'],ci_low_pp=100*(m2.params['apx:t']-1.96*m2.bse['apx:t']),ci_high_pp=100*(m2.params['apx:t']+1.96*m2.bse['apx:t']),n=int(m2.nobs)))
T=pd.DataFrame(rows); print(T.round(2).to_string(index=False)); T.to_csv('output/paper_pt/regression_table.csv',index=False)
ev=[(int(re.search(r'\[T\.(\d+)\]',k).group(1)),m3.params[k],m3.bse[k]) for k in m3.params.index if k.startswith('apx:C(yr')]
E=pd.DataFrame(ev,columns=['year','b','se']).sort_values('year'); E.loc[len(E)]=[2014,0,0]; E=E.sort_values('year'); E['lo']=E.b-1.96*E.se; E['hi']=E.b+1.96*E.se
E[['year','b','se']].assign(b_pp=lambda d:100*d.b,se_pp=lambda d:100*d.se).round(3).to_csv('output/paper_pt/regression_event_study.csv',index=False); print((100*E.set_index('year')[['b','lo','hi']]).round(1).to_string())
fig,ax=plt.subplots(figsize=(8,4.2)); ax.errorbar(E.year,100*E.b,yerr=100*1.96*E.se,fmt='o-',c='#c0392b',capsize=3)
ax.axhline(0,c='#999',lw=.8); ax.axvline(2014.5,c='k',ls=':'); ax.set_ylabel('self-published minus other books:\nchange in % with no ISBN, vs 2014 (points)'); ax.set_xlabel('publication year')
ax.set_title('Event study: no-ISBN gap, self-published vs other books (95% CI)'); plt.tight_layout(); plt.savefig('output/paper_pt/fig_regression_event_study.png',dpi=150)
