"""Poland (Biblioteka Narodowa national bibliography, MARC21, CC0): print monographs published in PL -> common schema -> ISBN-level self-publication classification.
usage: build_pl.py [parse|classify|all] [max_records]   (run with .venv/bin/python -I)"""
import sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import json
from extra_common import *
from pymarc import MARCReader
import os
SRC=Path(os.environ.get('PL_SRC',str(ROOT/'data/raw/poland_bn/bibs-ksiazka.marc')))
OUT=ROOT/'output/poland';OUT.mkdir(parents=True,exist_ok=True)
CFG=dict(part={'de','van','von','di','da','del','la','le'},
 corp=re.compile(r'\b(?:wydawnictwo|wydawnictwa|wydawnicza|wydawniczy|wyd|wydawca|oficyna|dom|firma|agencja|studio|pracownia|biuro|sp|z o o|spolka|sc|sj|ska|zaklad|edycja)\b'),
 explicit=re.compile(r"\bnakladem (?:wlasnym|autora|autorki|autorow)\b|\bwlasnym nakladem\b|\bwydanie wlasne\b|\bwydawnictwo wlasne\b|\bwlasne wydawnictwo\b|\bwyd\.? wlasne\b|\b(?:wlasnym )?sumptem (?:wlasnym|autora)\b|\bwlasnym sumptem\b|^autor$|^autorka$|^autorzy$|\bwyd\.? autora\b|\bwydawnictwo autora\b|\bwydanie autorskie\b|\bedycja autorska\b|\bwydawnictwo autorskie\b|self.?publish\w*|^wlasne$|^wlasny$|\bsamizdat\b|\bautor wydawca\b|\bwydawca autor\b|\bwydane przez autora\b"),
 gov=re.compile(r'\b(?:ministerstwo|urzad|starostwo|gmina|wojewodztwo|sejm|senat|rzad|kancelaria|powiat|miasto|gminny|miejski|miejska|komenda)\b'),
 reprint=re.compile(r'\bwyd\.? ?[2-9]\b|\b[2-9]\.? wyd|popraw|zmienion|uzupel|przedruk|wznow|reprint|dodruk'),
 unid=re.compile(r"s\W*n\W*|b\W*w\W*|b\W*m\W*w\W*|bez wydawcy|brak wydawcy|s\W*l\W*|nieznany|\[?b\.? ?m\.? ?w\.?\]?"),
 services=load_services(ROOT/'config/selfpub_services_pl.csv'))
def parse(limit=None):
 sk=Sink('pl');n=0;kept=0
 with open(SRC,'rb') as f:
  for rec in MARCReader(f,to_unicode=True,force_utf8=True,permissive=True):
   if rec is None:continue
   n+=1
   if limit and n>limit:break
   r=marc_row(rec,'bn_pl','PL',{'pl'})
   if r:sk.add(r);kept+=1
   if n%500000==0:print(n,kept,flush=True)
 sk.close();print('records read',n)
def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in('parse','all'):parse(int(sys.argv[2]) if len(sys.argv)>2 else None)
 if mode in('classify','all'):
  R,log=classify_catalogue('pl',make_classifier(CFG))
  json.dump(log,open(OUT/'build_log.json','w'),indent=1);print(json.dumps(log,indent=1))
if __name__=='__main__':main()
