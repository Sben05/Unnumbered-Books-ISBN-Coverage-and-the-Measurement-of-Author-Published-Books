"""Country-year panel from classified parquet files; counts only (no model)."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import duckdb,pandas as pd
rows=[]
for s in ['uk','nz','fr','qc','us','amz']:
    c=duckdb.connect()
    d=c.execute(f"""SELECT '{s}' AS source,pub_year,count(*) n,sum(self_pub::INT) sp,sum(author_is_publisher::INT) ap,sum(service_imprint::INT) svc,
     sum(service_platform::INT) platform,sum(service_author_services::INT) auth_svc,sum(service_vanity::INT) vanity,
     sum((service_imprint AND NOT author_is_publisher)::INT) svc_only,sum(amazon_imprint::INT) amazon_imprint,sum(us_9798::INT) i9798,
     sum(nz_pool::INT) nz_pool,sum(corporate_self::INT) corporate_self,sum(government::INT) government
     FROM read_parquet('{ROOT}/data/interim/{s}_classified.parquet') WHERE pub_year BETWEEN 1995 AND 2022 GROUP BY 1,2 ORDER BY 2""").df()
    rows.append(d)
p=pd.concat(rows);p.to_csv(ROOT/'output/selfpub/panel.csv',index=False);print(p.groupby('source').n.sum())
