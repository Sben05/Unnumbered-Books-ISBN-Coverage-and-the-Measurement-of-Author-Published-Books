"""Germany: by-year series, Wilson CIs, per-million vs other countries, break tests, validation sample, figure.
Input: data/interim/de_classified.parquet (from build_de.py classify). Output: output/germany/*"""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import numpy as np,pandas as pd
import statsmodels.api as sm
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
OUT=ROOT/'output/germany'
def wilson(k,n,z=1.96):
 k=np.asarray(k,float);n=np.asarray(n,float);p=np.where(n>0,k/np.maximum(n,1),np.nan);d=1+z*z/n
 c=(p+z*z/(2*n))/d;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
def main():
 R=pd.read_parquet(ROOT/'data/interim/de_classified.parquet')
 R['pub_year']=R.pub_year.astype(int)
 NFOR=int(R.foreign_bod.sum());json.dump({'foreign_bod_records_dropped':NFOR},open(OUT/'foreign_bod_dropped.json','w'))
 R=R[~R.foreign_bod].copy()  # BoD foreign-market branches (French/Swedish/... ISBNs printed in Norderstedt): not German-market titles
 R['ap']=R.author_is_publisher;R['apc']=R.ap_consistent
 R['svc']=R.service_imprint;R['comb']=R.ap|R.svc
 R['bod']=R.matched_services.str.contains('books on demand');R['svc_nobod']=R.svc&~R.bod
 R['svc_strong']=R.service_documented
 R['title_group']=R.title.str.lower().str.slice(0,60)+'|'+R.authors_personal.map(lambda a:';'.join(sorted(a)))
 R['group']=np.where(R.isbn13.str.startswith('9783'),'978-3',np.where(R.isbn13.str.startswith('9798'),'979-8',np.where(R.isbn13.str.startswith('979'),'979-other',np.where(R.isbn13.str.startswith('9781'),'978-1','978-other'))))
 g=R.groupby('pub_year')
 T=pd.DataFrame({'isbns':g.size(),'ap':g.ap.sum(),'ap_consistent':g.apc.sum(),'ap_explicit':g.explicit.sum(),'service':g.svc.sum(),'service_bod':g.bod.sum(),'service_platform':g.service_platform.sum(),
  'service_author_services':g.service_author_services.sum(),'service_vanity':g.service_vanity.sum(),'service_strong_only':g.svc_strong.sum(),'combined':g.comb.sum(),
  'institutional_selfpub_not_counted':g.institutional_selfpub.sum(),'corporate_self_not_counted':g.corporate_self.sum(),'mixed_candidates_not_counted':g.service_mixed.sum(),
  'thesis':g.thesis.sum(),'government':g.government.sum(),'reprint':g.reprint.sum(),'unidentified_publisher':g.unidentified_publisher.sum(),'isbn_978_3':g.apply(lambda d:(d.group=='978-3').sum()),
  'isbn_979_8':g.apply(lambda d:(d.group=='979-8').sum()),'amazon_imprint':g.amazon_imprint.sum(),
  'ap_isbn_978_3':g.apply(lambda d:(d.ap&(d.group=='978-3')).sum()),'ap_isbn_us_blocks_978_1_979_8':g.apply(lambda d:(d.ap&d.group.isin(['978-1','979-8'])).sum()),'ap_distinct_author_titles':g.apply(lambda d:d[d.ap].title_group.nunique()),
  'norderstedt_place':g.bod_place.sum()}).reset_index()
 for k in ['ap','ap_consistent','service','combined','service_bod','institutional_selfpub_not_counted']:
  T['share_'+k]=T[k]/T.isbns;lo,hi=wilson(T[k],T.isbns);T[k+'_wilson_low']=lo;T[k+'_wilson_high']=hi
 # sensitivity: AP excluding theses, government, reprints
 nt=R[~R.thesis&~R.government&~R.reprint].groupby('pub_year');T['ap_excl_thesis_gov_reprint']=T.pub_year.map(nt.ap.sum());T['isbns_excl_thesis_gov_reprint']=T.pub_year.map(nt.size())
 T['share_ap_excl_thesis_gov_reprint']=T.ap_excl_thesis_gov_reprint/T.isbns_excl_thesis_gov_reprint
 pop=pd.read_csv(ROOT/'config/population_official.csv');pop=pop[pop.iso3=='DEU'].set_index('year').population
 T['population']=T.pub_year.map(pop);
 for k in ['isbns','ap','ap_consistent','service','combined']:T[k+'_per_million']=T[k]/T.population*1e6
 T=T.rename(columns={'pub_year':'year'});T.to_csv(OUT/'de_by_year.csv',index=False)
 # ---- other countries per million
 O=pd.read_csv(ROOT/'output/night/ap_per_million_official_pop.csv');O=O.rename(columns={'ap_isbns':'ap'})
 d=T[['year','ap','ap_per_million','ap_consistent_per_million','combined_per_million']].copy();d.insert(0,'country','de');d=d.rename(columns={'ap_per_million':'per_million'})
 cmp=pd.concat([O[['country','year','ap','per_million']],d[['country','year','ap','per_million']]]).pivot(index='year',columns='country',values='per_million')
 cmp['de_ap_consistent']=T.set_index('year').ap_consistent_per_million;cmp['de_combined']=T.set_index('year').combined_per_million
 cmp.to_csv(OUT/'de_vs_others_ap_per_million.csv')
 # ---- break tests: segmented regression level shift on share (HAC), and placebo ranking
 rows=[]
 def its(series,ev,lo=1998,hi=2023,w=None):
  s=series[(series.index>=lo)&(series.index<=hi)].dropna();t=s.index.values-ev
  X=pd.DataFrame({'c':1.0,'t':t,'post':(t>=0).astype(float),'tpost':np.where(t>=0,t,0)},index=s.index)
  m=sm.OLS(s.values,X).fit(cov_type='HAC',cov_kwds={'maxlags':2});return m
 sh={'ap':T.set_index('year').share_ap,'ap_consistent':T.set_index('year').share_ap_consistent,'service':T.set_index('year').share_service,'combined':T.set_index('year').share_combined,'ap_per_million':T.set_index('year').ap_per_million,
  'service_per_million':T.set_index('year').service_per_million,'bod_share':T.set_index('year').share_service_bod}
 events={'BoD GmbH founded 2001':2001,'tredition/epubli 2007-08':2008,'ISBN-13 switch 2007':2007,'Amazon CreateSpace->KDP print/979-8 2019':2019,'DNB/MVB price events unknown (placebo 2012)':2012,'placebo 2005':2005,'placebo 2015':2015}
 for nme,s in sh.items():
  for en,ev in events.items():
   m=its(s,ev)
   rows.append(dict(series=nme,event=en,event_year=ev,level_shift=m.params['post'],se=m.bse['post'],p=m.pvalues['post'],slope_change=m.params['tpost'],slope_change_p=m.pvalues['tpost'],pre_slope=m.params['t'],n=int(m.nobs)))
 B=pd.DataFrame(rows);B.to_csv(OUT/'de_break_tests.csv',index=False)
 # placebo distribution: |level shift| for every year 2003-2020, standardised by series sd
 pr=[]
 for nme in ('ap','combined','service','ap_per_million'):
  s=sh[nme]
  for ev in range(2003,2021):
   m=its(s,ev,1998,2023);pr.append(dict(series=nme,event_year=ev,level_shift=m.params['post'],t=m.params['post']/m.bse['post']))
 P=pd.DataFrame(pr);P.to_csv(OUT/'de_placebo_breaks.csv',index=False)
 # ---- prefix table, top publishers among flagged (for classifier evidence)
 R.groupby(['pub_year','group']).size().unstack(fill_value=0).to_csv(OUT/'de_isbn_prefix_by_year.csv')
 for nm,mask in [('ap',R.ap),('service',R.svc)]:
  R[mask].groupby('publisher').size().sort_values(ascending=False).head(150).to_csv(OUT/f'de_top_publishers_{nm}.csv')
 R[R.svc].groupby(['matched_services','pub_year']).size().unstack(fill_value=0).to_csv(OUT/'de_service_by_year.csv')
 # ---- validation sample (deterministic hash)
 R['h']=R.isbn13.map(lambda s:hashlib.sha256(('de'+s).encode()).hexdigest())
 cols=['isbn13','pub_year','title','authors_personal','publisher','place','edition','matched_services','classification_reason','ap','ap_consistent','svc','explicit','institutional_selfpub','thesis']
 fl=R[R.comb].sort_values('h').head(200)[cols].assign(flag='flagged');un=R[~R.comb].sort_values('h').head(200)[cols].assign(flag='unflagged')
 V=pd.concat([fl,un]);V['authors_personal']=V.authors_personal.map(lambda a:'; '.join(a));V['gold_label']='';V.to_csv(OUT/'validation_de.csv',index=False)
 # ---- figure
 fig,ax=plt.subplots(2,2,figsize=(12,8));x=T.year
 a=ax[0,0];a.plot(x,T.isbns/1000);a.set_title('Print ISBNs (DE, thousands)');a.set_xlabel('publication year')
 a=ax[0,1]
 for k,l in [('ap','author=publisher'),('service','service imprint'),('combined','combined')]:
  a.plot(x,T['share_'+k]*100,label=l);a.fill_between(x,T[k+'_wilson_low']*100,T[k+'_wilson_high']*100,alpha=.2)
 a.set_title('Share of print ISBNs (%) with Wilson 95% CI');a.legend()
 for e in (2001,2008,2019):a.axvline(e,color='grey',ls=':')
 a=ax[1,0]
 for k,l in [('ap_per_million','AP'),('service_per_million','service'),('combined_per_million','combined')]:a.plot(x,T[k],label=l)
 a.set_title('Per million inhabitants (DEU)');a.legend()
 a=ax[1,1]
 for c in [c for c in cmp.columns if c in ('uk','fr','nz','es','pt','qc')]:a.plot(cmp.index,cmp[c],label=c.upper(),alpha=.7)
 a.plot(cmp.index,cmp['de'],'k',lw=2,label='DE');a.set_title('Author=publisher ISBNs per million (DE vs others)');a.legend(fontsize=7);a.set_yscale('log')
 plt.tight_layout();plt.savefig(OUT/'de_selfpub.png',dpi=130)
 pd.set_option('display.width',250)
 print(T[['year','isbns','ap','ap_consistent','service','service_bod','combined','share_ap','share_service','share_combined','ap_per_million','combined_per_million']].round(4).to_string())
 print(B[B.series.isin(['ap','combined','service'])].round(4).to_string())
 print(cmp.round(2).to_string())
if __name__=='__main__':main()
