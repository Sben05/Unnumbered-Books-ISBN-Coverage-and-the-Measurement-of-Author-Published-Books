"""Download Norwegian National Library (nb.no catalog API) book records with a Norwegian-agency ISBN (978-82 / 82) by issued year.
The API caps paging at ~5,100 hits per query, so each (year, ISBN-prefix) slice is split recursively by next digit until <=4900 hits.
Saves data/raw/nb_no/<year>/<prefix>.jsonl.gz (raw item JSON, one per line); resumable."""
import json,gzip,time,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent.parent;RAW=ROOT/'data/raw/nb_no'
U='https://api.nb.no/catalog/v1/items?q=year:%d%%20isbn:%s*&filter=mediatype:b%%C3%%B8ker&size=%d&page=%d'
def get(url,tries=8):
 for i in range(tries):
  try:return json.loads(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'isbn-study-research/1.0'}),timeout=120).read())
  except Exception as e:time.sleep(2*(i+1))
 raise RuntimeError(url)
def leaves(y,prefix):
 n=get(U%(y,prefix,1,0))['page']['totalElements']
 if n==0:return []
 if n<=4900:return [(y,prefix,n)]
 out=[]
 for d in '0123456789':out+=leaves(y,prefix+d)
 return out
def fetch(job):
 y,prefix,n=job;p=RAW/str(y)/f'{prefix}.jsonl.gz'
 if p.exists():return n
 items=[];page=0
 while len(items)<n:
  d=get(U%(y,prefix,100,page));its=d.get('_embedded',{}).get('items',[])
  if not its:break
  items+=its;page+=1
 p.parent.mkdir(exist_ok=True);tmp=p.with_suffix('.tmp')
 tmp.write_bytes(gzip.compress('\n'.join(json.dumps(i,ensure_ascii=False) for i in items).encode()));tmp.replace(p)
 if len(items)<n:print('SHORT',y,prefix,len(items),n,flush=True)
 return len(items)
def year(y):
 jobs=[]
 for fam in ('97882','82'):jobs+=leaves(y,fam)
 tot=sum(j[2] for j in jobs);print(y,'leaves',len(jobs),'hits',tot,flush=True)
 return [fetch(j) for j in jobs]
if __name__=='__main__':
 with ThreadPoolExecutor(3) as ex:list(ex.map(year,range(1995,2024)))
 print('ALLDONE',flush=True)
