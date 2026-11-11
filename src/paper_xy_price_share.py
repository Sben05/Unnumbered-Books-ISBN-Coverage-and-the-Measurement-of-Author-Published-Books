"""X-Y: price of ONE ISBN for an individual author (PPP international $, 2018, VAT incl.) vs share of ISBNs going to author-publishers.
Panel A: CERLALC Tables 4.1/4.3, same definition, avg 2017-19 (Ibero-America). Panel B: national bibliographies (own AP definitions), 2015-19.
Prices from docs/isbn_prices_batchA.csv, batchB.csv (agent research; confidence noted) and docs/FEE_HISTORY.md / primary APEL letter. PPP: World Bank PA.NUS.PPP 2018."""
import numpy as np, pandas as pd, statsmodels.formula.api as smf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
W=pd.read_csv('data/interim/worldbank_panel.csv'); W=W[W.year==2018].set_index('iso3')
ppp=W['PA.NUS.PPP']; gdp=W['NY.GDP.PCAP.PP.CD']; net=W['IT.NET.USER.ZS']
# local price incl. VAT, currency units, year-2018-ish; sources/confidence in notes
P={'ARG':(330,'ARS',None,'CAL online basic 2018 (+one-time ARS 800 author-editor registration)','high'),
   'BOL':(120,'BOB',None,'Camara Dptal del Libro La Paz 2017/18','high'),
   'BRA':(20,'BRL',None,'Biblioteca Nacional 2018 (+one-time BRL 270 registration)','high'),
   'CHL':(9270,'CLP',None,'Camara Chilena del Libro 2018, IVA incl.','high'),
   'COL':(60000,'COP',None,'Camara Colombiana del Libro 2018, IVA incl., non-member','high'),
   'CRI':(0,'CRC',None,'free per CERLALC regional table','medium'),
   'ECU':(20,'USD',None,'Camara Ecuatoriana del Libro 2017/18 (non-member)','high'),
   'SLV':(0,'USD',None,'free by law (Decreto 1074)','high'),
   'GTM':(150,'GTQ',None,'CERLALC table / agency page','medium'),
   'MEX':(216,'MXN',None,'INDAUTOR 2018 (196 in 2016, 233 in 2020)','high'),
   'PAN':(5,'PAB',None,'university procedure doc + 2007 press','medium'),
   'ESP':(45,'EUR',None,'FGEE tariff 2012-2019 incl. VAT','high'),
   'PRT':(15*1.23,'EUR',None,'APEL letter 11 Dec 2014: EUR 15 + 23% VAT','high'),
   'NZL':(0,'NZD',None,'National Library free 2021 terms','medium'),
   'CAN':(0,'CAD',None,'LAC free, Canadian self-publishers qualify','high'),
   'POL':(0,'PLN',None,'BN: ISBN allocation free','medium'),
   'EST':(0,'EUR',None,'National Library free','high'),
   'LVA':(2.85,'EUR',None,'LNB EUR 2.85 per title','high'),
   'FRA':(0,'EUR',None,'AFNIL free until 8 Mar 2019 (EUR 25 HT dossier fee after)','high'),
   'DEU':(90.98,'EUR',None,'MVB single ISBN 2016 incl. VAT','high'),
   'GBR':(89,'GBP',None,'Nielsen 2017 incl. VAT','high'),
   'USA':(125,'USD',None,'Bowker single ISBN 2017/2019 (KDP offers a free ISBN)','high')}
rows=[]
for k,(p,cur,_,note,conf) in P.items():
    rows.append(dict(iso3=k,price_local=p,currency=cur,ppp=ppp.get(k,np.nan),price_ppp_usd=p/ppp[k] if k in ppp.index and not np.isnan(ppp[k]) else np.nan,note=note,confidence=conf,gdp_pc=gdp.get(k),internet=net.get(k)))
