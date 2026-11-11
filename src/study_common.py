"""Shared schema, ISBN cleaning, and bounded-memory Parquet writing."""
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pyarrow as pa
import pyarrow.parquet as pq
from build_2025 import clean_isbns
TEXT_FIELDS='source record_id country_code title place record_type bib_level carrier language physical_description edition notes format_evidence'.split()
LIST_FIELDS='authors_personal contributors_personal authors_corporate publishers isbn13s isbn_qualifiers'.split()
BOOL_FIELDS='is_print country_eligible is_published role_uncertain'.split()
SCHEMA=pa.schema([(x,pa.string()) for x in TEXT_FIELDS]+[(x,pa.list_(pa.string())) for x in LIST_FIELDS]+[(x,pa.bool_()) for x in BOOL_FIELDS]+[('pub_year',pa.int32())])
DIGITAL=re.compile(r'e[ -]?book|epub|\bpdf\b|kindle|electronic resource|online resource|ressource en ligne|livre num[eé]rique|computer (?:disc|disk)|CD-ROM',re.I)
NONPRINT=re.compile(r'sound (?:disc|cassette|recording)|audio(?:book| disc| cassette)|microfiche|microfilm|videodisc|DVD|braille',re.I)
def tidy(s):return re.sub(r'\s+',' ',s or '').strip(' []:;,/=')
def year(s):
 m=re.search(r'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)',s or '')
 return int(m.group()) if m else None
def isbn_pairs(values):
 """Extract ISBN token before qualifiers, validate via existing checksum helpers."""
 out={}
 for raw,q in values:
  # Qualifiers can contain numbers: never concatenate them into the identifier.
  m=re.match(r'\s*(?:ISBN(?:-1[03])?\s*:?)?\s*([0-9Xx][0-9Xx\- ]{8,25})',raw)
  if not m:continue
  for isbn in clean_isbns([m.group(1).strip()],[]):
   qualifier=tidy(q+' '+raw[m.end():]);out[isbn]=tidy(out.get(isbn,'')+' '+qualifier)
 return list(out),list(out.values())
def base(source,**kw):
 r={x:'' for x in TEXT_FIELDS};r.update({x:[] for x in LIST_FIELDS});r.update({x:False for x in BOOL_FIELDS});r.update(source=source,pub_year=None,is_published=True);r.update(kw);return r
class Sink:
 def __init__(self,source):
  self.path=ROOT/f'data/interim/{source}_catalogue.parquet';self.tmp=self.path.with_suffix('.parquet.tmp');self.writer=pq.ParquetWriter(self.tmp,SCHEMA,compression='zstd');self.rows=[];self.n=0
 def add(self,r):
  self.rows.append(r);self.n+=1
  if len(self.rows)>=10000:self.flush()
 def flush(self):
  if self.rows:self.writer.write_table(pa.Table.from_pylist(self.rows,schema=SCHEMA));self.rows=[]
 def close(self):self.flush();self.writer.close();self.tmp.replace(self.path);print(self.path,self.n,flush=True)
