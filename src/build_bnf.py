"""Stream BnF's public UNIMARC ISO2709/UTF8 retrospective national books bibliography."""
import sys,re,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from pymarc import MARCReader
from study_common import *
def values(rec,tag,codes):return [v for f in rec.get_fields(tag) for v in f.get_subfields(*codes)]
def clean(s):return tidy(re.sub('[\x80-\x9f]','',s))
def parse(rec):
 v=lambda tag,codes:values(rec,tag,codes)
 leader=str(rec.leader).ljust(24);date=(v('100','a') or [''])[0].ljust(20);countries=v('102','a');pairs=[]
 for f in rec.get_fields('010'):
  pairs.extend((s,' '.join(f.get_subfields('b'))) for s in f.get_subfields('a'))
 ids,qs=isbn_pairs(pairs);authors=[];contributors=[];corporate=[];uncertain=False
 for f in rec.get_fields('700','701','702'):
  name=clean(', '.join(filter(None,[' '.join(f.get_subfields('a')),' '.join(f.get_subfields('b'))])))
  roles=f.get_subfields('4')
  if '070' in roles or (not roles and f.tag in ('700','701')):authors.append(name);uncertain|=not bool(roles)
  else:contributors.append(name)
 for f in rec.get_fields('710','711','712'):corporate.append(clean(' '.join(f.get_subfields('a','b'))))
 pubs=[];places=[];dates=[]
 for f in rec.get_fields('210','214'):
  # 214 indicator 2=0 publication; 1 production, 2 distribution, 3 manufacture, 4 copyright.
  if f.tag=='214' and f.indicators[1]!='0':continue
  pubs+=f.get_subfields('c');places+=f.get_subfields('a');dates+=f.get_subfields('d')
 phys='; '.join(v('215','acd'));gmd='; '.join(v('200','b'));media=v('182','c');carrier=v('183','c');form=v('106','a')
 digital=bool(DIGITAL.search(gmd+' '+phys)) or 'c' in media or bool(rec.get_fields('135'))
 nonprint=any(s in ('f','g','h','s','t') for s in form) or bool(NONPRINT.search(gmd+' '+phys))
 return base('fr',record_id=rec.get('001').data if rec.get('001') else '',country_code=';'.join(countries),country_eligible='FR' in countries,pub_year=year(date[9:13]) or year(' '.join(dates)),title=clean(' : '.join(v('200','aehi'))),publishers=[clean(p) for p in pubs],place='; '.join(map(clean,places)),authors_personal=authors,contributors_personal=contributors,authors_corporate=corporate,record_type=leader[6],bib_level=leader[7],carrier=gmd+'; 106='+','.join(form)+'; 182='+','.join(media)+'; 183='+','.join(carrier),language=';'.join(v('101','a')),physical_description=phys,edition='; '.join(v('205','a')),notes='; '.join(v('300','a')+v('328','a')),isbn13s=ids,isbn_qualifiers=qs,is_print=leader[6]=='a' and leader[7]=='m' and not(digital or nonprint),format_evidence='UNIMARC leader + 106 + 135 + 182 + 200b + 215',role_uncertain=uncertain)
def main():
 resume=ROOT/'data/interim/_scratch/fr_catalogue.resume.parquet'
 if '--resume' in sys.argv:
  (ROOT/'data/interim/fr_catalogue.parquet.tmp').replace(resume)
 sink=Sink('fr');errors=[];skip=0;seen=0
 if '--resume' in sys.argv:
  old=pq.ParquetFile(resume);skip=old.metadata.num_rows
  for batch in old.iter_batches(batch_size=10000):sink.writer.write_table(pa.Table.from_batches([batch]))
  sink.n=skip;print('Restored',skip,'persisted rows',flush=True)
 files=list((ROOT/'data/raw/bnf').glob('*.UTF8'))
 assert len(files)==28, f'Expected all 28 files, got {len(files)}'
 for path in sorted(files):
  with path.open('rb') as f:
   reader=MARCReader(f,to_unicode=True,force_utf8=True,utf8_handling='strict')
   for i,rec in enumerate(reader):
    if rec is None:errors.append(dict(file=path.name,record=i,error=str(reader.current_exception)));continue
    seen+=1
    if seen<=skip:continue
    try:
     row=parse(rec)
     if not row['record_id']:
      row['record_id']=path.name+':'+str(i)
      errors.append(dict(file=path.name,record=i,error='Missing 001; stable file:record surrogate retained'))
     sink.add(row)
    except Exception as exc:
     errors.append(dict(file=path.name,record=i,error=repr(exc)))
  print(path.name,sink.n,flush=True)
 sink.close();(ROOT/'output/selfpub/bnf_parse_errors.json').write_text(json.dumps(errors,indent=2))
if __name__=='__main__':main()