X=pd.DataFrame(rows).set_index('iso3')
sh=pd.read_csv('output/paper_pt/cerlalc_author_publisher_share.csv',index_col=0)
iso={'MÉXICO':'MEX','PORTUGAL':'PRT','COSTA RICA':'CRI','BRASIL':'BRA','COLOMBIA':'COL','CHILE':'CHL','GUATEMALA':'GTM','ARGENTINA':'ARG','EL SALVADOR':'SLV','ECUADOR':'ECU','PANAMÁ':'PAN','BOLIVIA':'BOL'}
A=pd.DataFrame({'cerlalc_ap_share_2017_19':{iso[n]:sh.loc[n,'avg_2017_19'] for n in sh.index if n in iso}})
A.loc['ESP','cerlalc_ap_share_2017_19']=np.mean([5094/89962,5326/81228,5635/90073])*100   # Tablas 4.3/4.1
A=A.join(X); A.to_csv('output/paper_pt/xy_panelA_cerlalc.csv'); print(A.round(1).sort_values('price_ppp_usd').to_string())
a=A.dropna(subset=['price_ppp_usd']); print('\nPanel A n=%d Spearman(price, share) = %.2f'%(len(a),a.price_ppp_usd.corr(a.cerlalc_ap_share_2017_19,method='spearman')))
a=a.assign(lgdp=np.log(a.gdp_pc),paid=(a.price_ppp_usd>0).astype(int))
for f in ['cerlalc_ap_share_2017_19 ~ price_ppp_usd','cerlalc_ap_share_2017_19 ~ price_ppp_usd + lgdp','cerlalc_ap_share_2017_19 ~ paid','cerlalc_ap_share_2017_19 ~ paid + lgdp + internet']:
    m=smf.ols(f,data=a.dropna(subset=['lgdp','internet'] if 'lgdp' in f or 'internet' in f else [])).fit(cov_type='HC1'); k=[x for x in m.params.index if x in ('price_ppp_usd','paid')][0]
    print('%-62s coef %.3f (SE %.3f, p=%.2f) n=%d'%(f,m.params[k],m.bse[k],m.pvalues[k],int(m.nobs)))
# Panel B: national bibliographies
B=pd.read_csv('output/paper_pt/intl_crosssection.csv')
m2={'NZ':'NZL','QC':'CAN','FR':'FRA','PL':'POL','EE':'EST','LV':'LVA','PT':'PRT','ES':'ESP','DE':'DEU','UK':'GBR'}
B['iso3']=B.country.map(m2); B=B.merge(X[['price_ppp_usd','confidence']],left_on='iso3',right_index=True,how='left'); B.to_csv('output/paper_pt/xy_panelB_national_bibliographies.csv',index=False)
print('\nPanel B (own AP definitions):'); print(B[['country','window','ap_share_pct','ap_per_million_yr','price_ppp_usd']].round(1).to_string(index=False))
b=B.dropna(subset=['price_ppp_usd']); print('Panel B n=%d Spearman price vs AP share %.2f ; vs per-million %.2f'%(len(b),b.price_ppp_usd.corr(b.ap_share_pct,method='spearman'),b.price_ppp_usd.corr(b.ap_per_million_yr,method='spearman')))
fig,ax=plt.subplots(1,2,figsize=(13,4.8))
a2=A.dropna(subset=['price_ppp_usd']); ax[0].scatter(a2.price_ppp_usd,a2.cerlalc_ap_share_2017_19,c='#2c7fb8',s=45)
for k,r in a2.iterrows(): ax[0].annotate(k,(r.price_ppp_usd,r.cerlalc_ap_share_2017_19),xytext=(4,3),textcoords='offset points',fontsize=8)
ax[0].set_xlabel('price of one ISBN for an individual author (PPP international $, 2018, VAT incl.)'); ax[0].set_ylabel('% of agency ISBNs going to author-publishers, 2017-19'); ax[0].set_title('A. Ibero-America (CERLALC, same definition)',fontsize=10)
ax[1].scatter(b.price_ppp_usd,b.ap_share_pct,c='#c0392b',s=45)
for _,r in b.iterrows(): ax[1].annotate(r.country,(r.price_ppp_usd,r.ap_share_pct),xytext=(4,3),textcoords='offset points',fontsize=8)
ax[1].set_yscale('log'); ax[1].set_xlabel('price of one ISBN for an individual author (PPP $, VAT incl.)'); ax[1].set_ylabel('% of print ISBNs that are author=publisher (national bibliography, own rule)'); ax[1].set_title('B. National bibliographies (definitions differ)',fontsize=10)
plt.tight_layout(); plt.savefig('output/paper_pt/fig_xy_price_share.png',dpi=150)
