"""UK service-imprint counts with and without the UK country filter (AuthorHouse/Xlibris moved their stated place to the US)."""
import sys,csv,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import duckdb
from classify_selfpub import SERVICES,raw_norm
rx=re.compile('|'.join(s['name_pattern'] for s in SERVICES if s['scope']!='mixed'))
rows=duckdb.connect().execute(f"""SELECT pub_year,country_eligible,array_to_string(publishers,'; ') FROM read_parquet('{ROOT}/data/interim/uk_catalogue.parquet')
 WHERE is_print AND is_published AND len(isbn13s)>0 AND pub_year BETWEEN 1995 AND 2016""").fetchall()
total=Counter();any_=Counter();uk=Counter()
for y,e,p in rows:
 total[y]+=1
 if p and rx.search(raw_norm(p)):any_[y]+=1;uk[y]+=bool(e)
with (ROOT/'output/selfpub/uk_service_place_sensitivity.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['pub_year','print_records','service_imprint_any_place','service_imprint_uk_place','share_any_place','share_uk_place'])
 for y in range(1995,2017):w.writerow([y,total[y],any_[y],uk[y],round(any_[y]/total[y],4),round(uk[y]/total[y],4)])
print(open(ROOT/'output/selfpub/uk_service_place_sensitivity.csv').read())
