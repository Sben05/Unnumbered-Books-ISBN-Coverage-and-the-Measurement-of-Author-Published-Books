"""ISBN-level rule classification with inspectable reasons and separate service/name flags."""
import sys,re,csv,unicodedata,hashlib,json
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import duckdb,pandas as pd,pyarrow as pa,pyarrow.parquet as pq
from study_common import DIGITAL
@lru_cache(maxsize=200000)
def raw_norm(s):
 s=unicodedata.normalize('NFKD',s or '');s=''.join(c for c in s if not unicodedata.combining(c));s=s.lower().replace('œ','oe').replace('æ','ae')
 return re.sub(r'\s+',' ',re.sub(r'[^\w\s]',' ',s)).strip()

@lru_cache(maxsize=200000)
def norm(s,publisher=False):
 s=unicodedata.normalize('NFKD',s or '');s=''.join(c for c in s if not unicodedata.combining(c));s=s.lower().replace('œ','oe').replace('æ','ae')
 s=re.sub(r'\([^)]*\)',' ',s);s=re.sub(r'\b(?:1[5-9]\d{2}|20\d{2})\b.*','',s)
 s=re.sub(r'\b(author|auteur|auteure|editor|editeur|illustrator|illustrateur|traducteur)\b',' ',s)
 if not publisher and ',' in s:
  a=s.split(',');s=' '.join(a[1:])+' '+a[0]
 s=re.sub(r'[^\w\s]',' ',s)
 if publisher:s=re.sub(r'\b(?:ltd|limited|inc|incorporated|publishing|publications?|pub|press|books?|editions?|edition|publishers?|publ)\b',' ',s)
 return re.sub(r'\s+',' ',s).strip()
def match_name(author,publisher):
 a=norm(author).split();p=norm(publisher,True).split()
 if not a or not p:return ''
 # Single surnames/pseudonyms are too ambiguous for automatic identity inference.
 if len(a)<2:return ''
 if len(p)>=2 and (a==p or a==list(reversed(p)) or sorted(a)==sorted(p)):return 'exact_name'
 # Require all full-name tokens consecutively; never a single surname or initial.
 if all(len(t)>1 for t in a) and (' '+' '.join(a)+' ') in (' '+' '.join(p)+' '):return 'full_name_containment'
 if a[-1] in p and any(t in p for t in ('family','trust','famille')):return 'surname_family_trust'
 # Initials must share surname and compatible given names, with at least one actual initial.
 for pp in (p,list(reversed(p))):
  if len(pp)!=len(a) or len(pp)<2 or a[-1]!=pp[-1] or len(a[-1])<3:continue
  if not any(len(x)==1 or len(y)==1 for x,y in zip(a[:-1],pp[:-1])):continue
  if all(x==y or ((len(x)==1 or len(y)==1) and x[0]==y[0]) for x,y in zip(a[:-1],pp[:-1])):return 'compatible_initials'
 return ''
EXPLICIT=re.compile(r'\b(?:the authors?|published by (?:the )?authors?|self published|l auteur|l auteure|les auteurs|chez l auteur|a compte d auteur|auto edition|autoedition)\b')
GOV=re.compile(r'\b(?:ministry|ministere|gouvernement|government|department|dept|parliament|parlement|council|stationery office|h m s o|hmso|office for national statistics|statistics new zealand|statistique quebec|crown|sante publique|institut national de sante|institut de la statistique|sante et services sociaux)\b')
STANDARDS=re.compile(r'\b(?:standards? (?:new zealand|australia|association)|british standards|bureau de normalisation|afnor|bsi)\b')
with (ROOT/'config/selfpub_services.csv').open() as f:SERVICES=[dict(x,regex=re.compile(x['name_pattern'])) for x in csv.DictReader(f)]
FIELDS=['author_is_publisher','service_imprint','service_platform','service_author_services','service_vanity','service_mixed','self_pub','self_pub_platform_only','corporate_self','government','standards','thesis','reprint_or_new_edition','amazon_imprint','us_9798','nz_pool','contributor_match','initials_match','explicit_author_statement','unidentified_publisher']
def flags(r):
 pubs=list(r['publishers']);authors=list(r['authors_personal']);corp=list(r['authors_corporate']);con=list(r['contributors_personal'])
 pn=[norm(p,True) for p in pubs];pall='; '.join(raw_norm(p) for p in pubs);out={x:False for x in FIELDS};why=[];service_names=[]
 out['unidentified_publisher']=not pn or all(p in ('','s n','sn','publisher not identified') for p in pn)
 out['corporate_self']=any(norm(c,True)==p and len(p)>3 for c in corp for p in pn)
 explicit=bool(EXPLICIT.search(pall));out['explicit_author_statement']=explicit
 # Corporate-only records publishing as 'the author' are institutional self-publication.
 if explicit and (authors or not corp):out['author_is_publisher']=True;why.append('explicit_author_statement')
 elif explicit and corp:out['corporate_self']=True
 for a in authors:
  for p in pubs:
   m=match_name(a,p)
   if m:out['author_is_publisher']=True;why.append(m);out['initials_match']|=m=='compatible_initials'
 out['contributor_match']=any(match_name(a,p) for a in con for p in pubs)
 for s in SERVICES:
  if s.get('sources') and r['source'] not in s['sources'].split(';'):continue
  # Temporal cutoffs are applied only where explicit evidence supports a launch date.
  if r['pub_year'] and (r['pub_year']<int(s['start_year']) or r['pub_year']>int(s['end_year'])):continue
  if s['regex'].search(pall):
   if s['scope']=='mixed':out['service_mixed']=True
   else:out['service_imprint']=True;out['service_'+s['tier']]=True
   service_names.append(s['name_pattern'])
 out['self_pub']=out['author_is_publisher'] or out['service_imprint']
 out['self_pub_platform_only']=out['author_is_publisher'] or out['service_platform']
 out['government']=bool(GOV.search(pall));out['standards']=bool(STANDARDS.search(pall))
 out['thesis']=bool(re.search(r'\bthesis|\btheses|\bdissertation|\bthese\b',norm(r['notes'])))
 out['reprint_or_new_edition']=bool(re.search(r'reprint|reimpr|revised|revue|\b[2-9](?:nd|rd|th|e|eme)?\b|nouvelle ed|new ed',norm(r['edition']+' '+r['notes'])))
 out['amazon_imprint']=bool(re.search(r'\bcreatespace\b|\bcreate space\b|\bbooksurge\b|\bindependently published\b|\bpublication independante\b',pall))
 out['us_9798']=r['isbn13'].startswith('9798') # US registration group, NOT proof of Amazon.
 out['nz_pool']=r['isbn13'].startswith(('9780473','978106'))
 out['classification_reason']=';'.join(sorted(set(why)));out['matched_services']=';'.join(service_names)
 out['title_group']=norm(r['title'])+'|'+ '|'.join(sorted(norm(a) for a in authors))
 return out

