"""Second wave (adds ~900 books; same matching rule). Visibility test with the Google Books API (key from env GOOGLE_BOOKS_API_KEY; never stored in files).
Stratified sample of BNP national-bibliography books (Portuguese print, 2010-2019): self-published (AP) and other, with/without ISBN, pre/post 2015.
For each book query intitle (+inauthor). Strict match = normalised-title token Jaccard >=0.75 AND author surname in volume authors (when known) AND year within +/-1 (when Google gives one).
Outcome: found; found with an ISBN in Google; found and 'for sale'. Resume-safe cache: data/interim/gb_cache.jsonl."""
import os, re, json, time, unicodedata, urllib.parse, urllib.request, pandas as pd, numpy as np
KEY=os.environ['GOOGLE_BOOKS_API_KEY']
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2010,2019)].copy()
raw=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','a700']); raw['id']=raw.id.astype(str); R=R.merge(raw,on='id',how='left')
def norm(s): s=unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s)).strip()
def sur(a):
    try: l=json.loads(a)
    except Exception: return ''
    return norm(l[0].get('a','').split(',')[0]) if l else ''
R['sur']=R.a700.map(sur); R['tn']=R.title.map(norm); R=R[R.tn.str.len()>=10]
R['grp']=np.where(R.ap,'AP','other')+'|'+np.where(R.has_isbn,'ISBN','noISBN')+'|'+np.where(R.pub_year<=2014,'pre','post')
R['cell']=np.where(R.ap,'AP','other')+'|'+np.where(R.has_isbn,'ISBN','noISBN')
import os as _os
done=set()
if _os.path.exists('data/interim/gb_cache.jsonl'):
    for l in open('data/interim/gb_cache.jsonl'): done.add(json.loads(l)['id'])
extra={'AP|ISBN':300,'AP|noISBN':300,'other|ISBN':150,'other|noISBN':150}
S=pd.concat([g[~g.id.isin(done)].sample(min(len(g[~g.id.isin(done)]),extra[k]),random_state=23) for k,g in R.groupby('cell')])
cache={}
if os.path.exists('data/interim/gb_cache.jsonl'):
    for l in open('data/interim/gb_cache.jsonl'): d=json.loads(l); cache[d['id']]=d
def query(r):
    q='intitle:"%s"'%r.title[:70].replace('"','')
    if r.sur: q+=' inauthor:'+r.sur.split()[-1]
    url='https://www.googleapis.com/books/v1/volumes?'+urllib.parse.urlencode({'q':q,'maxResults':10,'key':KEY,'printType':'books'})
    for k in range(8):
        try:
            with urllib.request.urlopen(url,timeout=30) as f: return json.load(f)
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(35); continue      # per-minute limit: wait and retry
            time.sleep(2)
        except Exception: time.sleep(2)
    return {'_quota':True}
def jac(a,b):
    A,B=set(a.split()),set(b.split()); return len(A&B)/max(1,len(A|B))
out=open('data/interim/gb_cache.jsonl','a'); done=0
for r in S.itertuples():
    if r.id in cache: continue
    d=query(r)
    if d.get('_quota'): print('QUOTA hit after',done,'queries'); break
    found=fi=fs=0
    for it in d.get('items',[]) or []:
        v=it.get('volumeInfo',{}); t=norm(v.get('title','')+' '+v.get('subtitle',''))
        if jac(r.tn,t)<0.75 and not (r.tn in t or t in r.tn and len(t)>12): continue
        if r.sur and r.sur.split()[-1] not in norm(' '.join(v.get('authors',[]) or [])): continue
        m=re.search(r'(19|20)\d\d',str(v.get('publishedDate','')))
        if m and abs(int(m.group())-int(r.pub_year))>1: continue
        found=1; fi=max(fi,int(any(i.get('type','').startswith('ISBN') for i in v.get('industryIdentifiers',[])))); fs=max(fs,int(it.get('saleInfo',{}).get('saleability')=='FOR_SALE'))
    rec=dict(id=r.id,grp=r.grp,year=int(r.pub_year),total=d.get('totalItems',0),found=found,found_isbn=fi,for_sale=fs,err=bool(d.get('_err')))
    out.write(json.dumps(rec)+'\n'); out.flush(); cache[r.id]=rec; done+=1; time.sleep(1.0)
print('queries this run',done,'| total cached',len(cache))
