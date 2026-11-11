"""Sweden (Libris XL, bibliography NB = Svensk bibliografi, print PhysicalResource) -> data/interim/se_catalogue.parquet."""
import sys,gzip,json,glob
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from study_common import Sink,base,tidy,year
from build_2025 import clean_isbns
def lab(x):
 if isinstance(x,dict):
  v=x.get('label') or x.get('name') or '';return ' '.join(v) if isinstance(v,list) else str(v)
 return str(x)
def parse(it):
 vals=[];quals=[]
 for i in it.get('identifiedBy',[]):
  if i.get('@type')=='ISBN' and i.get('value'):
   for c in clean_isbns([i['value']],[]):
    vals.append(c);q=i.get('qualifier');quals.append(tidy(' '.join(q) if isinstance(q,list) else str(q or '')))
 pubs=it.get('publication',[]);p0=next((p for p in pubs if p.get('@type')=='PrimaryPublication'),pubs[0] if pubs else {})
 co=p0.get('country') or {};co=co[0] if isinstance(co,list) and co else co;cc=co.get('code','') if isinstance(co,dict) else ''
 io=it.get('instanceOf',{});auth=[];con=[];corp=[]
 for c in io.get('contribution',[]):
  ag=c.get('agent',{});ag=ag if isinstance(ag,list) else [ag];r=(c.get('role') or {})
  rid=(r.get('@id','') if isinstance(r,dict) else '') or ''
  if isinstance(r,list):rid=' '.join(x.get('@id','') for x in r if isinstance(x,dict))
  for a in ag:
   if not isinstance(a,dict):continue
   if a.get('@type')=='Person':
    nm=tidy((a.get('familyName','')+', '+a.get('givenName','')) if a.get('familyName') else a.get('name',''))
    if not nm:continue
    isauth=c.get('@type')=='PrimaryContribution' or 'author' in rid or not rid
    (auth if isauth else con).append(nm)
   else:
    nm=tidy(a.get('name','') or lab(a))
    if nm and (c.get('@type')=='PrimaryContribution' or not rid):corp.append(nm)
 pubs_n=[tidy(x) for p in pubs if p.get('@type')=='PrimaryPublication' for x in ([lab(p['agent'])] if isinstance(p.get('agent'),dict) else [lab(a) for a in p.get('agent',[])]) if x]
 if not pubs_n:pubs_n=[tidy(lab(p['agent'])) for p in pubs if p.get('agent')]
 t=(it.get('hasTitle') or [{}])[0];notes=' ; '.join(lab(n) if isinstance(n,dict) else str(n) for n in it.get('hasNote',[]))
 ed=it.get('editionStatement','')
 langs=';'.join(l.get('code','') for l in io.get('language',[]))
 return base('se',record_id=it['@id'].rsplit('/',1)[-1],country_code=cc,country_eligible=cc=='sw',pub_year=year(str(p0.get('year',''))),title=tidy(t.get('mainTitle','')),
  publishers=pubs_n,place='; '.join(tidy(x) for pl in p0.get('place',[]) if isinstance(pl,dict) for x in pl.get('label',[])),authors_personal=auth,contributors_personal=con,authors_corporate=corp,
  isbn13s=vals,isbn_qualifiers=quals,is_print=True,record_type=io.get('@type',''),bib_level='m',language=langs,edition=tidy(ed if isinstance(ed,str) else ' '.join(ed)),notes=tidy(notes)[:300],
  is_published=io.get('@type')=='Monograph')
def main():
 sink=Sink('se');seen=set();dup=0
 for f in sorted(glob.glob(str(ROOT/'data/raw/libris/*/p*.json.gz'))):
  for it in json.load(gzip.open(f)).get('items',[]):
   if it['@id'] in seen:dup+=1;continue
   seen.add(it['@id']);sink.add(parse(it))
 print('dups',dup);sink.close()
if __name__=='__main__':
 if '--parse' in sys.argv or not (ROOT/'data/interim/se_catalogue.parquet').exists():main()
 import nordic_common as nc;nc.run('se','SWE','sweden')
