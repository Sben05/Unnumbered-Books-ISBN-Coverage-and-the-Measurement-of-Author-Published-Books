"""PHASE 1 audit: Portugal AP name-match series vs agency-defined author-edition prefix 978-989-20 (and 989-33), same sample.
Sample = data/interim/pt_classified.parquet (one row per unique valid print ISBN-13, BNP records, publication year)."""
import duckdb, numpy as np, pandas as pd
c=duckdb.connect(); P="data/interim/pt_classified.parquet"
q=f"""select pub_year y, count(*) n,
 sum(author_is_publisher::int) ap_orig, sum(ap_consistent::int) ap_cons, sum(ap_pure::int) ap_pure,
 sum((isbn13 like '97898920%')::int) p9892, sum((isbn13 like '97898933%')::int) p9893,
 sum((isbn13 like '97898920%' and ap_consistent)::int) both_cons, sum((isbn13 like '97898920%' and author_is_publisher)::int) both_orig,
 sum((isbn13 like '97898920%' and service_imprint)::int) p9892_service,
 sum((isbn13 like '97898920%' and corporate_self)::int) p9892_corp,
 sum((isbn13 like '97898920%' and unidentified_publisher)::int) p9892_nopub,
 sum((isbn13 like '97898920%' and government)::int) p9892_gov,
 sum((isbn13 like '9789892%' and not isbn13 like '97898920%')::int) p98929_other,
 sum((isbn_group like '978-972/989%')::int) n_pt_prefix
 from '{P}' where pub_year between 2005 and 2024 group by 1 order by 1"""
a=c.execute(q).df()
nn=c.execute("select pub_year y, count(*) n_noisbn, sum(ap_consistent::int) noisbn_ap_cons, sum(author_is_publisher::int) noisbn_ap_orig from 'data/interim/pt_noisbn.parquet' where pub_year between 2005 and 2024 group by 1 order by 1").df()
nn['y']=nn.y.astype(int); a=a.merge(nn,on='y',how='left')
a['total_print_records']=a.n+a.n_noisbn
for k in ['ap_orig','ap_cons','p9892','both_cons']: a['sh_'+k]=a[k]/a.n
a['p9892_not_ap']=a.p9892-a.both_cons; a['ap_not_p9892']=a.ap_cons-a.both_cons
a['ap_cons_share_of_p9892']=a.both_cons/a.p9892; a['p9892_share_of_ap_cons']=a.both_cons/a.ap_cons
a['ap_incl_noisbn']=a.ap_cons+a.noisbn_ap_cons
for k in ['ap_orig','ap_cons','p9892','n']: a['yoy_'+k]=a[k].pct_change()
a.to_csv('output/paper_pt/audit_annual_series.csv',index=False)
pd.set_option('display.width',250)
print(a[['y','n','ap_orig','ap_cons','p9892','p9893','both_cons','p9892_not_ap','ap_not_p9892','p9892_service','p9892_corp','p9892_nopub','n_noisbn','noisbn_ap_cons']].to_string(index=False))
print(a[['y','sh_ap_cons','sh_p9892','yoy_ap_cons','yoy_p9892','ap_cons_share_of_p9892','p9892_share_of_ap_cons']].round(4).to_string(index=False))
# catalogue-year variant for 98920
d=c.execute(f"select cat_year, count(*) n, sum((isbn13 like '97898920%')::int) p9892 from '{P}' where cat_year between 2010 and 2019 group by 1 order by 1").df(); print(d)
d.to_csv('output/paper_pt/audit_p9892_by_catalogue_year.csv',index=False)
# previously-assigned prefixes: a 989-20 ISBN is a NEW prefix each time (one title per prefix). Distinct prefixes (first 12 digits ~ 8-digit title block) are all unique by construction.
# ISBN serial position within 989-20: higher serial = later assignment (sequential allocation) -> infer assignment lag
e=c.execute(f"select pub_year y, min(substr(isbn13,9,4)::int) lo, median(substr(isbn13,9,4)::int) med, max(substr(isbn13,9,4)::int) hi, count(*) n from '{P}' where isbn13 like '97898920%' and pub_year between 2010 and 2019 group by 1 order by 1").df()
print(e)
e.to_csv('output/paper_pt/audit_9892_serial_by_pubyear.csv',index=False)
