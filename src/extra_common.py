"""Shared helpers for the extra-country builds (MARC21 -> common schema -> ISBN-level classification -> by-year tables).
Reuses norm/match_name (classify_selfpub), ap_consistent, study_common.Sink/base/isbn_pairs. Existing files are not modified."""
import sys,re,csv,math,json,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import numpy as np,pandas as pd
from study_common import Sink,base,isbn_pairs,tidy,year,DIGITAL,NONPRINT
from classify_selfpub import norm,match_name
from ap_consistent import ap_consistent,split_name

def low(s):
 s=unicodedata.normalize('NFKD',s or '');s=''.join(c for c in s if not unicodedata.combining(c)).lower().replace('ł','l').replace('đ','d');return s
def sub(f,code):return [tidy(x) for x in f.get_subfields(code)]
def marc_row(rec,source,cc,country_codes,ctry_pos=(15,18)):
 """One pymarc record -> common-schema row, or None. Print-monograph filtering is left to the caller via fields."""
 ld=rec.leader
 f008=rec['008'].data if rec['008'] else ''
 ctry=f008[ctry_pos[0]:ctry_pos[1]].strip() if len(f008)>=18 else ''
 form=f008[23] if len(f008)>23 else ''
 f1=rec['001'].data if rec['001'] else ''
 pairs=[]
 for f in rec.get_fields('020'):
  q=' '.join(sub(f,'q')+sub(f,'c')+sub(f,'z'))
  for a in sub(f,'a'):pairs.append((a,q))
 isbns,quals=isbn_pairs(pairs)
 pub=[];place=[];yr=None
 for f in rec.get_fields('260','264'):
  if f.tag=='264' and f.indicator2 not in('1',' ','\\'):continue
  pub+= [x for x in sub(f,'b')];place+=sub(f,'a')
  if yr is None:yr=year(' '.join(sub(f,'c')))
 if yr is None and len(f008)>=11 and f008[6] in 'sepqrt':yr=year(f008[7:11])
 a1=[];con=[];corp=[]
 AUTH=re.compile(r'^(?:autor|autorka|aut|spoluautor|wspolautor|współautor|author)',re.I)
 for f in rec.get_fields('100','700'):
  nm=tidy(' '.join(sub(f,'a')));rel=' '.join(sub(f,'e')+sub(f,'4'))
  if not nm:continue
  if f.tag=='100' or not rel or AUTH.match(rel) or rel.strip().lower()=='aut':a1.append(nm)
  else:con.append(nm)
 for f in rec.get_fields('110','710'):
  nm=tidy(' '.join(sub(f,'a')+sub(f,'b')))
  if nm:corp.append(nm)
 ext=' '.join(' '.join(sub(f,'a')) for f in rec.get_fields('300'))
 carrier=' '.join(' '.join(sub(f,'a')) for f in rec.get_fields('338'))+' '+' '.join(' '.join(sub(f,'a')) for f in rec.get_fields('337'))
 notes=' '.join(' '.join(sub(f,'a')) for f in rec.get_fields('500','502'))[:400]
 ed=' '.join(' '.join(sub(f,'a')) for f in rec.get_fields('250'))
 lang=f008[35:38] if len(f008)>=38 else ''
 title=tidy(' '.join(sub(rec['245'],'a'))) if rec['245'] else ''
 fe=[]
 if form in 'os' and form.strip():fe.append('008form='+form)
 if re.search(r'online|on-line|computer|internet|tiešsaistes|dators|elektron|zdroj online|online zdroj',carrier,re.I):fe.append('carrier')
 if any(f.data[:1]=='c' for f in rec.get_fields('007') if f.data):fe.append('007c')
 digital=bool(DIGITAL.search(' '.join(quals)+' '+ext)) or bool(fe)
 nonprint=bool(NONPRINT.search(ext+' '+carrier))
 r=base(source,record_id=f1,country_code=cc if ctry in country_codes else ctry,title=title,place='; '.join(place),record_type=ld[6],bib_level=ld[7],carrier=carrier.strip(),language=lang,
  physical_description=ext,edition=ed,notes=notes,format_evidence=';'.join(fe),authors_personal=a1,contributors_personal=con,authors_corporate=corp,publishers=[x for x in pub if x],
  isbn13s=isbns,isbn_qualifiers=quals,is_print=(not digital) and (not nonprint),country_eligible=ctry in country_codes,pub_year=yr)
 return r

