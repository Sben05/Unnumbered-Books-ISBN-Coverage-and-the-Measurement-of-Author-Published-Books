"""Amazon Reviews 2023 'Books' product metadata -> one row per ISBN-13 with publisher/year/format. Marketplace catalogue, no country."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import duckdb
con=duckdb.connect();con.execute("SET memory_limit='6GB';SET preserve_insertion_order=false")
con.execute(f"""COPY (
WITH r AS (SELECT parent_asin,title,author->>'name' author,store,rating_number,
  details->>'Publisher' publisher_raw,details->>'ISBN 13' isbn13_raw,details->>'Publication date' pubdate_raw,
  details->>'Language' AS lang,
  ((details->>'Paperback') IS NOT NULL OR (details->>'Hardcover') IS NOT NULL OR (details->>'Mass Market Paperback') IS NOT NULL OR (details->>'Board book') IS NOT NULL OR (details->>'Spiral bound') IS NOT NULL) AS has_print_format,
  ((details->>'File size') IS NOT NULL OR (details->>'Print length') IS NOT NULL) AS has_kindle_fields
  FROM read_ndjson('{ROOT}/data/raw/amazon_meta/meta_Books.jsonl',columns={{parent_asin:'VARCHAR',title:'VARCHAR',author:'JSON',store:'VARCHAR',rating_number:'BIGINT',details:'JSON'}},maximum_object_size=67108864,ignore_errors=true))
SELECT parent_asin,title,author,store,rating_number,lang AS language,has_print_format,has_kindle_fields,
  regexp_replace(isbn13_raw,'[^0-9]','','g') isbn13,
  trim(regexp_extract(publisher_raw,'^([^;(]*)',1)) publisher,
  publisher_raw,
  coalesce(try_cast(regexp_extract(publisher_raw,'\\(([^)]*(?:1[89]|20)\\d\\d)\\)',1) AS VARCHAR),'') pubdate_in_publisher,
  try_cast(regexp_extract(coalesce(nullif(regexp_extract(publisher_raw,'\\(([^)]*)\\)\\s*$',1),''),pubdate_raw,''),'((?:1[5-9]|20)\\d\\d)',1) AS INTEGER) pub_year
FROM r) TO '{ROOT}/data/interim/amazon_books.parquet' (FORMAT parquet,COMPRESSION zstd)""")
print(con.execute(f"select count(*),count(isbn13),sum((length(isbn13)=13)::int),count(pub_year),min(pub_year),max(pub_year) from read_parquet('{ROOT}/data/interim/amazon_books.parquet')").fetchall())
