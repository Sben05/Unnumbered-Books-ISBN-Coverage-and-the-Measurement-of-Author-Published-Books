"""Latvia (National Library of Latvia national bibliography 2014-2023, MARC21XML, CC0; https://dati.lnb.lv): print monographs -> common schema -> classification.
usage: build_lv.py [parse|classify|all]  (.venv/bin/python -I)"""
import sys,re,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from extra_common import *
import pymarc
SRC=ROOT/'data/raw/latvia_lnb/data/natl_bibliography-2014-2023-marc.xml';OUT=ROOT/'output/latvia';OUT.mkdir(parents=True,exist_ok=True)
CFG=dict(part={'de','van','von','di','da','la','le'},
 corp=re.compile(r'\b(?:apgads|izdevnieciba|izdevejs|izdevums|sia|as|biedriba|studija|birojs|fonds|z s|ik|sabiedriba)\b'),
 explicit=re.compile(r"\bautora (?:izdevums|apgads|izdevumi|izdevumos)\b|\bpasizdevums\b|\bpasizdots\b|^autors$|^autore$|^autori$|\bizdevejs autors\b|\bautora (?:privatizdevums|paša izdevums)\b|self.?publish\w*|\bpasizdevnieciba\b|\bizdots uz autora rekina\b|\bautora rekina\b"),
 gov=re.compile(r'\b(?:ministrija|pasvaldiba|dome|valsts|saeima|vaditaja|parvalde|agentura|centrs)\b'),
 reprint=re.compile(r'\b[2-9]\.? ?(?:izd|papild|labots)|papildinat|labots|pārstrād|parstrad|atkartots|reprint'),
 unid=re.compile(r"s\W*n\W*|nezinams|trukst|\[?b\W*i\W*\]?"),
 services=load_services(ROOT/'config/selfpub_services_lv.csv'))
def recs():
 from lxml import etree
 NS='{http://www.loc.gov/MARC21/slim}'
 for _,el in etree.iterparse(str(SRC),tag=NS+'record'):
  r=pymarc.Record()
  ld=(el.findtext(NS+'leader') or '').ljust(24)[:24]
  try:r.leader=pymarc.Leader(ld)
  except Exception:r.leader=pymarc.Leader(ld[:5]+'n'+ld[6:])
  for c in el:
   t=c.tag.replace(NS,'')
   if t=='controlfield':r.add_field(pymarc.Field(tag=c.get('tag'),data=c.text or ''))
   elif t=='datafield':
    r.add_field(pymarc.Field(tag=c.get('tag'),indicators=[c.get('ind1') or ' ',c.get('ind2') or ' '],subfields=[pymarc.Subfield(code=x.get('code'),value=x.text or '') for x in c if x.tag==NS+'subfield']))
  yield r
  el.clear()
def parse():
 sk=Sink('lv');n=0
 for rec in recs():
  n+=1;r=marc_row(rec,'lnb_lv','LV',{'lv'})
  if r:sk.add(r)
 sk.close();print('records read',n)
def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in('parse','all'):parse()
 if mode in('classify','all'):
  R,log=classify_catalogue('lv',make_classifier(CFG));json.dump(log,open(OUT/'build_log.json','w'),indent=1);print(json.dumps(log,indent=1))
if __name__=='__main__':main()
