"""Download the public BnF retrospective books UNIMARC/UTF8 product via its public form."""
import sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import requests
from bs4 import BeautifulSoup
from lxml import etree
from acquire_selfpub import record
LINK='https://transfert.bnf.fr/link/c06ebbc0-5dd9-44e8-966b-56c91dcf59c5'
POST='https://transfert.bnf.fr/webclient/godrive/PublicGoDrive.xhtml'
def main():
 s=requests.Session();r=s.get(LINK,timeout=60);soup=BeautifulSoup(r.text,'html.parser');vs=soup.select_one('input[name="javax.faces.ViewState"]')['value']
 for folder in ['BNF-Livres_2025','BNF-Livres_2025_Unimarc_UTF8']:
  a=next(a for a in soup.select('a') if a.get_text()==folder);key=a['id']
  r=s.post(POST,data={'javax.faces.partial.ajax':'true','javax.faces.source':key,'javax.faces.partial.execute':'@all','javax.faces.partial.render':'breadcrumbForm fileList toolbarForm messages',key:key,'fileList_SUBMIT':'1','javax.faces.ViewState':vs},headers={'Faces-Request':'partial/ajax'},timeout=60)
  tree=etree.fromstring(r.content);vs=tree.xpath('//update[contains(@id,"ViewState")]/text()')[0];soup=BeautifulSoup(''.join(tree.xpath('//update[@id="fileList"]/text()')),'html.parser')
 files=[(a['id'],a.get_text()) for a in soup.select('a') if '.UTF8' in a.get_text()]
 for key,name in files:
  dest=ROOT/'data/raw/bnf'/name
  if dest.exists():continue
  for attempt in range(3):
   try:
    with s.post(POST,data={key:key,'fileList_SUBMIT':'1','javax.faces.ViewState':vs},stream=True,timeout=(30,180)) as r:
     r.raise_for_status()
     if 'html' in r.headers.get('Content-Type',''):raise ValueError('Unexpected HTML download')
     tmp=dest.with_suffix(dest.suffix+'.part')
     with tmp.open('wb') as f:
      for b in r.iter_content(4*1024*1024):f.write(b)
     tmp.rename(dest)
    record(dest,LINK,'Licence Ouverte de l’État','Bibliothèque nationale de France; BNF-Livres_2025_Unimarc_UTF8')
    print(name,dest.stat().st_size,flush=True);break
   except Exception as e:
    print('retry',name,repr(e),flush=True)
    if attempt==2:raise
    time.sleep(3)
if __name__=='__main__':main()
