"""Assemble RESULTS.md: narrative (REPORT.md + ECON_RESULTS.md) plus every results table generated from output/selfpub/*.csv."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent.parent;O=ROOT/'output/selfpub'
def md(df,fmt=None):
    df=df.copy()
    for c in df.columns:
        if df[c].dtype.kind=='f':df[c]=df[c].map(lambda v:'' if pd.isna(v) else (f'{v:.4f}' if abs(v)<10 else f'{v:,.1f}'))
    return '| '+' | '.join(map(str,df.columns))+' |\n|'+'---|'*len(df.columns)+'\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in df.itertuples(index=False))+'\n'
def body(p,drop_h1=True):
    t=(ROOT/p).read_text().split('\n');return '\n'.join(t[1:] if drop_h1 else t).replace('\n## ','\n### ').replace('\n### ','\n### ')
L=[]
L.append('# RESULTS: self-publishing and ISBN cost (UK, NZ, France, Québec, US)\n')
L.append('Everything in one place. Part A: UK/NZ and France/Québec headline study. Part B: US, Amazon and econometric tests. Part C: all year-by-year tables, sensitivity checks, coverage, validation. Definitions, sources and known biases: [METHODS.md](METHODS.md). Descriptive only; no causal claims beyond what Part B states.\n')
L.append('## Figures\n')
for f in ['uk_nz_shares','fr_qc_shares','sensitivity','ap_share_all','amazon_timeline','amazon_vs_bowker','frqc_parallel_trends','per_capita_ap']:
    L.append(f'![{f}](output/selfpub/figures/{f}.png)\n')
L.append('\n# Part A. UK vs NZ and France vs Québec\n');L.append(body('archive/research-notes/docs/REPORT.md'))
L.append('\n# Part B. US, Amazon and econometric tests\n');L.append(body('archive/research-notes/docs/ECON_RESULTS.md'))
L.append('\n# Part C. Tables\n')
b=pd.read_csv(O/'all_by_year.csv')
L.append('## C1. Print ISBNs and self-published shares by year (all sources, full classified range)\n\nColumns: share = (author=publisher OR service)/print ISBNs; ap = author=publisher; svc = service imprint; corp = corporate author=publisher (not counted); window = inside the main window.\n')
for s,name in [('uk','United Kingdom (BNB, May 2018 snapshot; 2015+ incomplete)'),('nz','New Zealand'),('fr','France (2022 incomplete)'),('qc','Québec (2010+)')]:
    d=b[(b.source==s)&(b.pub_year>=1995)][['pub_year','print_isbns','self_published','share','wilson_low','wilson_high','author_is_publisher','service_imprint','corporate_self','unidentified_publisher','main_window']].copy()
    d['pub_year']=d.pub_year.astype(int);L.append(f'### {name}\n');L.append(md(d))
P=pd.read_csv(O/'panel.csv')
for s,name in [('us','US, Library of Congress (window 1995–2011; later years truncated)'),('amz','Amazon marketplace sample (print ISBNs, all countries, US-centred)')]:
    d=P[(P.source==s)][['pub_year','n','sp','ap','svc','platform','amazon_imprint','i9798']].copy();d['share']=d.sp/d.n;d['pub_year']=d.pub_year.astype(int)
    L.append(f'### {name}\n');L.append(md(d.rename(columns={'n':'print_isbns','sp':'self_published','ap':'author_is_publisher','svc':'service_imprint','platform':'service_platform'})))
L.append('## C2. Trends and early/late changes (all variants)\n');t=pd.read_csv(O/'trends_and_early_late.csv');L.append(md(t))
L.append('## C3. Sensitivity checks, pooled over each main window\n\nWindows: UK/NZ 1995–2014; FR/QC 2010–2021.\n')
s=pd.read_csv(O/'sensitivity_by_year.csv');W={'uk':(1995,2014),'nz':(1995,2014),'fr':(2010,2021),'qc':(2010,2021)}
rows=[]
for src,(lo,hi) in W.items():
    v=s[(s.source==src)&s.pub_year.between(lo,hi)].groupby('variant')[['self_published','print_isbns']].sum();v['share']=v.self_published/v.print_isbns;v['source']=src;rows.append(v.reset_index())
R=pd.concat(rows);L.append(md(R.pivot(index='variant',columns='source',values='share').reset_index()))
L.append('Full year-by-year sensitivity series: `output/selfpub/sensitivity_by_year.csv`.\n')
L.append('## C4. Coverage and quality (selected columns)\n');c=pd.read_csv(O/'coverage.csv')
cc=c[c.pub_year.between(1995,2022)][['source','pub_year','total_records','country_print_records','valid_isbn_share_country_print','publisher_share_country_print','personal_author_share_country_print','raw_isbn_occurrences','duplicate_isbn_occurrences','completeness_status']].copy();cc['pub_year']=cc.pub_year.astype(int);L.append(md(cc))
L.append('## C5. Amazon-issued ISBNs, 979-8 and NZ pool context\n');L.append(md(pd.read_csv(O/'amazon_and_nz_prefix_context.csv')))
L.append('## C6. Amazon-issued ISBNs: Amazon sample vs national bibliographies\n');L.append(md(pd.read_csv(O/'amazon_issued_capture.csv')))
L.append('## C7. Unknown-breakpoint tests (sup-F, bootstrap p)\n');L.append(md(pd.read_csv(O/'break_tests.csv')))
L.append('## C8. NZ minus UK interrupted time series on the log-odds gap\n');L.append(md(pd.read_csv(O/'nz_uk_its.csv')))
L.append('## C9. Pooled difference-in-differences around 2007/08\n');L.append(md(pd.read_csv(O/'did_amazon_era.csv')))
L.append('## C10. France vs Québec: parallel trends and post-2019 tests\n');L.append(md(pd.read_csv(O/'frqc_parallel_trends_did.csv')))
g=pd.read_csv(O/'frqc_gap_series.csv');gg=g.pivot(index='pub_year',columns='outcome',values='gap').reset_index();gg.columns=['pub_year']+['gap_logodds_'+c for c in gg.columns[1:]];L.append('### Yearly France−Québec log-odds gap\n');L.append(md(gg.replace([float('inf')],float('nan'))))
L.append('### Author=publisher entry in France and Québec\n');L.append(md(pd.read_csv(O/'frqc_author_publisher_entry.csv').query('pub_year>=2010')))
L.append('## C11. Per-capita author=publisher rates\n');pc=pd.read_csv(O/'per_capita.csv');L.append(md(pc.pivot(index='pub_year',columns='source',values='ap_per_m').reset_index()))
L.append('## C12. Author=publisher entry, NZ/UK/US(LoC)\n');L.append(md(pd.read_csv(O/'ap_entry_nz_uk_us.csv').query('pub_year>=2000')))
L.append('## C13. BnF official benchmark vs our France series\n')
o=pd.read_csv(O/'bnf_official_benchmarks.csv')[['year','author_depositor_books','total_deposited_books','share']].rename(columns={'share':'bnf_author_depositor_share'})
f=b[b.source=='fr'][['pub_year','print_isbns','author_is_publisher','self_published']].copy();f['our_ap_share']=f.author_is_publisher/f.print_isbns;f['our_combined_share']=f.self_published/f.print_isbns
m=f.merge(o,left_on='pub_year',right_on='year');L.append(md(m[['pub_year','bnf_author_depositor_share','our_ap_share','our_combined_share']]));L.append('Correlation 2009–2020: AP vs BnF 0.96; combined vs BnF 0.65.\n')
L.append('## C14. Validation\n\nRecord-only read of 25 flagged and 25 unflagged ISBNs per source (not independent, no web lookups): flagged — no clear false positives, about 5 borderline sole-trader/company imprints; unflagged — UK/FR almost all real publishers, NZ/QC a few likely misses (pseudonyms, small imprints). Full 200+200 samples with blank gold-label columns: `output/selfpub/validation_{uk,nz,fr,qc}.csv`. NZ pool check: flag rate inside the 978-0-473/978-1-06 pool is 27–38%, outside 2–7%.\n')
L.append('## C15. Source totals\n');L.append(md(pd.read_csv(O/'source_totals.csv')))
L.append('## C16. File index\n\nAll under `output/selfpub/`: all_by_year, uk_nz_by_year, fr_qc_by_year, sensitivity_by_year, trends_and_early_late, coverage, amazon_and_nz_prefix_context, amazon_issued_capture, break_tests, nz_uk_its, did_amazon_era, frqc_parallel_trends_did, frqc_gap_series, frqc_author_publisher_entry, per_capita, panel, ap_entry_nz_uk_us, uk_service_place_sensitivity, bnf_official_benchmarks, publisher_candidates_*, duplicates_*, validation_*, figures/*.\n')
(ROOT/'archive/research-notes/RESULTS.md').write_text('\n'.join(L))
print(len('\n'.join(L)))
