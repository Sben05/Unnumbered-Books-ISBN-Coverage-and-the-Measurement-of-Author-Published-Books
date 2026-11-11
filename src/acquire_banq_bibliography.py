"""Download annual public bibliographies for print/carrier verification of CSV rows."""
import sys,concurrent.futures,time,json
from pathlib import Path
from urllib.parse import urljoin
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from bs4 import BeautifulSoup
from acquire_selfpub import download
BASE='https://www2.banq.qc.ca/ressources_en_ligne/bibliographie_quebec/'
def work(task):
 y,name=task;url=BASE+f'refonte_{y}/'+name
 try:return str(download(url,f'data/raw/banq_bibliography/{y}/{name}','BAnQ public bibliography; metadata reuse attributed','Bibliothèque et Archives nationales du Québec'))
 except Exception as e:return f'ERROR {y}/{name}: {e}'
def main():
 tasks=[]
 for y in range(2010,2025):
  work((y,'tdm_index.html'))
  p=ROOT/f'data/raw/banq_bibliography/{y}/tdm_index.html'
  soup=BeautifulSoup(p.read_bytes(),'html.parser')
  names=sorted({a['href'] for a in soup.select('a[href]') if a['href'].startswith('tdm') and a['href']!='tdm_index.html'})
  tasks.extend((y,n) for n in names)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(work,tasks):print(r,flush=True)
if __name__=='__main__':main()
