"""Platform-issued identifiers in national bibliographies: books whose ISBN is Amazon-issued (979-8 prefix, introduced by Amazon KDP ~2020)
or whose imprint is CreateSpace / 'Independently published'. Per country-year: platform books per 1,000 ISBN books; platform share of self-published (AP or platform) books.
Also the Amazon marketplace sample (Amazon Reviews 2023 metadata) as the global reference."""
import duckdb, pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
c=duckdb.connect(); rows=[]
apcol={'pt':'ap_consistent','pl':'ap_consistent','ee':'ap_consistent','lv':'ap_consistent','de':'ap_consistent'}
for f in ['uk','us','nz','qc','fr','de','es','pt','pl','ee','lv','no']:
    ap=apcol.get(f,'author_is_publisher')
    d=c.execute(f"""select pub_year y, count(*) n, sum((isbn13 like '9798%' or amazon_imprint)::int) platform, sum((isbn13 like '9798%')::int) p9798,
        sum({ap}::int) ap from 'data/interim/{f}_classified.parquet' where pub_year between 2008 and 2022 group by 1 order by 1""").df()
    d['country']=f.upper(); rows.append(d)
P=pd.concat(rows); P['platform_per_1000']=1000*P.platform/P.n; P['platform_share_of_selfpub']=P.platform/(P.ap+P.platform)
P.to_csv('output/paper_pt/platform_isbn_by_country_year.csv',index=False)
pd.set_option('display.width',220)
print(P.pivot(index='y',columns='country',values='platform_per_1000').loc[2010:2022].round(1).to_string())
print(P.pivot(index='y',columns='country',values='platform').loc[2016:2022].fillna(0).astype(int).to_string())
a=c.execute("select pub_year y, count(*) n, sum(amazon_imprint::int) amz, sum((isbn13 like '9798%')::int) p9798 from 'data/interim/amz_classified.parquet' where pub_year between 2005 and 2022 group by 1 order by 1").df()
a['amazon_issued_share']=(a.amz+a.p9798)/a.n; print(a.round(3).to_string(index=False)); a.to_csv('output/paper_pt/amazon_marketplace_platform_share.csv',index=False)
fig,ax=plt.subplots(figsize=(9,4.5))
for cc in ['FR','DE','UK','ES','PT','NZ','QC','PL','EE']:
    s=P[P.country==cc].set_index('y').platform_per_1000.loc[2012:2022]; ax.plot(s.index,s,marker='o',ms=3,label=cc,lw=2.2 if cc=='FR' else 1.2)
ax.axvline(2019.2,c='#c0392b',ls=':',lw=1); ax.text(2019.3,ax.get_ylim()[1]*0.9,'FR fee (Mar 2019)',fontsize=8,color='#c0392b')
ax.set_ylabel('platform-issued ISBN books per 1,000 ISBN books'); ax.set_title('Amazon-issued identifiers recorded in national bibliographies'); ax.legend(fontsize=8,ncol=3)
plt.tight_layout(); plt.savefig('output/paper_pt/fig_platform_isbn.png',dpi=150)