def main(sources):
 for source in sources:
  path=ROOT/f'data/interim/{source}_catalogue.parquet'; con=duckdb.connect();con.execute("SET memory_limit='8GB';SET preserve_insertion_order=false")
  # Explode ISBN/qualifier pairs together. Keep source metadata for all valid ISBNs.
  con.execute(f"CREATE TEMP TABLE x AS SELECT * EXCLUDE(isbn13s,isbn_qualifiers),unnest(isbn13s) isbn13,unnest(isbn_qualifiers) isbn_qualifier FROM read_parquet('{path}')")
  con.execute("ALTER TABLE x ADD COLUMN isbn_print BOOLEAN")
  con.execute("UPDATE x SET isbn_print=is_print AND NOT regexp_matches(lower(coalesce(isbn_qualifier,'')), 'e[ -]?book|epub|pdf|kindle|electronic|online|numerique|numérique|audio|microform|microfiche|microfilm')")
  con.execute(f"COPY x TO '{ROOT}/data/interim/{source}_records.parquet' (FORMAT parquet,COMPRESSION zstd)")
  # Prefer geographic, published, print records; prevent digital-only duplicates entering denominator.
  q="""SELECT *,row_number() OVER(PARTITION BY isbn13 ORDER BY country_eligible DESC,is_published DESC,isbn_print DESC,(CASE WHEN len(publishers)>0 THEN 2 ELSE 0 END + CASE WHEN len(authors_personal)>0 THEN 2 ELSE 0 END + CASE WHEN title!='' THEN 1 ELSE 0 END + CASE WHEN pub_year IS NOT NULL THEN 1 ELSE 0 END) DESC,record_id) ranking FROM x"""
  con.execute('CREATE TEMP TABLE ranked AS '+q)
  con.execute(f"COPY (SELECT isbn13,count(*) n,count(DISTINCT pub_year) year_count,count(DISTINCT country_code) country_count FROM x GROUP BY 1 HAVING count(*)>1) TO '{ROOT}/output/selfpub/duplicates_{source}.csv' (HEADER)")
  batches=con.execute('SELECT * EXCLUDE(ranking) FROM ranked WHERE ranking=1 AND country_eligible AND is_published AND isbn_print AND pub_year BETWEEN 1995 AND 2022').fetch_record_batch(10000)
  dest=ROOT/f'data/interim/{source}_classified.parquet';tmp=dest.with_suffix('.parquet.tmp');writer=None;n=0
  for batch in batches:
   rows=batch.to_pylist()
   for r in rows:r.update(flags(r))
   t=pa.Table.from_pylist(rows)
   if writer is None:writer=pq.ParquetWriter(tmp,t.schema,compression='zstd')
   writer.write_table(t);n+=len(rows)
  if writer:writer.close();tmp.replace(dest)
  print(source,n,'classified ISBNs',flush=True);con.close()
if __name__=='__main__':main(sys.argv[1:] or ['nz','uk','fr','qc'])
