"""Germany (DNB title data, MARC21 .mrc.gz, CC0): stream -> common schema (data/interim/de_catalogue.parquet),
then classify (author=publisher; German service imprints) -> data/interim/de_classified.parquet.
usage: build_de.py parse [file_index ...]   |  build_de.py merge  |  build_de.py classify
Raw files: data/raw/dnb/dnb_all_dnbmarc_20261013.N.mrc.gz (never modified)."""
import sys,re,csv,gzip,json,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from study_common import Sink,base,isbn_pairs,tidy,year
RAW=ROOT/'data/raw/dnb';VER='20261013'
OUT=ROOT/'output/germany';OUT.mkdir(parents=True,exist_ok=True)
# ---------------- parsing ----------------
NONPRINT_CARRIER=re.compile(r'online|computer|datentr|audio|video|mikro|cd|dvd|speicher|lochkarte|schallplatte|kassette|folie|objekt|stereo|disk',re.I)
PRINT_CARRIER=re.compile(r'^(?:band|bände|blatt|blätter|karte|tafel|heft|bogen|rolle|faltblatt)',re.I)
def fields(rec):
 ldr=rec[:24];b=int(ldr[12:17]);d=rec[24:b-1];out={}
 for i in range(0,len(d),12):
  tag=d[i:i+3].decode();ln=int(d[i+3:i+7]);st=int(d[i+7:i+12]);out.setdefault(tag,[]).append(rec[b+st:b+st+ln-1])
 return ldr,out
def subs(raw):
 """variable field -> (ind1+ind2, [(code,text)])"""
 ind=raw[:2].decode('latin1');s=[]
 for p in raw[2:].split(b'\x1f')[1:]:
  if p:s.append((chr(p[0]),p[1:].decode('utf-8','replace')))
 return ind,s
def sf(raw,codes):
 return [t for c,t in subs(raw)[1] if c in codes]
def clean_name(n):return tidy(re.sub(r'<[^>]*>','',n or ''))
def parse_record(rec,fn):
 ldr,f=fields(rec)
 if ldr[6:7]!=b'a' or ldr[7:8]!=b'm':return None,'not_text_monograph'
 g=lambda t:f.get(t,[])
 f008=g('008')[0].decode('latin1') if g('008') else ''
 isbns=[];quals=[]
 raw020=[]
 for r in g('020'):
  s=subs(r)[1];a=[t for c,t in s if c=='a'];n9=[t for c,t in s if c=='9'];c=' '.join(t for k,t in s if k in 'cqb')
  src=a or n9
  for x in src:raw020.append((x,c))
 isbns,quals=isbn_pairs(raw020)
 y=None
 pub=[];place=[]
 for r in g('264')+g('260'):
  ind,s=subs(r)
  if r in g('264') and ind[1] not in '14':continue  # 264 _4 = copyright date only; keep _1 (publication) (and _4 only for year)
  if ind[1]=='4':continue
  place+= [clean_name(t) for c,t in s if c=='a'];pub+=[clean_name(t) for c,t in s if c=='b']
  if y is None:
   for c,t in s:
    if c=='c' and year(t):y=year(t);break
 if y is None:
  y=year(f008[7:11]) if f008[6:7] in 'smtrep' and f008[7:11].isdigit() else None
 if y is None:
  for r in g('264'):
   for c,t in subs(r)[1]:
    if c=='c' and year(t):y=year(t);break
 carrier='; '.join(t for r in g('338') for t in sf(r,'a'))
 f007=g('007')[0].decode('latin1')[:2] if g('007') else ''
 phys=' '.join(t for r in g('300') for t in sf(r,'a'))
 url856=[t for r in g('856') for t in sf(r,'u')]
 online=bool(re.search(r'online|computer',carrier,re.I)) or f007[:1]=='c' or ' '.join(t for r in g('020') for t in sf(r,'c')).lower().find('online')>=0
 if carrier:printc=bool(PRINT_CARRIER.match(carrier)) and not NONPRINT_CARRIER.search(carrier)
 else:printc=(f007[:1] in ('t','')) and not online
 if online:printc=False
 if re.search(r'\bCD|DVD|online|Datentr',phys,re.I) and not re.search(r'\bS\.|Seiten|Bl\.',phys):printc=False
 cc=[t for r in g('044') for t in sf(r,'c')]
 country='DE' if any(x in ('XA-DE','XA-DDDE') for x in cc) else (cc[0] if cc else ('DE' if f008[15:18] in ('gw','ge') else f008[15:18]))
 eligible=country=='DE'
 aut=[];con=[];corp=[]
 for r in g('100')+g('700'):
  s=subs(r)[1];nm=clean_name(' '.join(t for c,t in s if c=='a'));rel=[t for c,t in s if c=='4']
  if not nm:continue
  (aut if (r in g('100') or any(x in ('aut','cre') for x in rel)) else con).append(nm)
 for r in g('110')+g('111')+g('710')+g('711'):
  n=clean_name(' '.join(t for c,t in subs(r)[1] if c in 'ab'))
  if n:corp.append(n)
 title=tidy(' '.join(t for r in g('245') for t in sf(r,'ab')))
 notes=' | '.join(t for k in ('502','500','501','504') for r in g(k) for t in sf(r,'a'))[:500]
 gnd=bool(g('100'))
 f041=[t for r in g('041') for t in sf(r,'a')]
 d=base('de',record_id=(g('001')[0].decode() if g('001') else ''),country_code=country,title=title,place='; '.join(place),record_type='a',bib_level='m',carrier=carrier,
  language=(f041[0] if f041 else f008[35:38]),physical_description=phys,edition=' '.join(t for r in g('250') for t in sf(r,'a')),notes=notes,
  format_evidence=f"007:{f007}|f008type:{f008[6:7]}|856:{len(url856)}",authors_personal=aut,contributors_personal=con,authors_corporate=corp,publishers=pub,isbn13s=isbns,isbn_qualifiers=quals,
  is_print=printc,country_eligible=eligible,is_published=True,role_uncertain=False,pub_year=y)
 return d,'ok'
