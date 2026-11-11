from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent.parent;O=ROOT/'output/selfpub'
(ROOT/'archive/drafts').mkdir(parents=True,exist_ok=True)
def tbl(df):
    df=df.copy()
    for c in df.columns:
        if df[c].dtype.kind=='f':df[c]=df[c].map(lambda v:'' if pd.isna(v) else f'{v:.4f}')
    return '| '+' | '.join(map(str,df.columns))+' |\n|'+'---|'*len(df.columns)+'\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in df.itertuples(index=False))+'\n'
b=pd.read_csv(O/'all_by_year.csv');P=pd.read_csv(O/'panel.csv');S=pd.read_csv(O/'sensitivity_by_year.csv')
F=['# FIGURE_DATA: values behind each figure\n']
d=b[((b.source.isin(['uk','nz']))&b.pub_year.between(1995,2014))][['source','pub_year','print_isbns','self_published','share','wilson_low','wilson_high']];F+=['## uk_nz_shares.png (combined share = AP OR service; denominator = print ISBNs)\n',tbl(d.sort_values(['source','pub_year']))]
d=b[((b.source.isin(['fr','qc']))&b.pub_year.between(2010,2021))][['source','pub_year','print_isbns','self_published','share','wilson_low','wilson_high']];F+=['## fr_qc_shares.png (France 2010–2021; Québec 2010–2021)\n',tbl(d.sort_values(['source','pub_year']))]
W={'uk':(1995,2014),'nz':(1995,2014),'fr':(2010,2021),'qc':(2010,2021)};r=[]
for s,(lo,hi) in W.items():
    v=S[(S.source==s)&S.variant.isin(['main','author_only','author_plus_platform','include_mixed_contract_imprints'])&S.pub_year.between(lo,hi)];r.append(v[['source','variant','pub_year','print_isbns','self_published','share']])
F+=['## sensitivity.png (four variants per country)\n',tbl(pd.concat(r).sort_values(['source','variant','pub_year']))]
W2={'nz':(1995,2022),'uk':(1995,2014),'us':(1995,2011),'fr':(2005,2021),'qc':(2010,2021)};r=[]
for s,(lo,hi) in W2.items():
    v=P[(P.source==s)&P.pub_year.between(lo,hi)][['source','pub_year','n','ap']].copy();v['ap_share']=v.ap/v.n;r.append(v.rename(columns={'n':'print_isbns','ap':'author_is_publisher'}))
F+=['## ap_share_all.png (AP = author=publisher, NOT Amazon Publishing; US = Library of Congress)\n',tbl(pd.concat(r))]
a=P[(P.source=='amz')&P.pub_year.between(2000,2022)][['pub_year','n','amazon_imprint','i9798','sp']].rename(columns={'n':'amazon_sample_print_isbns','amazon_imprint':'createspace_or_independently_published','i9798':'isbn_979_8','sp':'self_published_combined'})
F+=['## amazon_timeline.png left panel + amazon_vs_bowker.png (Amazon sample)\n',tbl(a.assign(combined_share=a.self_published_combined/a.amazon_sample_print_isbns)),'Bowker points plotted: 2007 = 11%, 2012 = 40% (published figures only; no series).\n']
(O/'FIGURE_DATA.md').write_text('\n'.join(F))
core=['# REVIEW BUNDLE (core)\n']+[Path(ROOT/p).read_text() for p in ['archive/research-notes/METHODS.md','archive/research-notes/docs/MODEL_SPECS.md']]
R=(ROOT/'archive/research-notes/RESULTS.md').read_text();i=R.index('## C7.');j=R.index('## C11.')
core+=['\n# Part B audit tables (from RESULTS.md C7–C10)\n',R[i:j],'\n',(O/'FIGURE_DATA.md').read_text()]
(ROOT/'archive/drafts/REVIEW_BUNDLE_core.md').write_text('\n'.join(core))
(ROOT/'archive/drafts/REVIEW_BUNDLE_full.md').write_text('\n'.join(core)+'\n\n# FULL RESULTS.md\n\n'+R)
for f in ['REVIEW_BUNDLE_core.md','REVIEW_BUNDLE_full.md']:print(f,(ROOT/'archive/drafts'/f).stat().st_size//1024,'KB')
