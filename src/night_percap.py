import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('src/night_events.py').read().split("# FR is free")[0])
pop=pd.read_csv('config/population_official.csv'); m={'uk':'GBR','nz':'NZL','fr':'FRA','qc':'CAN_QC','es':'ESP','pt':'PRT'}
cnt={s:(a[a.source==s].set_index('pub_year').author_is_publisher) for s in ['uk','nz','fr','qc']}
cnt['es']=es.ap; cnt['pt']=pt.ap_consistent
rows=[]
for s,c in cnt.items():
    p=pop[pop.iso3==m[s]].set_index('year').population
    for y,v in c.items():
        if y in p.index and 2005<=y<=2021: rows.append(dict(country=s,year=y,ap_isbns=v,per_million=v/(p[y]/1e6)))
d=pd.DataFrame(rows); d.to_csv('output/night/ap_per_million_official_pop.csv',index=False)
t=d.pivot(index='year',columns='country',values='per_million'); print(t.round(0).to_string())
t.plot(figsize=(8,4.5),logy=True,marker='o',ms=3); plt.ylabel('AP ISBNs per million (log)'); plt.title('Author=publisher ISBNs per million, official population')
for y,l in [(2012,'ES fee'),(2015,'PT fee'),(2019,'FR fee')]: plt.axvline(y,ls=':',c='grey')
plt.tight_layout(); plt.savefig('output/night/ap_per_million.png',dpi=150)
