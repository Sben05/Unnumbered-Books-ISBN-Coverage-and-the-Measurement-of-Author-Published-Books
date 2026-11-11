"""Exploratory cross-section: single-ISBN price faced by an individual author vs recorded author=publisher (AP) print ISBNs per million and AP share.
Each country uses its own national bibliography and its own AP rule; windows differ (UK coverage collapses after 2014). NOT causal; levels not strictly comparable."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pop=pd.concat([pd.read_csv('config/population_official.csv'),pd.read_csv('config/population_extra.csv')]).drop_duplicates(['iso3','year']).set_index(['iso3','year']).population
rows=[]
a=pd.read_csv('output/selfpub/all_by_year.csv')
for src,iso,(y0,y1) in [('nz','NZL',(2015,2019)),('qc','CAN_QC',(2015,2019)),('fr','FRA',(2015,2018)),('uk','GBR',(2010,2014))]:
    s=a[(a.source==src)&a.pub_year.between(y0,y1)]; rows.append(dict(country=src.upper(),window=f'{y0}-{y1}',ap=s.author_is_publisher.sum(),isbns=s.print_isbns.sum(),popm=sum(pop[(iso,y)] for y in range(y0,y1+1))/1e6))
es=pd.read_csv('output/spain/es_by_year.csv'); s=es[es.pub_year.between(2015,2019)]; rows.append(dict(country='ES',window='2015-2019',ap=s.ap.sum(),isbns=s.print_isbns.sum(),popm=sum(pop[('ESP',y)] for y in range(2015,2020))/1e6))
pt=pd.read_csv('output/portugal/pt_ap_consistent_by_year.csv'); s=pt[pt.pub_year.between(2015,2019)]; rows.append(dict(country='PT',window='2015-2019',ap=s.ap_consistent.sum(),isbns=s.print_isbns.sum(),popm=sum(pop[('PRT',y)] for y in range(2015,2020))/1e6))
de=pd.read_csv('output/germany/de_by_year.csv'); s=de[de.year.between(2015,2019)]; rows.append(dict(country='DE',window='2015-2019',ap=s.ap.sum(),isbns=s.isbns.sum(),popm=sum(pop[('DEU',y)] for y in range(2015,2020))/1e6))
for c,iso,f,(y0,y1) in [('PL','POL','output/poland/pl_by_year.csv',(2015,2019)),('EE','EST','output/estonia/ee_by_year.csv',(2015,2019)),('LV','LVA','output/latvia/lv_by_year.csv',(2015,2019))]:
    x=pd.read_csv(f); s=x[x.pub_year.between(y0,y1)]; rows.append(dict(country=c,window=f'{y0}-{y1}',ap=s.ap_consistent.sum(),isbns=s.print_isbns.sum(),popm=sum(pop[(iso,y)] for y in range(y0,y1+1))/1e6))
D=pd.DataFrame(rows)
price={'NZ':(0,'free (National Library)'),'QC':(0,'free (BAnQ)'),'FR':(0,'free until Mar 2019'),'PL':(0,'free'),'EE':(0,'free'),'LV':(2.85,'nominal EUR 2.85'),
       'PT':(15,'EUR 15 + VAT (2015-)'),'ES':(45,'EUR 45 (undated tariff)'),'DE':(70,'EUR 70 (2022-24; earlier unknown)'),'UK':(110,'GBP 89-99 (observed 2016+)')}
D['price_eur']=D.country.map(lambda c:price[c][0]); D['price_note']=D.country.map(lambda c:price[c][1])
D['ap_per_million_yr']=D.ap/D.popm; D['ap_share_pct']=100*D.ap/D.isbns
D=D.sort_values('price_eur'); print(D.round(2).to_string(index=False)); D.to_csv('output/paper_pt/intl_crosssection.csv',index=False)
print('Spearman price vs AP/million: %.2f ; vs AP share: %.2f'%(D.price_eur.corr(D.ap_per_million_yr,method='spearman'),D.price_eur.corr(D.ap_share_pct,method='spearman')))
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
for a_,col,lab in [(ax[0],'ap_per_million_yr','AP print ISBN books per million residents per year'),(ax[1],'ap_share_pct','AP share of print ISBNs (%)')]:
    a_.scatter(D.price_eur,D[col],s=50,c='#2c7fb8')
    for _,r in D.iterrows(): a_.annotate(f"{r.country} ({r.window})",(r.price_eur,r[col]),xytext=(4,4),textcoords='offset points',fontsize=8)
    a_.set_yscale('log'); a_.set_xlabel('single ISBN price for an individual author (EUR, approx.)'); a_.set_ylabel(lab)
fig.suptitle('Exploratory: ISBN price vs recorded self-publishing (own national bibliography and AP rule per country; not causal)',fontsize=10)
plt.tight_layout(); plt.savefig('output/paper_pt/fig_intl_crosssection.png',dpi=150)