def parse(idxs):
 import collections
 for i in idxs:
  fn=RAW/f'dnb_all_dnbmarc_{VER}.{i}.mrc.gz';sink=Sink(f'de_part{i}');st=collections.Counter();buf=b''
  with gzip.open(fn,'rb') as fh:
   while True:
    chunk=fh.read(1<<24)
    if not chunk and not buf:break
    buf+=chunk;parts=buf.split(b'\x1d');buf=parts.pop() if chunk else b''
    for r in parts:
     if not r:continue
     st['records']+=1
     try:d,why=parse_record(r+b'\x1d',fn)
     except Exception as e:st['parse_error']+=1;continue
     if d is None:st[why]+=1;continue
     st['text_monograph']+=1
     if not d['isbn13s']:st['no_isbn']+=1;continue
     sink.add(d);st['written']+=1
    if st['records']%2000000<len(parts):print(i,dict(st),flush=True)
    if not chunk:break
  sink.close();json.dump(dict(st),open(OUT/f'parse_log_part{i}.json','w'));print(i,dict(st),flush=True)
def merge():
 import duckdb
 con=duckdb.connect();files=sorted((ROOT/'data/interim').glob('de_part*_catalogue.parquet'))
 print(files)
 con.execute(f"COPY (SELECT * FROM read_parquet({[str(x) for x in files]})) TO '{ROOT}/data/interim/de_catalogue.parquet' (FORMAT parquet,COMPRESSION zstd)")
 print(con.execute(f"select count(*) from read_parquet('{ROOT}/data/interim/de_catalogue.parquet')").fetchone())

# ---------------- classification ----------------
from classify_selfpub import norm,match_name
from ap_consistent import ap_consistent,split_name
PART_DE={'von','van','de','der','den','zu','zur','vom','la','le','di','da','du','und','and'}
def low(s):
 s=unicodedata.normalize('NFKD',s or '');s=''.join(c for c in s if not unicodedata.combining(c));return s.lower().replace('\u00df','ss')
