"""Reproducible descriptive summaries; no causal or classification-accuracy inference."""
import sys,math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import duckdb,pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=ROOT/'output/selfpub'
WINDOWS={'uk':(1995,2014),'nz':(1995,2014),'fr':(2010,2021),'qc':(2010,2021)}
LABELS={'uk':'United Kingdom','nz':'New Zealand','fr':'France','qc':'Québec'}
def wilson(k,n):
 if not n:return (float('nan'),float('nan'))
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return c-h,c+h
def rates(df):
 df['share']=df.self_published/df.print_isbns
 ci=[wilson(k,n) for k,n in zip(df.self_published,df.print_isbns)]
 df['wilson_low']=[v[0] for v in ci];df['wilson_high']=[v[1] for v in ci]
 return df
def main():
 OUT.mkdir(exist_ok=True,parents=True);(OUT/'figures').mkdir(exist_ok=True)
 yearly=[];cover=[];sens=[];context=[];candidates=[];totals=[]
 for source,(lo,hi) in WINDOWS.items():
  con=duckdb.connect();con.execute("SET memory_limit='3GB'")
  con.execute(f"CREATE VIEW c AS SELECT * FROM read_parquet('{ROOT}/data/interim/{source}_catalogue.parquet')")
  con.execute(f"CREATE VIEW r AS SELECT * FROM read_parquet('{ROOT}/data/interim/{source}_records.parquet')")
  con.execute(f"CREATE VIEW d AS SELECT * FROM read_parquet('{ROOT}/data/interim/{source}_classified.parquet')")
  totals.append(dict(source=source,raw_records=con.execute('SELECT count(*) FROM c').fetchone()[0],classified_isbns=con.execute('SELECT count(*) FROM d').fetchone()[0]))
  y=con.execute('''SELECT source,pub_year,count(*) print_isbns,sum(self_pub::INT) self_published,
   sum(author_is_publisher::INT) author_is_publisher,sum(service_imprint::INT) service_imprint,
   sum((author_is_publisher AND service_imprint)::INT) both_flags,sum(corporate_self::INT) corporate_self,
   sum(service_platform::INT) platform,sum(service_author_services::INT) author_services,sum(service_vanity::INT) vanity,
   sum(unidentified_publisher::INT) unidentified_publisher,sum((len(authors_personal)=0)::INT) no_personal_author
   FROM d GROUP BY 1,2 ORDER BY 2''').df()
  y=rates(y);y['main_window']=y.pub_year.between(lo,hi);yearly.append(y)
  cv=con.execute('''SELECT source,pub_year,count(*) total_records,sum(country_eligible::INT) country_records,
   sum((len(isbn13s)>0)::INT) records_with_valid_isbn,
   sum((country_eligible AND is_published)::INT) country_published_records,
   sum((country_eligible AND is_published AND is_print)::INT) country_print_records,
   sum((country_eligible AND is_published AND is_print AND len(isbn13s)>0)::INT) country_print_with_isbn,
   sum((country_eligible AND is_published AND is_print AND len(publishers)>0)::INT) country_print_with_publisher,
   sum((country_eligible AND is_published AND is_print AND len(authors_personal)>0)::INT) country_print_with_personal_author
   FROM c WHERE pub_year BETWEEN 1995 AND 2026 GROUP BY 1,2 ORDER BY 2''').df()
  dup=con.execute('''SELECT pub_year,count(*) raw_isbn_occurrences,count(DISTINCT isbn13) distinct_isbns_before_filters,
    count(*)-count(DISTINCT isbn13) duplicate_isbn_occurrences FROM r WHERE pub_year BETWEEN 1995 AND 2026 GROUP BY 1''').df()
  cv=cv.merge(dup,on='pub_year',how='left').merge(y[['pub_year','print_isbns']],on='pub_year',how='left')
  cv['valid_isbn_share_all_records']=cv.records_with_valid_isbn/cv.total_records
  cv['print_share_country_published']=cv.country_print_records/cv.country_published_records.replace(0,np.nan)
  cv['valid_isbn_share_country_print']=cv.country_print_with_isbn/cv.country_print_records.replace(0,np.nan)
  cv['publisher_share_country_print']=cv.country_print_with_publisher/cv.country_print_records.replace(0,np.nan)
  cv['personal_author_share_country_print']=cv.country_print_with_personal_author/cv.country_print_records.replace(0,np.nan)
  cv['absolute_completeness_estimate']=np.nan
  cv['completeness_status']='Not identifiable from one catalogue snapshot; descriptive counts only'
  cv['main_window']=cv.pub_year.between(lo,hi)
  if source=='uk':cv.loc[cv.pub_year>=2017,'completeness_status']='May 2018 snapshot: 2017–18 vulnerable to lag; later years not usable'
  if source=='qc':cv['completeness_status']='ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place'
  cover.append(cv)
  variants={
   'main':('TRUE','self_pub'), 'author_only':('TRUE','author_is_publisher'),
   'services_only':('TRUE','service_imprint'), 'author_plus_platform':('TRUE','self_pub_platform_only'),
   'exclude_vanity':('TRUE','author_is_publisher OR service_platform OR service_author_services'),
   'include_mixed_contract_imprints':('TRUE','self_pub OR service_mixed'),
   'exclude_government_standards':('NOT government AND NOT standards','self_pub'),
   'exclude_theses':('NOT thesis','self_pub'), 'exclude_reprints_new_editions':('NOT reprint_or_new_edition','self_pub'),
   'exclude_all_four':('NOT government AND NOT standards AND NOT thesis AND NOT reprint_or_new_edition','self_pub'),
   'exclude_initials_only_matches':('TRUE',"service_imprint OR (author_is_publisher AND NOT (classification_reason='compatible_initials'))"),
   'include_contributor_matches':('TRUE','self_pub OR contributor_match'),
   'exclude_unidentified_publishers':('NOT unidentified_publisher','self_pub')}
  for variant,(den,num) in variants.items():
   v=con.execute(f'SELECT source,pub_year,count(*) print_isbns,sum(({num})::INT) self_published FROM d WHERE {den} GROUP BY 1,2 ORDER BY 2').df()
   v=rates(v);v['variant']=variant;sens.append(v)
  v=con.execute('''WITH t AS (SELECT source,title_group,min(pub_year) pub_year,bool_or(self_pub) self_pub FROM d GROUP BY 1,2)
   SELECT source,pub_year,count(*) print_isbns,sum(self_pub::INT) self_published FROM t GROUP BY 1,2 ORDER BY 2''').df()
  v=rates(v);v['variant']='normalized_title_author_groups';sens.append(v)
  ctx=con.execute('''SELECT source,pub_year,count(*) print_isbns,sum(amazon_imprint::INT) amazon_imprint,
   sum(us_9798::INT) us_9798_not_amazon_proof,sum((amazon_imprint AND us_9798)::INT) both_amazon_and_9798,
   sum(nz_pool::INT) nz_pool,sum((nz_pool AND self_pub)::INT) nz_pool_flagged,
   sum((NOT nz_pool AND self_pub)::INT) other_prefix_flagged FROM d GROUP BY 1,2 ORDER BY 2''').df();context.append(ctx)
  # Deterministic stratified sample. Blank gold labels are intentional, never machine-generated truth.
  val=con.execute(f'''SELECT * EXCLUDE(title_group) FROM d WHERE pub_year BETWEEN {lo} AND {hi}
   QUALIFY row_number() OVER(PARTITION BY self_pub ORDER BY md5('isbn-study-v1:' || isbn13))<=200
   ORDER BY self_pub DESC,md5('isbn-study-v1:' || isbn13)''').df()
  val['stratum']=np.where(val.self_pub,'flagged','unflagged')
  val['sampling_probability']=[min(200,int(y.loc[y.main_window,'self_published'].sum()))/int(y.loc[y.main_window,'self_published'].sum()) if f else min(200,int((y.loc[y.main_window,'print_isbns']-y.loc[y.main_window,'self_published']).sum()))/int((y.loc[y.main_window,'print_isbns']-y.loc[y.main_window,'self_published']).sum()) for f in val.self_pub]
  val['gold_self_published']=None;val['review_status']='awaiting_independent_review';val['review_evidence_url']='';val['review_notes']=''
  for col in ['authors_personal','contributors_personal','authors_corporate','publishers']:
   val[col]=val[col].map(lambda a:json.dumps(list(a),ensure_ascii=False))
  val.to_csv(OUT/f'validation_{source}.csv',index=False)
  cand=con.execute(f'''WITH a AS (SELECT unnest(publishers) publisher,authors_personal, title_group,isbn13,self_pub FROM d WHERE pub_year BETWEEN {lo} AND {hi}),
   p AS (SELECT publisher,count(DISTINCT isbn13) isbn_count,count(DISTINCT title_group) title_count,sum(self_pub::INT) flagged FROM a GROUP BY 1),
   ac AS (SELECT publisher,unnest(authors_personal) author,title_group FROM a),
   aut AS (SELECT publisher,author,count(DISTINCT title_group) nt FROM ac GROUP BY 1,2),
   ag AS (SELECT publisher,count(*) distinct_authors,sum((nt=1)::INT) single_title_authors FROM aut GROUP BY 1)
   SELECT '{source}' AS source,p.*,ag.* EXCLUDE(publisher),single_title_authors::DOUBLE/nullif(distinct_authors,0) single_title_author_share
   FROM p LEFT JOIN ag USING(publisher) WHERE isbn_count>=5 ORDER BY distinct_authors DESC NULLS LAST''').df()
  cand.to_csv(OUT/f'publisher_candidates_{source}.csv',index=False)
  con.close();print(source,'summarized',flush=True)
 by=pd.concat(yearly,ignore_index=True);by.to_csv(OUT/'all_by_year.csv',index=False)
 pd.concat(cover,ignore_index=True).to_csv(OUT/'coverage.csv',index=False)
 se=pd.concat(sens,ignore_index=True);se.to_csv(OUT/'sensitivity_by_year.csv',index=False)
 pd.concat(context,ignore_index=True).to_csv(OUT/'amazon_and_nz_prefix_context.csv',index=False)
 pd.DataFrame(totals).to_csv(OUT/'source_totals.csv',index=False)
 trends=[]
 for source,(lo,hi) in WINDOWS.items():
  for variant in se.variant.unique():
   v=se[(se.source==source)&(se.variant==variant)&se.pub_year.between(lo,hi)].sort_values('pub_year')
   early=v[v.pub_year.between(lo,lo+2)];late=v[v.pub_year.between(hi-2,hi)]
   e=early.self_published.sum()/early.print_isbns.sum();l=late.self_published.sum()/late.print_isbns.sum()
   trends.append(dict(source=source,variant=variant,start_year=lo,end_year=hi,slope_pp_per_year=np.polyfit(v.pub_year,v.share*100,1)[0],early_pooled_share=e,late_pooled_share=l,change_pp=(l-e)*100,early_n=early.print_isbns.sum(),late_n=late.print_isbns.sum()))
 # UK extension and common four-country short window are clearly secondary.
 for source,lo,hi,label in [('uk',1995,2017,'UK_NZ_extension'),('nz',1995,2017,'UK_NZ_extension')]+[(s,2010,2013,'common_2010_2013') for s in WINDOWS]+[(s,2010,2018,'fr_qc_both_free_2010_2018') for s in ('fr','qc')]+[(s,2018,2021,'fr_fee_era_2018_2021') for s in ('fr','qc')]+[(s,2005,2011,'uk_nz_2005_2011') for s in ('uk','nz')]:
  v=by[(by.source==source)&by.pub_year.between(lo,hi)];early=v[v.pub_year==lo];late=v[v.pub_year==hi]
  e=early.self_published.sum()/early.print_isbns.sum();l=late.self_published.sum()/late.print_isbns.sum()
  trends.append(dict(source=source,variant=label,start_year=lo,end_year=hi,slope_pp_per_year=np.polyfit(v.pub_year,v.share*100,1)[0],early_pooled_share=e,late_pooled_share=l,change_pp=(l-e)*100,early_n=early.print_isbns.sum(),late_n=late.print_isbns.sum()))
 pd.DataFrame(trends).to_csv(OUT/'trends_and_early_late.csv',index=False)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
 for name,sources in [('uk_nz',['uk','nz']),('fr_qc',['fr','qc'])]:
  v=by[by.source.isin(sources)&by.main_window];v.to_csv(OUT/f'{name}_by_year.csv',index=False)
  fig,ax=plt.subplots(figsize=(10,5.7))
  for s,color in zip(sources,['#245a9b','#bd4d30']):
   d=v[v.source==s];ax.plot(d.pub_year,d.share*100,label=LABELS[s],color=color,lw=2.3,marker='o',ms=3)
   ax.fill_between(d.pub_year.to_numpy(),(d.wilson_low*100).to_numpy(),(d.wilson_high*100).to_numpy(),alpha=.12,color=color)
  ax.set(ylabel='Flagged self-published print ISBNs (%)',xlabel='Publication year',title='Observed national-bibliography shares: '+ ' vs '.join(LABELS[s] for s in sources));ax.legend(frameon=False);ax.grid(axis='y',alpha=.2)
  if name=='fr_qc':ax.axvline(2018.8,color='#777777',ls='--',lw=1)
  note='Author = publisher OR documented self-publishing service. Shading: nominal 95% Wilson intervals.\nCatalogue coverage and classification uncertainty are not included.'
  if name=='fr_qc':note+='\nAFNIL ISBNs were free until March 2019 (dashed line): both places were free before then. France 2022 excluded as incomplete.'
  fig.text(.10,.02,note,fontsize=8,color='#444444');fig.tight_layout(rect=[0,.10,1,1]);fig.savefig(OUT/f'figures/{name}_shares.png');fig.savefig(OUT/f'figures/{name}_shares.svg');plt.close(fig)
 fig,axs=plt.subplots(2,2,figsize=(11,7))
 for ax,s in zip(axs.ravel(),WINDOWS):
  for variant,label in [('main','Main'),('author_only','Author = publisher'),('author_plus_platform','Author + platform'),('include_mixed_contract_imprints','Including mixed contracts')]:
   lo,hi=WINDOWS[s];d=se[(se.source==s)&(se.variant==variant)&se.pub_year.between(lo,hi)];ax.plot(d.pub_year,d.share*100,label=label)
  ax.set_title(LABELS[s]);ax.set_ylabel('Share (%)');ax.grid(alpha=.15)
 axs[0,0].legend(fontsize=8,frameon=False);fig.tight_layout();fig.savefig(OUT/'figures/sensitivity.png');plt.close(fig)
 print('Analysis outputs complete',flush=True)
if __name__=='__main__':main()
