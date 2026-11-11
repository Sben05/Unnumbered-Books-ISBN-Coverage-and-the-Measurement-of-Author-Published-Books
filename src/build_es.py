"""Spain (BNE monographs 2007-2022): parse, filter to print books, one row per valid ISBN-13, classify self-publication.
Reuses norm/match_name/service logic from classify_selfpub.py; adds Spanish name and phrase rules."""
import sys,re,csv,json,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from build_2025 import clean_isbns
from classify_selfpub import norm,match_name
OUT=ROOT/'output/spain';OUT.mkdir(parents=True,exist_ok=True)
def low(s):
 s=unicodedata.normalize('NFKD',s or '');return ''.join(c for c in s if not unicodedata.combining(c)).lower()
PART={'de','del','la','las','los','y','e','i','da','do','dos','van','von','el','di'}
CORP=re.compile(r'\b(?:s l u|s l|s a|s c|sl|sa|slu|sau|editorial|editores|editor|ediciones|edicions|edicion|ed|edic|publicaciones|producciones|grupo)\b')
EXPL=re.compile(r"\b(?:el|la|los|las) (?:autor|autora|autores|autoras)\b|\bautor[- ]editor\b|\bautoedic\w*|\bautoeditad\w*|\bautoeditor\w*|\bautopublic\w*|\ba cuenta (?:del|de) (?:el )?autor\b|\b(?:edicion|ediciones|editado|publicado|publicacion) (?:del|de la|por el|por la|por los) (?:autor|autora|autores)\b|\bpor (?:el|la) autor")
GOV=re.compile(r'\b(?:ministerio|ministeri|gobierno|govern|xunta|junta de|generalitat|diputacion|diputacio|ayuntamiento|ajuntament|concello|cabildo|consejeria|conselleria|comunidad de madrid|comunidad autonoma|parlamento|parlament|cortes|senado|congreso de los diputados|boletin oficial|instituto nacional|agencia estatal|eusko jaurlaritza|departamento de|departament de|mancomunidad|consell insular|consell comarcal)\b')
REPRINT=re.compile(r'reimpr|reedic|reeditad|nueva edicion|nova edicio|revisad|revisat|ampliad|ampliat|corregid|corregit|actualizad|actualitzat|\b(?:segunda|tercera|cuarta|quinta|sexta|septima|octava|novena|decima|segona|quarta|cinquena)\b|\b(?:[2-9]|1\d)\s*[aªº°n]?\s*(?:ed|edic|edici|edicion|edicio)\b')
NONPRINT=re.compile(r'^\s*(?:\d+\s+)?(?:cd|dvd|disco|casete|cinta|video|microficha|disquete|recurso|mapa|cartel|partitura|diapositiva|archivo)')
ISBN_RE=re.compile(r'(97[89](?:[- ]?\d){10}|\d(?:[- ]?\d){8}[- ]?[\dXx])\s*(\([^)]*\))?')
EQ=re.compile(r'e-?book|epub|pdf|electr|digital|en l[ií]nea|kindle|audio',re.I)
with (ROOT/'config/selfpub_services_es.csv').open() as f:SERV=[dict(x,regex=re.compile(x['name_pattern'])) for x in csv.DictReader(f)]
def parse_isbns(s):
 out={};bad=0
 for m in ISBN_RE.finditer(s or ''):
  q=m.group(2) or ''
  c=clean_isbns([m.group(1)],[])
  if not c:bad+=1;continue
  out[c[0]]=out.get(c[0],'')+q
 return out,bad
def parse_people(s):
 auth=[];con=[]
 for seg in (s or '').split('//'):
  seg=seg.strip()
  if not seg:continue
  name=re.split(r'\s,\s|\s-[a-záéíóúñ]',seg+' ')[0].strip(' ,')
  roles=re.findall(r'\s-([a-záéíóúñ]+)',seg)
  role=roles[0] if roles else ''
  tgt=auth if role in ('','aut','autor','escritor','coautor') else con
  if name and name not in tgt:tgt.append(name)
 return auth,con