def umlaut(s):return re.sub(r'ae|oe|ue','',s) if False else s.replace('ae','a').replace('oe','o').replace('ue','u')
CORP=re.compile(r'\b(?:verlag|verlage|verlags\w*|verl|buchverlag|gmbh|mbh|kg|ag|ohg|ug|gbr|e k|e v|co|und|haftungsbeschrankt|edition|editions|ed|medien|media|publishing|publishers|publisher|publications|books|press|buchhandlung|druck|druckerei|haus|im|des|der|die|das|inh)\b')
EXPL=re.compile(r"\bselbstverl\w*|\beigenverl\w*|\bselbstverleg\w*|\bverl(?:ag)?\.? ?(?:des|d|der|von) ?(?:autors?|autorin\w*|verfassers?|verf|autor)\b|\bverlag d(?:es)? autor\w*|^(?:der |die )?(?:autor|autorin|verfasser|verfasserin)$|^autor(?:in|en)? ?(?:selbst)?$|\bvom (?:autor|verfasser)\b|\bprivatdruck\b|\bauf kosten (?:des|d) (?:autors|verfassers|verf)|\bautor(?:in)? im selbstverlag|\bverfasser im selbstverlag|\bvon autor\b|\bautoren? selbst\b|\bselbst ?publi\w*|\bself.?publi\w*|\bin eigener regie\b|\bverlag des verfassers\b")
INST=re.compile(r'\b(?:verein|vereins|vereinigung|gesellschaft|institut|museum|universitat|uni|stiftung|kirche|kirchen\w*|gemeinde|e v|akademie|bund|landkreis|kreis|stadt|amt|verband|club|arbeitskreis|arbeitsgemeinschaft|fakultat|schule|sektion|ministerium|forschung\w*|zentrum|bibliothek|archiv|innung|kammer|fachbereich|lehrstuhl|seminar|abteilung|dienststelle|hochschule|fachhochschule|herausgeber\w*|hrsg|redaktion|land|bezirk|stadtverwaltung|verwaltung|projekt|gruppe|initiative|forum|werk|kloster|pfarr\w*|chor|orchester|bibliotheken|fachschaft|institution|organisation|dachverband|landesverband|ortsverein)\b')
GOV=re.compile(r'\b(?:bundesministerium|ministerium|landesregierung|bundesamt|landesamt|statistisch\w*|bundestag|landtag|bundesregierung|regierungs\w*|stadtverwaltung|landratsamt|senatsverwaltung|bundesanstalt|landesanstalt|deutscher bundestag|bundesrat|auswartiges amt)\b')
UNID=re.compile(r'^(?:s\W*n\W*|o\W*v\W*|ohne verlag|ohne verlagsangabe|ohne angabe|verlag nicht ermittelbar|nicht ermittelbar|verlag nicht ermittelt|\[?s\.? ?n\.?\]?|ohne ort und verlag|nicht angegeben|k\W*a\W*)$')
REPRINT=re.compile(r'\b(?:[2-9]|1\d)\.?\s*(?:aufl|ausg|ed|neu)|neuaufl|nachdr|neubearb|uberarb|erw\b|erweit|reprint|unverand|\bneuausg|\bneudruck|\bsonderausg')
THESIS=re.compile(r'diss|hochschulschrift|habil|zugl\b|zugl\.|bachelor|masterarbeit|diplomarbeit|thesis|inaug')
with (ROOT/'config/selfpub_services_de.csv').open() as f:SERV=[dict(x,regex=re.compile(x['name_pattern'])) for x in csv.DictReader(f)]
def pubclean(p):return re.sub(r'[\[\]]','',p or '').strip(' ,;.:/')
def nmatch(a,pc):
 m=match_name(a,pc)
 if m:return m
 g,s=split_name(a)
 if umlaut(' '.join(g+s))!=' '.join(g+s) or umlaut(pc)!=pc:
  m=match_name(umlaut(' '.join(g+s)),umlaut(pc))
  if m:return 'umlaut_'+m
 return ''
def flags(r):
 pubs=[pubclean(p) for p in r['publishers'] if pubclean(p)];pl=low('; '.join(pubs));authors=list(r['authors_personal']);corp=[low(c) for c in r['authors_corporate']]
 pc=norm(CORP.sub(' ',norm(pl,True)),True) if pl else ''
 out={};out['publisher']='; '.join(pubs)
 out['unidentified_publisher']=(not pc and not EXPL.search(pl)) or bool(UNID.match(pl.strip()))
 expl=bool(EXPL.search(pl));inst=bool(INST.search(pl)) and expl
 personal_ok=bool(authors)
 ap=False;why=[];corp_self=False
 if expl:
  if inst or (not personal_ok and corp):corp_self=True
  else:ap=True;why.append('explicit_author_statement')
 if pc and not out['unidentified_publisher']:
  for a in authors:
   for p in [pc]+[norm(CORP.sub(' ',norm(low(x),True)),True) for x in pubs]:
    m=nmatch(a,p)
    if m:ap=True;why.append(m);break
 apc=False
 if pc:
  toks=pc.split()
  for a in authors:
   if ap_consistent(a,toks,PART_DE) or ap_consistent(umlaut(low(a)) if False else a,[umlaut(t) for t in toks],PART_DE):apc=True;break
 out['ap_pure']=apc;out['ap_consistent']=ap or apc
 out['corporate_self']=corp_self or any(norm(c,True)==pc and len(pc)>3 for c in corp)
 svc=mixed=False;tiers=set();names=[];weak=False;doc=False
 for s in SERV:
  if s['regex'].search(pl):
   if s['scope']=='mixed':mixed=True;continue
   if r['pub_year'] and (r['pub_year']<int(s['start_year']) or r['pub_year']>int(s['end_year'])):continue
   svc=True;tiers.add(s['tier']);names.append(s['name_pattern'].split('|')[0][:40]);weak|=s['evidence_status']!='documented';doc|=s['evidence_status']=='documented'
 # fallback: BoD often appears as place Norderstedt only
 out.update(author_is_publisher=ap,service_imprint=svc,service_mixed=mixed,service_platform='platform' in tiers,service_author_services='author_services' in tiers,service_vanity='vanity' in tiers,
  service_documented=doc,foreign_bod=bool(re.search(r'books on demand\W+(?:frankreich|schweden|finnland|danemark|spanien|norwegen|italien|niederlande|polen|osterreich|schweiz|belgien|portugal)',pl)),self_pub_combined=ap or svc,classification_reason=';'.join(sorted(set(why))),matched_services=';'.join(names),explicit=expl,institutional_selfpub=bool(expl and inst))
 txt=low(r['notes'])
 out['government']=bool(GOV.search(pl)) or any(GOV.search(c) for c in corp)
 out['thesis']=bool(THESIS.search(txt))
 out['reprint']=bool(REPRINT.search(low(r['edition'])))
 out['bod_place']='norderstedt' in low(r['place']);out['amazon_imprint']=bool(re.search(r'create\s?space|independently published|amazon|kindle',pl))
 return out
