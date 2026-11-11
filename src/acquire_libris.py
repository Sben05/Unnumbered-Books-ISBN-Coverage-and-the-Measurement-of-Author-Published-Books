"""Download Svensk bibliografi (Libris 'NB' bibliography) print PhysicalResource records by publication year via the Libris XL find API.
Sorted by meta.controlNumber (default order is unstable across pages and loses ~30% of records). Saves each 200-record page as gzip JSON in data/raw/libris/<year>/p<NNNN>.json.gz; resumable; threaded."""
import sys,json,gzip,time,urllib.request,urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent.parent;RAW=ROOT/'data/raw/libris'
BASE='https://libris.kb.se/find.jsonld?q=*&and-meta.bibliography.@id=https://libris.kb.se/library/NB&and-publication.year=%d&@type=PhysicalResource&and-category.@id=https://id.kb.se/term/saobf/Print&_limit=200&_sort=meta.controlNumber&_offset=%d'
def get(url,tries=8):
 for i in range(tries):
  try:
   req=urllib.request.Request(url,headers={'Accept':'application/ld+json','User-Agent':'isbn-study-research/1.0'})
   b=urllib.request.urlopen(req,timeout=180).read();d=json.loads(b);return d
  except Exception as e:
   time.sleep(3*(i+1))
 raise RuntimeError(url)
def page(args):
 y,off=args;p=RAW/str(y)/f'p{off//200:04d}.json.gz'
 if p.exists():return 0
 d=get(BASE%(y,off));p.parent.mkdir(exist_ok=True)
 tmp=p.with_suffix('.tmp');tmp.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False).encode()));tmp.replace(p);return len(d['items'])
def main():
 jobs=[]
 for y in range(1995,2024):
  d=get((BASE%(y,0)).replace('_limit=200','_limit=1'));n=d['totalItems'];print(y,n,flush=True)
  jobs+=[(y,o) for o in range(0,n,200)]
 with ThreadPoolExecutor(14) as ex:
  for i,r in enumerate(ex.map(page,jobs)):
   if i%50==0:print('done',i,len(jobs),flush=True)
 print('ALLDONE',flush=True)
if __name__=='__main__':main()
