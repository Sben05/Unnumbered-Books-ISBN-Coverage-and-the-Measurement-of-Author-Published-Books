"""Parse Library of Congress MDSConnect BooksAll (MARC21) into the study schema, source 'us'. Parallel by part file."""
import sys,gzip,io
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pyarrow as pa,pyarrow.parquet as pq,duckdb
from pymarc import MARCReader
from study_common import *
PARTS=ROOT/'data/interim/_scratch/loc_parts'
def sf(f,codes):return [tidy(x.value) for x in f.subfields if x.code in codes and tidy(x.value)]
def parse(rec,part):
 g=lambda t:rec.get_fields(t);ld=rec.leader;f008=(g('008')[0].data if g('008') else '').ljust(40)
 pairs=[];ps=[];con=[];co=[];pubs=[];places=[];phys=[];edition=[];notes=[];title='';date=''
 for f in rec.get_fields('020'):pairs.extend((s,' '.join(sf(f,'q'))) for s in sf(f,'a'))
 for f in g('100')+g('700'):
  name=tidy(' '.join(sf(f,'aq')));roles=' '.join(sf(f,'e4')).lower()
  if f.tag=='100' or not roles or 'author' in roles or 'aut' in roles:ps.append(name)
  else:con.append(name)
 for f in g('110')+g('710'):co.append(tidy(' '.join(sf(f,'ab'))))
 for f in g('245'):title=' '.join(sf(f,'ab'))
 for f in g('260')+[x for x in g('264') if x.indicator2=='1']:pubs+=sf(f,'b');places+=sf(f,'a');date=date or ' '.join(sf(f,'c'))
 for f in g('300'):phys+=sf(f,'abc')
 for f in g('250'):edition+=sf(f,'a')
 for f in g('500')+g('502'):notes+=sf(f,'a')
 ids,qs=isbn_pairs(pairs);cc=f008[15:18].strip();p='; '.join(phys)
 recid=(g('001')[0].data if g('001') else '').strip() or f'{part}:?'
 electronic=f008[23] in 'oqs' or bool(DIGITAL.search(p+' '+' '.join(sf(g('245')[0],'h')) if g('245') else p))
 return base('us',record_id=recid,country_code=cc,country_eligible=cc.endswith('u') and cc not in ('',),pub_year=year(f008[7:11]) or year(date),title=title,place='; '.join(places),publishers=pubs,authors_personal=ps,contributors_personal=con,authors_corporate=co,record_type=ld[6],bib_level=ld[7],carrier='008/23='+f008[23],language=f008[35:38].strip(),physical_description=p,edition='; '.join(edition),notes='; '.join(notes),isbn13s=ids,isbn_qualifiers=qs,is_print=ld[6]=='a' and ld[7]=='m' and not(electronic or f008[23] in 'abc' or NONPRINT.search(p)),format_evidence='MARC21 leader + 008/23 + 300',is_published=True)
def work(path):
 out=PARTS/(path.name.split('.')[2]+'.parquet');w=pq.ParquetWriter(out,SCHEMA,compression='zstd');rows=[];n=0
 with gzip.open(path,'rb') as fh:
  for rec in MARCReader(fh,to_unicode=True,force_utf8=True,permissive=True):
   if rec is None:continue
   try:rows.append(parse(rec,path.name))
   except Exception as e:continue
   n+=1
   if len(rows)>=10000:w.write_table(pa.Table.from_pylist(rows,schema=SCHEMA));rows=[]
 if rows:w.write_table(pa.Table.from_pylist(rows,schema=SCHEMA))
 w.close();return path.name,n
def main():
 PARTS.mkdir(parents=True,exist_ok=True);files=sorted((ROOT/'data/raw/loc_books').glob('*.gz'))
 with ProcessPoolExecutor(6) as ex:
  for name,n in ex.map(work,files):print(name,n,flush=True)
 duckdb.connect().execute(f"COPY (SELECT * FROM read_parquet('{PARTS}/*.parquet')) TO '{ROOT}/data/interim/us_catalogue.parquet' (FORMAT parquet,COMPRESSION zstd)")
 print('us catalogue done',flush=True)
if __name__=='__main__':main()