def classify():
 import duckdb,pandas as pd
 con=duckdb.connect();con.execute("SET memory_limit='10GB';SET preserve_insertion_order=false")
 P=ROOT/'data/interim/de_catalogue.parquet';log={}
 log['records_text_monograph_with_isbn']=con.execute(f"select count(*) from read_parquet('{P}')").fetchone()[0]
 for k,w in [('not_print','not is_print'),('not_DE',"not (country_code='DE' OR country_code LIKE 'XA-DE%' OR country_code LIKE 'XA-DDDE%')"),('no_year','pub_year is null'),('year_outside_1995_2023','pub_year is not null and (pub_year<1995 or pub_year>2023)')]:
  log['records_'+k]=con.execute(f"select count(*) from read_parquet('{P}') where {w}").fetchone()[0]
 con.execute(f"CREATE TEMP TABLE x AS SELECT * EXCLUDE(isbn13s,isbn_qualifiers),unnest(isbn13s) isbn13,unnest(isbn_qualifiers) isbn_qualifier FROM read_parquet('{P}') WHERE is_print AND (country_code='DE' OR country_code LIKE 'XA-DE%' OR country_code LIKE 'XA-DDDE%') AND pub_year BETWEEN 1995 AND 2023")
 con.execute("UPDATE x SET is_print=NOT regexp_matches(lower(coalesce(isbn_qualifier,'')),'e[ -]?book|epub|pdf|kindle|online|elektron|audio|hörbuch|cd|dvd|mp3')")
 log['isbn_rows_before_dedup']=con.execute("select count(*) from x").fetchone()[0]
 con.execute("""CREATE TEMP TABLE r AS SELECT * EXCLUDE(rk) FROM (SELECT *,row_number() OVER(PARTITION BY isbn13 ORDER BY (CASE WHEN len(publishers)>0 THEN 2 ELSE 0 END+CASE WHEN len(authors_personal)>0 THEN 2 ELSE 0 END+CASE WHEN title!='' THEN 1 ELSE 0 END) DESC,pub_year,record_id) rk FROM x WHERE is_print) WHERE rk=1""")
 log['isbn_rows_after_dedup']=con.execute("select count(*) from r").fetchone()[0]
 import pyarrow as pa,pyarrow.parquet as pq
 dest=ROOT/'data/interim/de_classified.parquet';tmp=dest.with_suffix('.tmp');w=None;n=0
 it=con.execute("select * from r").fetch_record_batch(20000)
 for b in it:
  rows=b.to_pylist()
  for q in rows:q.update(flags(q))
  t=pa.Table.from_pylist(rows)
  if w is None:w=pq.ParquetWriter(tmp,t.schema,compression='zstd')
  w.write_table(t);n+=len(rows)
 w.close();tmp.replace(dest);log['classified']=n
 json.dump(log,open(OUT/'build_log.json','w'),indent=1);print(json.dumps(log,indent=1))
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='parse':parse([int(x) for x in sys.argv[2:]] or [1,2,3,4,5])
 elif cmd=='merge':merge()
 elif cmd=='classify':classify()