def split_name(n):
 if ',' in n:
  s,g=n.split(',',1);return norm(g).split(),norm(s).split()
 t=norm(n).split();return t[:-1],t[-1:]
def strip_part(t):return [x for x in t if x not in PART]
def ap_match(author,pub_clean):
 """author as 'Surname, Given'; returns reason or ''."""
 g,s=split_name(author);nat=' '.join(g+s)
 for a,p in ((nat,pub_clean),(' '.join(strip_part(g+s)),' '.join(strip_part(pub_clean.split())))):
  m=match_name(a,p)
  if m:return m
 gs,ss=strip_part(g),strip_part(s)
 p=strip_part(norm(pub_clean,True).split())
 if len(ss)>=2 and gs and all(len(x)>1 for x in gs) and len(ss[0])>=3:
  if p==gs+[ss[0]] or p==[ss[0]]+gs:return 'es_given_first_surname'
 # initials + surname(s): leading single letters must be a prefix of the given-name initials
 k=0
 while k<len(p) and len(p[k])==1:k+=1
 if k and gs and k<=len(gs) and p[:k]==[x[0] for x in gs[:k]] and len(ss)>=1:
  rest=p[k:]
  if rest and len(rest[0])>=3 and (rest==ss or rest==ss[:1]) and len(ss[0])>=3:return 'compatible_initials'
 return ''
def pub_first(e):
 e=(e or '').strip();first=re.split(r'\s{2,}',e)[0] if e else ''
 first=re.sub(r'[\[\]]','',first).strip(' ,;.:/');return first
def flags(r):
 pub=pub_first(r['Editorial']);pl=low(pub);pc=norm(CORP.sub(' ',norm(pl,True)),True) if pl else ''
 auth,con=parse_people(r['Autor Personas']);corp=[low(c).strip(' /') for c in re.split(r'//',r['Autor Entidades']) if c.strip()]
 out=dict(authors_personal=json.dumps(auth,ensure_ascii=False),contributors=json.dumps(con,ensure_ascii=False),publisher=pub)
 out['unidentified_publisher']=(not pc) or pc in ('s n','sn','sin editorial')
 corp_self=any(norm(c,True)==pc and len(pc)>3 for c in corp);expl=bool(EXPL.search(pl))
 ap=False;why=[]
 if expl and (auth or not corp):ap=True;why.append('explicit_author_statement')
 elif expl and corp:corp_self=True
 if pc:
  for a in auth:
   m=ap_match(a,pc)
   if m:ap=True;why.append(m)
 out['contributor_match']=bool(pc) and any(ap_match(a,pc) for a in con)
 svc=mixed=False;tiers=set();names=[]
 for s in SERV:
  if s['regex'].search(pl):
   names.append(s['name_pattern'])
   if s['scope']=='mixed':mixed=True
   else:svc=True;tiers.add(s['tier']);
   if s['scope']!='mixed' and s['evidence_status']=='user_listed_unverified':out['svc_unverified']=True
 out.update(author_is_publisher=ap,service_imprint=svc,service_mixed=mixed,service_platform='platform' in tiers,service_author_services='author_services' in tiers,service_vanity='vanity' in tiers,
  corporate_self=corp_self,self_published_combined=ap or svc,classification_reason=';'.join(sorted(set(why))),matched_services=';'.join(names),explicit=expl)
 out.setdefault('svc_unverified',False)
 out['government']=bool(GOV.search(pl)) or bool(GOV.search(' '.join(corp)))
 out['reprint']=bool(REPRINT.search(low(r['Edición'])+' '+low(r['Descripción y notas'])[:300]))
 out['amazon_imprint']=bool(re.search(r'create\s?space|independently published|^independently$',pl))
 return out
