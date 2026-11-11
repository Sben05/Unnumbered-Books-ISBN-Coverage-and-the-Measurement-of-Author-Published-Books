"""Require independent catalogue print evidence and identifiable Québec publication place."""
import sys,re,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from classify_selfpub import raw_norm
from enrich_banq import publication_place
NAMES=set((ROOT/'config/quebec_place_names.txt').read_text().splitlines())
def place_norm(s):
 s=re.sub(r'\([^)]*\)',' ',s);s=raw_norm(s)
 s=re.sub(r'\bst\b','saint',s);s=re.sub(r'\bste\b','sainte',s)
 return s
OTHER=re.compile(r'\b(?:ontario|ont\b|ottawa|toronto|moncton|nouveau brunswick|n b|new brunswick|manitoba|vancouver|british columbia|saskatchewan|alberta|nouvelle ecosse|nova scotia|france|belgique|suisse|new york|paris|arles|lyon|bruxelles|lausanne|london|halifax)\b')
def geography(place):
 if not place:return 'missing'
 raw=raw_norm(place)
 # Co-publication is eligible when Québec is explicit in a semicolon-separated place.
 for part in place.split(';'):
  s=raw_norm(part)
  if re.search(r'\bquebec\b|\bque\b|\bqc\b',s):return 'QC_explicit'
  if OTHER.search(s):continue
  cleaned=place_norm(part).strip()
  if cleaned in NAMES and cleaned not in ('canada','province'):return 'QC_gazetteer'
  # Remove a trailing country but do not strip province conflicts.
  cleaned=re.sub(r'\s+canada$','',cleaned)
  if cleaned in NAMES and cleaned not in ('canada','province'):return 'QC_gazetteer'
 if OTHER.search(raw):return 'outside_QC'
 return 'unresolved'
def main():
 original=ROOT/'data/interim/qc_catalogue.parquet';d=pd.read_parquet(original)
 proxy=d['print_proxy'].copy() if 'print_proxy' in d else d.is_print.copy()
 # Preserve the original proxy when rerunning derived enrichment.
 for c in ['verified_print','full_description','verified_place','category','evidence_url','bibliography_year','print_proxy','geography_check','bibliography_matched']:
  if c in d:d=d.drop(columns=c)
 ev=pd.read_parquet(ROOT/'data/interim/qc_bibliography_evidence.parquet').sort_values('bibliography_year').drop_duplicates('record_id',keep='last')
 ev['verified_place']=ev.full_description.map(publication_place)
 d=d.merge(ev,on='record_id',how='left',validate='many_to_one')
 d['print_proxy']=proxy;d['bibliography_matched']=d.full_description.notna()
 d['geography_check']=d.verified_place.fillna('').map(geography)
 d['country_eligible']=d.geography_check.isin(['QC_explicit','QC_gazetteer']);d['country_code']=d.geography_check
 d['is_print']=d.verified_print.fillna(False).astype(bool)
 d['place']=d.verified_place.fillna('');d['physical_description']=d.full_description.fillna(d.physical_description)
 d['format_evidence']='BAnQ annual catalogue category and full physical description; absent evidence excluded'
 # ISBN-specific digital qualifications: a record can list multiple formats.
 def qualifiers(r):
  text=r.full_description if isinstance(r.full_description,str) else ''
  result=[]
  for isbn in r.isbn13s:
   pattern=r'ISBN\s*'+r'[\s\-]*'.join(isbn)+r'\s*(\([^)]*\))?'
   m=re.search(pattern,text,re.I);result.append(m.group(1) or '' if m else '')
  return result
 d['isbn_qualifiers']=d.apply(qualifiers,axis=1)
 d.to_parquet(original,index=False)
 d.groupby(['pub_year','bibliography_matched','geography_check','is_print'],dropna=False).size().rename('records').to_csv(ROOT/'output/selfpub/qc_geography_format_audit.csv')
 pd.DataFrame(d[['verified_place','geography_check']].value_counts()).to_csv(ROOT/'output/selfpub/qc_place_decisions.csv')
 print(d.geography_check.value_counts().to_dict());print('Matched',int(d.bibliography_matched.sum()),'of',len(d),'strict print QC',int((d.country_eligible & d.is_print).sum()))
if __name__=='__main__':main()
