"""Sequential serial numbers inside 978-989-20-NNNN-C as an agency-assignment-rate proxy (assumes sequential allocation after 2006 per APEL report fn.18)."""
import duckdb, pandas as pd, numpy as np
c=duckdb.connect(); P="data/interim/pt_classified.parquet"
d=c.execute(f"select pub_year y, cat_year, substr(isbn13,9,4)::int s, ap_consistent ap, isbn13 from '{P}' where isbn13 like '97898920%' and pub_year between 2006 and 2020").df()
g=d.groupby('y').s.agg(['count','min','median','max',lambda x:x.quantile(.9),lambda x:x.quantile(.1)]); g.columns=['n','min','med','max','q90','q10']
g['d_med']=g.med.diff(); g['d_q90']=g.q90.diff(); g['d_q10']=g.q10.diff()
print(g.round(0).to_string())
# robust slope of serial on pub_year for windows
for lo,hi in [(2010,2014),(2011,2014),(2015,2018),(2016,2019)]:
    s=d[(d.y>=lo)&(d.y<=hi)]; b=np.polyfit(s.y,s.s,1); print(lo,hi,'OLS slope serial/yr',round(b[0],0),'n',len(s))
# same by catalogue year
d2=d.groupby('cat_year').s.median().diff(); print(d2.dropna().round(0).to_dict())
g.to_csv('output/paper_pt/audit_9892_serial_quantiles.csv')
# cumulative allocated by Jan 2014 per APEL report: 3,692 'ISBN atribuídos a autores-editores até 2013' (Listagem de prefixos, Jan 2014)
mx=c.execute(f"select max(substr(isbn13,9,4)::int) from '{P}' where isbn13 like '97898920%' and pub_year<=2013").fetchone(); print('max serial seen in books pub<=2013:',mx)