def main():
 df=pd.read_parquet(ROOT/'data/interim/es_raw.parquet');N0=len(df);log={}
 df['bib_year']=df['Año de Bibliografía'].str.extract(r'(\d{4})')[0].astype(int)
 df['pub_year']=df['Fecha de publicación'].str.extract(r'(?<!\d)(1[5-9]\d\d|20\d\d)(?!\d)')[0].astype(float)
 log['records_total']=N0
 keep=(df['Tipo de documento']=='Libro')&(df['País de publicación']=='sp')&~df['Descripción física'].map(lambda x:bool(NONPRINT.match(low(x))))
 log['records_not_libro']=int((df['Tipo de documento']!='Libro').sum());log['records_not_spain']=int((df['País de publicación']!='sp').sum())
 log['records_nonprint_physdesc']=int(df['Descripción física'].map(lambda x:bool(NONPRINT.match(low(x)))).sum())
 d=df[keep].copy();log['records_print_spain']=len(d);log['records_missing_pub_year']=int(d.pub_year.isna().sum())
 # ISBN explosion
 rows=[];bad=0;noisbn=[]
 for i,r in zip(d.index,d.to_dict('records')):
  isb,b=parse_isbns(r['ISBN']);bad+=b
  isb={k:v for k,v in isb.items() if not EQ.search(v)}
  if not isb:noisbn.append(i);continue
  for k,v in isb.items():rows.append((i,k))
 log['invalid_isbn_tokens_dropped']=bad;log['print_records_without_valid_isbn']=len(noisbn)
 x=pd.DataFrame(rows,columns=['idx','isbn13']);log['isbn_rows_before_dedup']=len(x)
 d['score']=(d.Editorial!='').astype(int)*2+(d['Autor Personas']!='').astype(int)*2+(d['Título']!='').astype(int)+d.pub_year.notna().astype(int)+(d['Descripción física']!='').astype(int)+(d['Edición']!='').astype(int)
 x=x.join(d[['idBNE','score','bib_year']],on='idx').sort_values(['isbn13','score','bib_year','idBNE'],ascending=[True,False,True,True])
 x=x.drop_duplicates('isbn13');log['isbn_rows_after_dedup']=len(x)
 res=[]
 for idx,isbn in zip(x.idx,x.isbn13):
  r=d.loc[idx].to_dict();o=flags(r)
  o.update(isbn13=isbn,idBNE=r['idBNE'],bib_year=r['bib_year'],pub_year=r['pub_year'],title=r['Título'],publisher_full=r['Editorial'],edition=r['Edición'],physical=r['Descripción física'],lang=r['Lengua de publicación'],notes=(r['Descripción y notas'] or '')[:300],place=r['Lugar de publicación'])
  res.append(o)
 R=pd.DataFrame(res);R['pub_year']=R.pub_year.astype('Int64')
 R['isbn_group']=R.isbn13.map(lambda s:'978-84' if s.startswith('97884') else '979-13' if s.startswith('97913') else '979-8' if s.startswith('9798') else '979-10' if s.startswith('97910') else '978-other' if s.startswith('978') else '979-other')
 R.to_parquet(ROOT/'data/interim/es_classified.parquet',compression='zstd')
 # print records without a valid ISBN: classify too (selection check)
 nn=[];
 for idx in noisbn:
  r=d.loc[idx].to_dict();o=flags(r);nn.append(dict(pub_year=r['pub_year'],author_is_publisher=o['author_is_publisher'],service_imprint=o['service_imprint'],self_published_combined=o['self_published_combined']))
 pd.DataFrame(nn).to_parquet(ROOT/'data/interim/es_noisbn.parquet')
 json.dump(log,open(OUT/'build_log.json','w'),indent=1);print(json.dumps(log,indent=1));print(R.shape,R[['author_is_publisher','service_imprint','service_mixed','corporate_self','self_published_combined']].sum().to_dict())
if __name__=='__main__':main()
