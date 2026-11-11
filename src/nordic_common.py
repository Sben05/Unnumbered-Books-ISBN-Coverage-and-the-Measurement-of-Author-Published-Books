"""Shared classification + analysis for the Nordic controls (NO, SE; FI/DK not obtainable).
Reuses classify_selfpub.flags/norm/match_name unmodified; overrides its module-level SERVICES and EXPLICIT at run time only (no file edits)."""
import sys,re,csv,math,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import duckdb,numpy as np,pandas as pd,pyarrow as pa,pyarrow.parquet as pq
import classify_selfpub as cs
NORDIC_EXPLICIT=r'omakustanne|omakustanteena|forfattarens forlag|forfattarens eget forlag|forfattaren sjalv|forfattare sjalv|utgiven av forfattaren|egen utgivning|egenutgivning|eget forlag|pa eget forlag|eget forlag|egna forlag|forfatterens eget forlag|forfatterens forlag|forfatteren selv|udgivet af forfatteren|pa forfatterens forlag|selvudgivelse|selvudgivet|selvforlag|selvutgitt|selvutgivelse|forfatterforlag|forfatterutgitt|forfatteren|forfattaren|forfatter|utgitt av forfatteren|utgitt av forfatteren selv|pa egen bekostning|pa eget forlag'
class _Expl:
 def __init__(s):s.old=cs.EXPLICIT;s.new=re.compile(r'(?<![a-z])(?:'+NORDIC_EXPLICIT+r')(?![a-z])')
 def search(s,t):return s.old.search(t) or s.new.search(t)
UNID=re.compile(r'^(?:utan forlag|uten forlag|uden forlag|s n|sn|utan uppgift|uten opplysninger)$')
def load_services(cc):
 rows=[]
 for f in ('selfpub_services.csv',f'selfpub_services_{cc}.csv'):
  with (ROOT/'config'/f).open() as fh:rows+=list(csv.DictReader(fh))
 return [dict(x,regex=re.compile(x['name_pattern'])) for x in rows]
def classify(cc,y0=1995,y1=2023):
 cs.SERVICES=load_services(cc);cs.EXPLICIT=_Expl()
 path=ROOT/f'data/interim/{cc}_catalogue.parquet';con=duckdb.connect();con.execute("SET memory_limit='8GB'")
 con.execute(f"CREATE TEMP TABLE x AS SELECT * EXCLUDE(isbn13s,isbn_qualifiers),unnest(isbn13s) isbn13,unnest(isbn_qualifiers) isbn_qualifier FROM read_parquet('{path}')")
 con.execute("ALTER TABLE x ADD COLUMN isbn_print BOOLEAN")
 con.execute("UPDATE x SET isbn_print=is_print AND NOT regexp_matches(lower(coalesce(isbn_qualifier,'')),'e[ -]?book|epub|pdf|kindle|electronic|online|audio|lydbok|ljudbok')")
 n_all=con.execute('select count(*) from x').fetchone()[0]
 con.execute("CREATE TEMP TABLE ranked AS SELECT *,row_number() OVER(PARTITION BY isbn13 ORDER BY country_eligible DESC,is_published DESC,isbn_print DESC,(CASE WHEN len(publishers)>0 THEN 2 ELSE 0 END+CASE WHEN len(authors_personal)>0 THEN 2 ELSE 0 END+CASE WHEN title!='' THEN 1 ELSE 0 END+CASE WHEN pub_year IS NOT NULL THEN 1 ELSE 0 END) DESC,record_id) ranking FROM x")
 log=dict(isbn_rows=n_all,distinct_isbn=con.execute('select count(distinct isbn13) from x').fetchone()[0])
 for k,w in [('not_country_eligible','NOT country_eligible'),('not_monograph','NOT is_published'),('year_outside','pub_year IS NULL OR pub_year NOT BETWEEN %d AND %d'%(y0,y1))]:
  log['rows_excluded_'+k]=con.execute(f'select count(*) from ranked where ranking=1 and {w}').fetchone()[0]
 df=con.execute(f'SELECT * EXCLUDE(ranking) FROM ranked WHERE ranking=1 AND country_eligible AND is_published AND isbn_print AND pub_year BETWEEN {y0} AND {y1}').df()
 rows=df.to_dict('records')
 for r in rows:
  for k in ('publishers','authors_personal','authors_corporate','contributors_personal'):r[k]=list(r[k])
  r.update(cs.flags(r));pn=[cs.norm(p,True) for p in r['publishers']];pall=' '.join(cs.raw_norm(p) for p in r['publishers'])
  r['unidentified_publisher']=r['unidentified_publisher'] or bool(UNID.match(pall.strip())) or not any(pn)
 out=pd.DataFrame(rows);out['publisher_full']=out.publishers.map(lambda p:'; '.join(p));out['authors_str']=out.authors_personal.map(lambda a:' | '.join(a))
 out.drop(columns=['publishers','authors_personal','authors_corporate','contributors_personal'],inplace=True,errors='ignore')
 out.to_parquet(ROOT/f'data/interim/{cc}_classified.parquet',compression='zstd');log['classified']=len(out);return out,log
