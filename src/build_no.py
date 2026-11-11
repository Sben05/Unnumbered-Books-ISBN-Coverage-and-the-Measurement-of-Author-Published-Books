"""Norway (nb.no catalogue API, books with Norwegian-agency ISBN 978-82/82) -> data/interim/no_catalogue.parquet (common schema), then classify/analyse."""
import sys,gzip,json,glob,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from study_common import Sink,base,tidy,year
from build_2025 import clean_isbns
def person(n):return ',' in n and not re.search(r'\b(?:forlag|institutt|høgskole|universitet|selskap|forening|kommune|departement|bibliotek|museum|stiftelse|lag|råd|norges|norsk|ab|as|a/s)\b',n,re.I)
def parse(it):
 m=it['metadata'];ids=m.get('identifiers',{});raw=(ids.get('isbn13') or [])+(ids.get('isbn10') or [])
 isb=clean_isbns([],[])
 isb=clean_isbns(ids.get('isbn13') or [],ids.get('isbn10') or [])
 oi=m.get('originInfo',{});cr=m.get('creators') or []
 auth=[tidy(c) for c in cr if person(c)];corp=[tidy(c) for c in cr if not person(c)]
 y=year(oi.get('issued',''))
 return base('no',record_id=it['id'],country_code='NO' if any(i.startswith('97882') for i in isb) else '',country_eligible=any(i.startswith('97882') for i in isb),pub_year=y,
  title=tidy(m.get('title','')),publishers=[tidy(oi['publisher'])] if oi.get('publisher') else [],place=tidy((m.get('geographic') or {}).get('city','')),
  authors_personal=auth,authors_corporate=corp,isbn13s=isb,isbn_qualifiers=['']*len(isb),is_print=True,record_type='book',bib_level='m',
  language=';'.join(l.get('code','') for l in m.get('languages',[])),notes=tidy('; '.join(m.get('series') and [str(s) for s in m['series']] or []))[:200])
def main():
 sink=Sink('no');seen=set();dup=0
 for f in sorted(glob.glob(str(ROOT/'data/raw/nb_no/*/*.jsonl.gz'))):
  for l in gzip.open(f,'rt'):
   it=json.loads(l)
   if it['id'] in seen:dup+=1;continue
   seen.add(it['id']);sink.add(parse(it))
 print('duplicate item ids across slices',dup);sink.close()
if __name__=='__main__':
 if '--parse' in sys.argv or not (ROOT/'data/interim/no_catalogue.parquet').exists():main()
 import nordic_common as nc;nc.run('no','NOR','norway')
