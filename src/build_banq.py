"""Parse BAnQ CSV conservatively; quarantine malformed rows, flag physical-print proxy."""
import sys,csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from study_common import *
def main():
 sink=Sink('qc');bad=[]
 path=sorted((ROOT/'data/raw/banq').glob('extract*.csv'))[-1]
 with path.open(encoding='cp1252',newline='') as f:
  reader=csv.reader(f);header=[x.strip() for x in next(reader)]
  for row in reader:
   if len(row)!=len(header):bad.append(dict(line=reader.line_num,field_count=len(row),raw_fields=row));continue
   x=dict(zip(header,row));get=lambda k:x.get('DC_'+k,'').strip()
   def person(prefix):
    surname=get(prefix+'__NOM');first=get(prefix+'__PRENOM')
    return (surname+', '+first if first else surname).strip()
   a=person('CREATOR');c=person('CONTRIBUTOR');p=get('PUBLISHER');dim=get('FORMAT__DIMENSIONS');pages=get('FORMAT__NBPAGES');genre=get('TYPE__GENRE');subject=get('SUBJECT');dewey=get('SUBJECT__CLASSIFICATION_DEWEY')
   ids,qs=isbn_pairs([(get('IDENTIFIER__ISBN'),'')]);title=get('TITLE')
   digital=bool(DIGITAL.search(dim+' '+pages+' '+genre+' '+subject));nonbook=bool(re.search(r'partitions?|musique not[eé]e|cartes g[eé]ographiques|atlas|enregistrements? sonores?|disques? compacts?|livres? audio',genre+' '+subject,re.I))
   nonbook = nonbook or dewey == 'Musique'
   print_ok=bool(re.search(r'\d\s*cm\b',dim,re.I)) and not (digital or nonbook or NONPRINT.search(dim+' '+pages))
   sink.add(base('qc',record_id=x['NO_SEQ'],country_code='QC_dataset_scope',country_eligible=True,pub_year=year(get('DATE_ISSUED')),title=title,publishers=[p] if p else [],authors_personal=[a] if a else [],contributors_personal=[c] if c else [],authors_corporate=[v for v in [get('CREATOR__GROUPE'),get('CONTRIBUTOR__GROUPE')] if v],carrier=genre,language=get('LANGUAGE'),physical_description=pages+' pages; '+dim,notes=subject+'; Dewey group='+dewey,record_type='',bib_level='',isbn13s=ids,isbn_qualifiers=qs,is_print=print_ok,is_published=get('TYPE__STATUT')=='PUBLIÉ',format_evidence='PROXY: dimensions in cm, non-book/digital exclusions; no MARC carrier supplied',role_uncertain=True))
 sink.close()
 with (ROOT/'output/selfpub/banq_malformed_rows.jsonl').open('w') as f:
  for r in bad:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 print('Quarantined',len(bad),'malformed rows')
if __name__=='__main__':main()