# ---------- classification ----------
def make_classifier(lang_cfg):
 """lang_cfg: dict(part=set, corp=regex, explicit=regex, gov=regex, reprint=regex, services=list(dicts with regex,scope,tier,start_year,name_pattern), unid=regex)"""
 PART=lang_cfg['part'];CORP=lang_cfg['corp'];EXPL=lang_cfg['explicit'];GOV=lang_cfg['gov'];SERV=lang_cfg['services'];UNID=lang_cfg['unid'];REP=lang_cfg['reprint']
 def strip_part(t):return [x for x in t if x not in PART]
 def ap_match(author,pc):
  g,s=split_name(author);nat=' '.join(g+s)
  for a,p in ((nat,pc),(' '.join(strip_part(g+s)),' '.join(strip_part(pc.split())))):
   m=match_name(a,p)
   if m:return m
  return ''
 def flags(r):
  pubs=[x for x in r['publishers']];pub=tidy('; '.join(pubs));pub=re.sub(r'[\[\]]','',pub)
  pl=low(pub);pn=norm(pl,True);pc=norm(CORP.sub(' ',pn),True) if pn else ''
  auth=list(r['authors_personal']);con=list(r['contributors_personal']);corp=[low(c) for c in r['authors_corporate']]
  o={}
  o['unidentified_publisher']=(not pc) or bool(UNID.fullmatch(pl.strip()))
  expl=bool(EXPL.search(pl));ap=False;why=[]
  corp_self=any(norm(c,True)==pc and len(pc)>3 for c in corp)
  if expl and (auth or not corp):ap=True;why.append('explicit_author_statement')
  elif expl and corp:corp_self=True
  if pc and not o['unidentified_publisher']:
   for a in auth:
    m=ap_match(a,pc)
    if m:ap=True;why.append(m)
  o['ap_pure']=bool(pc) and not o['unidentified_publisher'] and any(ap_consistent(a,pc.split(),PART) for a in auth)
  o['ap_consistent']=ap or o['ap_pure']
  o['contributor_match']=bool(pc) and any(ap_match(a,pc) for a in con)
  svc=mixed=False;names=[];tiers=set()
  for s in SERV:
   if s['regex'].search(pl):
    names.append(s['name_pattern'])
    if s['scope']=='mixed':mixed=True
    else:
     if s['start_year'] and r['pub_year'] and int(r['pub_year'])<int(s['start_year']):continue
     svc=True;tiers.add(s['tier'])
  o.update(author_is_publisher=ap,service_imprint=svc,service_mixed=mixed,service_platform='platform' in tiers,service_author_services='author_services' in tiers,corporate_self=corp_self,
   self_published_combined=ap or svc,classification_reason=';'.join(sorted(set(why))),matched_services=';'.join(names),explicit=expl,publisher_clean=pub)
  o['government']=bool(GOV.search(pl)) or bool(GOV.search(' '.join(corp)))
  o['reprint']=bool(REP.search(low(r['edition'])+' '+low(r['notes'])[:200]))
  o['amazon_imprint']=bool(re.search(r'create\s?space|independently published|amazon',pl))
  return o
 return flags

def load_services(path):
 with open(path) as f:return [dict(x,regex=re.compile(x['name_pattern'])) for x in csv.DictReader(f)]

