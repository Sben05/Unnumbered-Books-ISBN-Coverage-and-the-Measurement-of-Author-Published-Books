"""Join full annual catalogue descriptions to CSV IDs for carrier and publication-place checks."""
import sys,re,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from bs4 import BeautifulSoup
from study_common import isbn_pairs
from classify_selfpub import norm
EXCLUDED={'tdmATL','tdmCAR','tdmM61','tdmM62','tdmM63','tdmM64','tdmM66','tdmM67','tdmM68','tdmM7','tdmas','tdmDEL','tdmREL','tdmREO','tdmREP','tdmAFF','tdmCPO'}
def publication_place(txt):
 statements=[s for s in txt.split('—')[1:] if ':' in s and re.search(r'\b(?:19|20)\d{2}\b',s)]
 for s in statements:
  place=s.split(':')[0].strip(' [].,;')
  if re.search(r'edition|édition|edicion|edición|auflage|izdanie|editie|commence|mise à jour|revision|révision|actualiza',place,re.I):continue
  return re.sub(r'\s*\[?etc\.?$', '',place,flags=re.I).strip(' [].,;')
 return ''
def main():
 rows=[]
 for path in sorted((ROOT/'data/raw/banq_bibliography').glob('*/*.html')):
  if path.name=='tdm_index.html':continue
  soup=BeautifulSoup(path.read_bytes(),'html.parser')
  for span in soup.select('.BIB-ISBD-RECORD'):
   recall=span.find_next(class_='BIB-RECALL-RECORD')
   if recall is None or not recall.select('td'):continue
   rid=recall.select('td')[-1].get_text(strip=True)
   if not re.fullmatch(r'\d+',rid):continue
   txt=span.get_text(' ',strip=True)
   # First publication statement after the title/responsibility: place : publisher, year.
   statements=[s for s in txt.split('—')[1:] if ':' in s and re.search(r'\b(?:19|20)\d{2}\b',s)]
   place=publication_place(txt)
   nonprint=path.stem in EXCLUDED or bool(re.search(r'\[(?:musique imprim[eé]e|musique not[eé]e|enregistrement sonore|ressource [eé]lectronique|document [eé]lectronique|document cartographique)\]|\b\d+ partitions?\b|\b\d+ parties?\b|\b\d+ ressources? en ligne\b|\b\d+ disques? (?:sonores?|compacts?)\b',txt,re.I))
   print_ok=not nonprint and bool(re.search(r'\b(?:pages?|p\.|volumes?|vol\.|v\.)',txt,re.I))
   rows.append(dict(record_id=rid,bibliography_year=int(path.parent.name),verified_print=print_ok,full_description=txt,verified_place=place,category=path.stem,evidence_url='https://www2.banq.qc.ca/ressources_en_ligne/bibliographie_quebec/refonte_'+path.parent.name+'/'+path.name))
  if len(rows)%10000<500:print(path,len(rows),flush=True)
 df=pd.DataFrame(rows);df.to_parquet(ROOT/'data/interim/qc_bibliography_evidence.parquet',index=False)
 df.groupby('verified_place').size().sort_values(ascending=False).to_csv(ROOT/'output/selfpub/qc_places.csv')
 print('Evidence records',len(df),'distinct',df.record_id.nunique(),flush=True)
if __name__=='__main__':main()
