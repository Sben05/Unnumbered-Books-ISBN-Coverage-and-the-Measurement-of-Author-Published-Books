"""Immutable, resumable downloads with SHA256 provenance. Run with python -I."""
import hashlib,json,os,time
from pathlib import Path
from datetime import datetime,timezone
import requests
ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'data/raw/download_manifest.jsonl'
def download(url,relative,licence='',source=''):
 path=ROOT/relative;path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  print('Already present:',path.name,flush=True);return path
 tmp=path.with_suffix(path.suffix+'.part')
 with requests.get(url,stream=True,timeout=(30,180)) as r:
  r.raise_for_status()
  with tmp.open('wb') as f:
   for block in r.iter_content(4*1024*1024):f.write(block)
 tmp.rename(path)
 record(path,url,licence,source)
 print('Downloaded',path.name,path.stat().st_size,flush=True);return path
def record(path,url,licence,source):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 row=dict(path=str(path.relative_to(ROOT)),url=url,retrieved_utc=datetime.now(timezone.utc).isoformat(),bytes=path.stat().st_size,sha256=h.hexdigest(),licence=licence,source=source)
 with MANIFEST.open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('path');p.add_argument('--licence',default='');p.add_argument('--source',default='');a=p.parse_args();download(a.url,a.path,a.licence,a.source)