def wilson(k,n):
 if not n:return (np.nan,np.nan)
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
POP=pd.read_csv(ROOT/'config/population_official.csv')
def by_year(df,iso3):
 pop=POP[POP.iso3==iso3].set_index('year').population;rows=[]
 for y,g in df.groupby('pub_year'):
  n=len(g);r=dict(pub_year=int(y),print_isbns=n)
  for c,col in (('ap','author_is_publisher'),('service','service_imprint'),('combined','self_pub')):
   k=int(g[col].sum());lo,hi=wilson(k,n);r.update({c:k,'share_'+c:k/n,c+'_wilson_low':lo,c+'_wilson_high':hi})
  r['service_mixed_not_counted']=int(g.service_mixed.sum());r['unidentified_publisher']=int(g.unidentified_publisher.sum())
  P=pop.get(y,np.nan)/1e6;r['population_millions']=P;r['isbns_per_million']=n/P;r['selfpub_per_million']=r['combined']/P;r['ap_per_million']=r['ap']/P
  rows.append(r)
 return pd.DataFrame(rows)
def validation(df,cc,n=60):
 df=df.copy();df['key']=df.isbn13.map(lambda s:hashlib.sha1(f'{cc}-validation-v1|{s}'.encode()).hexdigest())
 cols=['isbn13','pub_year','title','authors_str','publisher_full','author_is_publisher','service_imprint','classification_reason','matched_services','explicit_author_statement','government','edition','key']
 fl=df[df.self_pub].sort_values('key').head(n).assign(stratum='flagged');un=df[~df.self_pub].sort_values('key').head(n).assign(stratum='unflagged')
 v=pd.concat([fl,un])[['stratum']+cols];v['gold_label']='';return v
CODEBOOK={'no':"""# Codebook: Norway (nb.no catalogue API)
Source: https://api.nb.no/catalog/v1/items (National Library of Norway search API; metadata in the public API). Query used: `year:<Y> isbn:<prefix>*`, filter `mediatype:bøker`, prefixes `97882` (ISBN-13) and `82` (ISBN-10), split recursively by next digit to stay under the API's ~5,100-hit paging cap. Raw: data/raw/nb_no/<year>/<prefix>.jsonl.gz (one API item per line).
Fields used: metadata.identifiers.isbn13/isbn10 (ISBN-10 converted to ISBN-13, checksum validated), metadata.title, metadata.creators (flat list; a name with a comma and no organisation word is treated as personal author, otherwise corporate), metadata.originInfo.publisher/issued, metadata.geographic.city, metadata.languages.
Universe: catalogued books (mediatype bøker) whose ISBN is in the Norwegian registration group 978-82. Country filter = ISBN prefix 978-82 (the API gives no reliable country-of-publication field). Books published in Norway under a foreign ISBN (e.g. KDP 979-8) are NOT in this universe; books with a 978-82 ISBN printed abroad are.
Print filter: none possible (API does not separate print and e-book records); all records are treated as print. One row per ISBN-13 (best record kept).
Year: originInfo.issued (4-digit year). Window 1995-2023.
Flags: author_is_publisher (name match author vs publisher via classify_selfpub.match_name, or explicit phrase 'eget forlag', 'forfatteren', 'selvutgitt' ...), service_imprint (config/selfpub_services.csv + config/selfpub_services_no.csv), self_pub = either. service_mixed = candidate imprints not counted.""",
'se':"""# Codebook: Sweden (Libris XL, Svensk bibliografi)
Source: https://libris.kb.se/find.jsonld (Libris XL find API, KB; CC0 data). Filters: meta.bibliography = https://libris.kb.se/library/NB (Nationalbibliografin / Svensk bibliografi), @type=PhysicalResource, category = saobf/Print, publication.year = Y. Raw: data/raw/libris/<year>/pNNNN.json.gz (200 records per page, as served).
Fields: identifiedBy[@type=ISBN] (ISBN-10 converted; checksum validated), publication[PrimaryPublication].agent.label (publisher), .year, .country.code ('sw' = Sweden), instanceOf.contribution (Person agents; PrimaryContribution/author role -> authors_personal, others -> contributors; non-person -> corporate), instanceOf @type (Monograph kept), hasTitle, editionStatement, hasNote.
Country filter: publication country code 'sw'. Monograph filter: instanceOf @type = Monograph. Print filter: carrier category saobf/Print in the query. One row per ISBN-13. Window 1995-2023.
Flags as for Norway with config/selfpub_services_se.csv."""}
def run(cc,iso3,name):
 out=ROOT/f'output/{name.lower()}';out.mkdir(parents=True,exist_ok=True)
 df,log=classify(cc);by=by_year(df,iso3);by.to_csv(out/f'{cc}_by_year.csv',index=False)
 v=validation(df,cc);v.to_csv(out/f'validation_{cc}.csv',index=False)
 (out/'codebook.md').write_text(CODEBOOK[cc]+f"\n\nBuild log: {json.dumps(log)}\n")
 top=df[df.service_imprint].matched_services.value_counts().head(15)
 print(json.dumps(log));print(by[['pub_year','print_isbns','ap','service','combined','share_combined']].to_string());print(top.to_string())
 json.dump(log,open(out/'build_log.json','w'),indent=1);return df
