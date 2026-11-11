"""Stream the nested BNB RDF/XML books product, excluding distribution-only geography."""
import sys,zipfile,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from lxml import etree
from study_common import *
NS=dict(rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#',dct='http://purl.org/dc/terms/',blt='http://www.bl.uk/schemas/bibliographic/blterms#',event='http://purl.org/NET/c4dm/event.owl#',rdfs='http://www.w3.org/2000/01/rdf-schema#',foaf='http://xmlns.com/foaf/0.1/',bibo='http://purl.org/ontology/bibo/',rdau='http://rdaregistry.info/Elements/u/',isbd='http://iflastandards.info/ns/isbd/elements/')
R='{'+NS['rdf']+'}'
UK_GEO={'6269131':'enk','2638360':'stk','2634895':'wlk','2641364':'nik','2635167':'xxk'}
def xp(el,path):return el.xpath(path,namespaces=NS)
def parse(el):
 title=el.findtext('dct:title',namespaces=NS)
 if title is None:return None
 events=xp(el,'blt:publication/rdf:Description')
 ps=[];co=[];con=[]
 for field,target in [('creator',ps),('contributor',con)]:
  for a in xp(el,'dct:'+field+'/rdf:Description'):
   name=a.findtext('foaf:name',namespaces=NS) or a.findtext('rdfs:label',namespaces=NS) or ''
   if NS['foaf']+'Person' in xp(a,'rdf:type/@rdf:resource'):target.append(name)
   else:co.append(name)
 pubs=[];places=[];years=[];codes=[]
 for e in events:
  pubs+=xp(e,'event:agent/rdf:Description/rdfs:label/text()')
  places+=xp(e,'event:place/rdf:Description/rdfs:label/text()')
  years+=xp(e,'event:time/rdf:Description/rdfs:label/text()')
  for u in xp(e,'event:place/@rdf:resource'):
   key=u.rstrip('/').split('/')[-1];codes.append(UK_GEO.get(key,'geo:'+key))
 ids,qs=isbn_pairs([(s,'') for s in xp(el,'bibo:isbn13/text()|bibo:isbn10/text()')])
 carrier=xp(el,'rdau:P60048/@rdf:resource');media=xp(el,'rdau:P60050/@rdf:resource');content=xp(el,'rdau:P60049/@rdf:resource')
 phys='; '.join(xp(el,'isbd:P1053/text()'));fmt='; '.join(carrier+media+content)
 volume=any(u.endswith('/1049') for u in carrier);text=any(u.endswith('/1020') for u in content);unmediated=any(u.endswith('/1007') for u in media)
 fallback=not carrier and bool(re.search(r'\b(?:p\.|pages|volumes?|v\.)',phys,re.I))
 print_ok=(volume or fallback) and (text or not content) and (unmediated or not media) and not bool(DIGITAL.search(phys) or NONPRINT.search(phys))
 yrs=sorted(set(y for y in map(year,years) if y))
 return base('uk',record_id=el.get(R+'about',''),country_code=';'.join(sorted(set(codes))),country_eligible=any(c in UK_GEO.values() for c in codes),pub_year=yrs[0] if yrs else None,title=title,place='; '.join(places),publishers=pubs,authors_personal=ps,contributors_personal=con,authors_corporate=co,record_type='a' if text else '',bib_level='m',carrier=fmt,language=';'.join(u.split('/')[-1] for u in xp(el,'dct:language/@rdf:resource')),physical_description=phys,edition='; '.join(xp(el,'bibo:edition/text()')),notes='; '.join(xp(el,'dct:description/text()')),isbn13s=ids,isbn_qualifiers=qs,is_print=print_ok,format_evidence='RDA volume/text/unmediated; physical-description fallback if carrier absent',role_uncertain=True)
def main():
 sink=Sink('uk')
 with zipfile.ZipFile(ROOT/'data/raw/bnb/BNBLODBooks_201805_rdf.zip') as z:
  for name in z.namelist():
   if not name.endswith('.rdf'):continue
   with z.open(name) as f:
    for _,el in etree.iterparse(f,events=('end',),tag=R+'Description',resolve_entities=False,no_network=True):
     # Nested descriptions must survive until the outer bibliographic description finishes.
     if el.getparent() is None or el.getparent().tag!=R+'RDF':continue
     r=parse(el)
     if r:sink.add(r)
     el.clear()
     while el.getprevious() is not None:del el.getparent()[0]
   print(name,sink.n,flush=True)
 sink.close()
if __name__=='__main__':main()
