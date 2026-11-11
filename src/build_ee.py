"""Estonia (National Library of Estonia, curated Estonian National Bibliography - books, CC BY 4.0): publications with place-of-publication country 'er' -> common schema -> classification.
usage: build_ee.py [parse|classify|all]  (.venv/bin/python -I)"""
import sys,re,json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from extra_common import *
SRC=ROOT/'data/raw/estonia_enb/enb_books.tsv';OUT=ROOT/'output/estonia';OUT.mkdir(parents=True,exist_ok=True)
CFG=dict(part={'de','van','von','di','da','la','le'},
 corp=re.compile(r'\b(?:kirjastus|kirjastuse|kirjastajad|kirjastaja|ou|as|mtu|fie|tu|trukikoda|trykikoda|ltd|oy)\b'),
 explicit=re.compile(r"\bautori (?:kulul|valjaanne|kirjastus|omakirjastus|poolt|valjaandel)\b|\bautor(?:i)? kirjastus\b|\bomal kulul\b|\bomakirjastus\b|\bautoriv(?:aljaanne)\b|^autor$|^autorid$|\bisekirjastus\b|self.?publish\w*|\bkirjastaja autor\b|\bautori kulul\b|\bautori omal kulul\b|^omavaljaanne$|\bomavaljaanne\b"),
 gov=re.compile(r'\b(?:ministeerium|vabariigi valitsus|riigikogu|linnavalitsus|vallavalitsus|maavalitsus|amet|riigi|linnakantselei)\b'),
 reprint=re.compile(r'\b[2-9]\.? ?(?:tr|trukk|ilmumine|vaide|taiend)|parand|taiend|kordustrukk|reprint|uustrukk'),
 unid=re.compile(r"s\W*n\W*|tundmatu|puudub|\[?s\W*l\W*\]?"),
 services=load_services(ROOT/'config/selfpub_services_ee.csv'))
def parse():
 import pandas as pd
 sk=Sink('ee');n=0
 for ch in pd.read_csv(SRC,sep='\t',dtype=str,keep_default_na=False,chunksize=100000,quoting=csv.QUOTE_MINIMAL,on_bad_lines='warn'):
  ch.columns=[c.strip() for c in ch.columns]
  for d in ch.to_dict('records'):
   n+=1
   pub=[x.strip() for x in re.split(r'\s*;\s*',d['publisher']) if x.strip()] if d['publisher'] else []
   cre=[re.sub(r'\s*\(.*?\)|\s*\[.*?\]','',d['creator']).strip()] if d['creator'] else []
   au=list(cre);co=[]
   for c in [x.strip() for x in d['contributor'].split('; ') if x.strip()]:
    if ':' in c:continue
    nm=re.sub(r'\s*\(.*?\)|\s*\[.*?\]','',c).strip();role=re.findall(r'\[(.*?)\]',c)
    (au if role==['autor'] else co).append(nm)
   toks=[(x,'') for x in re.findall(r'[0-9][0-9Xx\- ]{8,16}[0-9Xx]',d['isbn'])]
   isbns,quals=isbn_pairs(toks)
   yr=year(d['publication_date_cleaned']) or year(d['publication_date'])
   r=base('enb_ee',record_id=d['id'],country_code='EE',title=d['title'],place=d['publication_place'],record_type='a',bib_level='m',language=d['language'],physical_description=d['page_count'],edition=d['edition_statement'],
    authors_personal=au,contributors_personal=co,authors_corporate=[x for x in [d['corporate_unit']] if x],publishers=pub,isbn13s=isbns,isbn_qualifiers=quals,pub_year=yr,
    country_eligible=d['publication_place_control'].strip()=='er',is_print=not(d['is_digitized']=='True' and not d['page_count']) and not re.search(r'digira|e-?raamat',d['publisher'],re.I))
   sk.add(r)
 sk.close();print('rows',n)
def main():
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in('parse','all'):parse()
 if mode in('classify','all'):
  R,log=classify_catalogue('ee',make_classifier(CFG));json.dump(log,open(OUT/'build_log.json','w'),indent=1);print(json.dumps(log,indent=1))
if __name__=='__main__':main()
