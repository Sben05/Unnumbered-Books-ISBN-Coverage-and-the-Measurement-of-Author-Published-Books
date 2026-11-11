"""Convert amazon_books.parquet to study schema as source 'amz' (Amazon marketplace catalogue; print formats only)."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import duckdb
from study_common import SCHEMA
con=duckdb.connect()
con.execute(f"""COPY (SELECT 'amz' AS source,parent_asin record_id,'xx' country_code,coalesce(title,'') title,'' place,'a' record_type,'m' bib_level,'print' carrier,coalesce(language,'') AS language,'' physical_description,'' edition,'' AS notes,'Amazon details keys' format_evidence,
 CASE WHEN author IS NULL OR author='' THEN []::VARCHAR[] ELSE [author] END authors_personal,[]::VARCHAR[] contributors_personal,[]::VARCHAR[] authors_corporate,
 CASE WHEN publisher IS NULL OR publisher='' THEN []::VARCHAR[] ELSE [publisher] END publishers,[isbn13] isbn13s,['']::VARCHAR[] isbn_qualifiers,
 has_print_format AND NOT has_kindle_fields is_print,true country_eligible,true is_published,false role_uncertain,pub_year::INT pub_year
 FROM read_parquet('{ROOT}/data/interim/amazon_books.parquet') WHERE length(isbn13)=13 AND isbn13 SIMILAR TO '97[89][0-9]{{10}}') TO '{ROOT}/data/interim/amz_catalogue.parquet' (FORMAT parquet,COMPRESSION zstd)""")
print(con.execute(f"select count(*),sum(is_print::int) from read_parquet('{ROOT}/data/interim/amz_catalogue.parquet')").fetchall())
