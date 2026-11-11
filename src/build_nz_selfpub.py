"""Stream Publications NZ into the study schema; retains all years and non-ISBN records."""
import sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from lxml import etree
from study_common import *
from build_nz import parse_record,M,subfields

def parse(rec):
 old=parse_record(rec);cf={c.get('tag'):c.text or '' for c in rec.findall(M+'controlfield')};f008=cf.get('008','').ljust(40)
 ps=[];co=[];contributors=[];pairs=[];carrier=[];physical=[];notes=[];edition=[];unknown=False
 for f in rec.findall(M+'datafield'):
  tag=f.get('tag');v=lambda codes:subfields(f,codes)
  if tag=='020':pairs.extend((s,' '.join(v('q'))) for s in v('a'))
  elif tag in ('100','700'):
   name=tidy(' '.join(v('abq')));roles=' '.join(v('e4')).lower()
   if tag=='100' or not roles or 'author' in roles or 'aut' in v('4'):ps.append(name);unknown|=not bool(roles)
   else:contributors.append(name)
  elif tag in ('110','710'):co.append(tidy(' '.join(v('ab'))))
  elif tag=='338':carrier+=v('ab')
  elif tag=='300':physical+=v('abc')
  elif tag=='245':carrier+=v('h')
  elif tag=='250':edition+=v('a')
  elif tag in ('500','502'):notes+=v('a')
 c007=[c.text or '' for c in rec.findall(M+'controlfield') if c.get('tag')=='007']
 car='; '.join(carrier);phys='; '.join(physical)
 electronic=any(x.startswith(('cr','co')) for x in c007) or f008[23] in 'oqs' or bool(DIGITAL.search(car+' '+phys))
 micro=f008[23] in 'abc' or any(x.startswith('h') for x in c007)
 ids,qs=isbn_pairs(pairs)
 return base('nz',record_id=old['nlnz_id'],country_code=old['country_008'],country_eligible=old['country_008']=='nz',pub_year=year(old['date1']),title=old['title'],place='; '.join(old['places']),publishers=old['publishers'],authors_personal=ps,contributors_personal=contributors,authors_corporate=co,record_type=old['record_type'],bib_level=old['bib_level'],carrier=car+'; 007='+','.join(c007),language=f008[35:38].strip(),physical_description=phys,edition='; '.join(edition),notes='; '.join(notes),isbn13s=ids,isbn_qualifiers=qs,is_print=old['record_type']=='a' and old['bib_level']=='m' and not(electronic or micro or NONPRINT.search(car+' '+phys)),format_evidence='MARC21 leader + 008/23 + 007 + 245h + 338 + 300',is_published=(rec.findtext(M+'leader') or ' '*18)[17:18]!='8',role_uncertain=unknown)
def main():
 sink=Sink('nz')
 with zipfile.ZipFile(ROOT/'data/raw/natlibnz/pubsnzmetadataxml.zip') as z,z.open(z.namelist()[0]) as f:
  for _,el in etree.iterparse(f,events=('end',),tag=M+'record',resolve_entities=False,no_network=True):
   sink.add(parse(el));el.clear()
   while el.getprevious() is not None:del el.getparent()[0]
   if sink.n%100000==0:print('NZ',sink.n,flush=True)
 sink.close()
if __name__=='__main__':main()