def classify_catalogue(cc,flags):
 """catalogue parquet -> ISBN-level classified parquet (best record per ISBN) + no-ISBN parquet."""
 df=pd.read_parquet(ROOT/f'data/interim/{cc}_catalogue.parquet')
 log={'records_total':len(df)}
 for c in 'authors_personal contributors_personal authors_corporate publishers isbn13s isbn_qualifiers'.split():df[c]=df[c].map(list)
 keep=df.is_print&df.country_eligible&(df.record_type=='a')&(df.bib_level=='m')
 for k,m in [('not_language_material_monograph',~((df.record_type=='a')&(df.bib_level=='m'))),('not_country',~df.country_eligible),('not_print',~df.is_print)]:log['excluded_'+k]=int(m.sum())
 d=df[keep].copy();log['records_print_monograph_country']=len(d);log['missing_pub_year']=int(d.pub_year.isna().sum())
 d['n_isbn']=d.isbn13s.map(len)
 d['score']=(d.publishers.map(len)>0).astype(int)*2+(d.authors_personal.map(len)>0).astype(int)*2+(d.title!='').astype(int)+d.pub_year.notna().astype(int)+(d.physical_description!='').astype(int)+(d.edition!='').astype(int)
 res=[];nn=[]
 cache={}
 d=d.reset_index(drop=True)
 recs=d.to_dict('records')
 best={}
 for i,r in enumerate(recs):
  if not r['isbn13s']:continue
  for k in r['isbn13s']:
   cur=best.get(k)
   if cur is None or (r['score'],-i)>(recs[cur]['score'],-cur):best[k]=i
 log['isbn_rows_before_dedup']=int(d.n_isbn.sum());log['isbn_rows_after_dedup']=len(best)
 need=set(best.values())|{i for i,r in enumerate(recs) if not r['isbn13s']}
 for i in need:
  r=recs[i];cache[i]=flags(r)
 for k,i in best.items():
  r=recs[i];o=dict(cache[i]);o.update(isbn13=k,record_id=r['record_id'],pub_year=r['pub_year'],title=r['title'],publisher_full='; '.join(r['publishers']),authors='; '.join(r['authors_personal']),edition=r['edition'],extent=r['physical_description'],lang=r['language'],notes=r['notes'][:300],place=r['place']);res.append(o)
 R=pd.DataFrame(res);R['pub_year']=R.pub_year.astype('Int64')
 R.to_parquet(ROOT/f'data/interim/{cc}_classified.parquet',compression='zstd')
 for i,r in enumerate(recs):
  if r['isbn13s']:continue
  o=cache[i];nn.append(dict(record_id=r['record_id'],pub_year=r['pub_year'],ap_consistent=o['ap_consistent'],author_is_publisher=o['author_is_publisher'],service_imprint=o['service_imprint'],self_published_combined=o['self_published_combined']))
 pd.DataFrame(nn,columns=['record_id','pub_year','ap_consistent','author_is_publisher','service_imprint','self_published_combined']).to_parquet(ROOT/f'data/interim/{cc}_noisbn.parquet')
 log['print_records_without_valid_isbn']=len(nn);log['classified_isbn_rows']=len(R)
 return R,log

# ---------- analysis ----------
def wilson(k,n):
 if not n:return (np.nan,np.nan)
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return c-h,c+h
def by_year(R,iso3,lo=1995,hi=2023):
 pop=pd.read_csv(ROOT/'config/population_official.csv');ex=ROOT/'config/population_extra.csv'
 if ex.exists():pop=pd.concat([pop,pd.read_csv(ex)]).drop_duplicates(['iso3','year'],keep='last')
 pop=pop[pop.iso3==iso3].set_index('year').population
 R=R[R.pub_year.between(lo,hi)].copy();R['pub_year']=R.pub_year.astype(int);rows=[]
 for y,g in R.groupby('pub_year'):
  n=len(g);r=dict(pub_year=y,print_isbns=n,ap_consistent=int(g.ap_consistent.sum()),ap_strict=int(g.author_is_publisher.sum()),service=int(g.service_imprint.sum()),combined=int(g.self_published_combined.sum()),
   explicit=int(g.explicit.sum()),government_not_counted=int(g.government.sum()),unidentified_publisher=int(g.unidentified_publisher.sum()))
  for c in ['ap_consistent','ap_strict','service','combined']:
   r['share_'+c]=r[c]/n;a,b=wilson(r[c],n);r[c+'_wilson_low']=a;r[c+'_wilson_high']=b
  P=pop.get(y,np.nan);r['population']=P
  r['print_isbns_per_million']=n/(P/1e6) if P==P else np.nan;r['combined_per_million']=r['combined']/(P/1e6) if P==P else np.nan
  r['ap_consistent_per_million']=r['ap_consistent']/(P/1e6) if P==P else np.nan
  rows.append(r)
 return pd.DataFrame(rows)
def validation_sample(R,out_csv,seed=20261109,n=60,col='self_published_combined'):
 rng=np.random.default_rng(seed);R=R[R.pub_year.between(1995,2023)]
 pos=R[R[col]];neg=R[~R[col]]
 a=pos.iloc[rng.choice(len(pos),min(n,len(pos)),replace=False)].assign(sample='flagged');b=neg.iloc[rng.choice(len(neg),n,replace=False)].assign(sample='unflagged')
 S=pd.concat([a,b])[['sample','isbn13','pub_year','title','authors','publisher_full','place','edition','notes',col,'classification_reason','matched_services']].reset_index(drop=True)
 S['gold_self_published']='';S['comment']='';S.to_csv(out_csv,index=False);return S
