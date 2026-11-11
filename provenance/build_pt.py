"""Portugal (BNP UNIMARC catalogue): print monographs, one row per valid ISBN-13, classify self-publication.
Reuses norm/match_name from classify_selfpub.py; Portuguese phrases, particles and government patterns."""
import sys,re,csv,json,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from build_2025 import clean_isbns
from classify_selfpub import norm,match_name
from ap_consistent import ap_consistent,PART_PT
OUT=ROOT/'output/portugal';OUT.mkdir(parents=True,exist_ok=True)
def low(s):
 s=unicodedata.normalize('NFKD',s or '');return ''.join(c for c in s if not unicodedata.combining(c)).lower()
PART={'de','da','do','das','dos','e','del','la','van','von','di'}
CORP=re.compile(r'\b(?:lda|ltda|s a|sa|unipessoal|editora|editores|editor|edicoes|edicao|ed|edic|publicacoes|producoes|grupo|livraria|editorial)\b')
EXPL=re.compile(r"\b(?:o|a|os|as) (?:autor|autora|autores|autoras)\b|^autor$|^autora$|\bedicao (?:do|de|da|d) ?(?:o )?autor\w*|\bed\.? (?:do|de|da) autor\w*|\bed\.? autor\b|\bedicao autor\b|\bauto.?edic\w*|\bauto.?edit\w*|\bauto.?public\w*|\bpor conta (?:do|de) autor\b|\bpublicado pelo autor\b|\bo proprio autor\b|\bautor.editor\b")
GOV=re.compile(r'\b(?:camara municipal|junta de freguesia|municipio|ministerio|governo|assembleia da republica|assembleia municipal|assembleia legislativa|direccao.geral|direcao.geral|comissao de coordenacao|secretaria.geral|secretaria de estado|presidencia do conselho|instituto nacional|regiao autonoma|comunidade intermunicipal|inspeccao.geral|inspecao.geral|imprensa nacional|autoridade|gabinete do)\b')
REPRINT=re.compile(r'reimp|reedi|nova ed|rev\b|revista|revisto|aument|actualiz|atualiz|\b(?:segunda|terceira|quarta|quinta|sexta|setima|oitava|nona|decima)\b|\b(?:[2-9]|1\d)\s*[.]?\s*[aªº°]?\s*(?:ed|edic)\w*')
ISBN_RE=re.compile(r'(97[89](?:[- ]?\d){10}|\d(?:[- ]?\d){8}[- ]?[\dXx])')
EQ=re.compile(r'e-?book|epub|pdf|electr|digital|online|em linha|kindle|mobi|audio|cd-?rom|dvd',re.I)
NONPRINT_EXT=re.compile(r'^\s*(?:\d+\s+)?(?:cd|dvd|disco|cassete|cassette|video|ficheiro|recurso|mapa|cartaz|partitura|diapositivo|microficha|mapas)',re.I)
with (ROOT/'config/selfpub_services_pt.csv').open() as f:SERV=[dict(x,regex=re.compile(x['name_pattern'])) for x in csv.DictReader(f)]
def parse_isbns(raw):
 out={};bad=0
 for e in json.loads(raw):
  if EQ.search(e['b']) or EQ.search(e['d']):continue
  for m in ISBN_RE.finditer(e['a']):
   c=clean_isbns([m.group(1)],[])
   if not c:bad+=1;continue
   out[c[0]]=e['b']
 return out,bad
def nm(e):
 return (e['a']+', '+e['b']).strip(', ') if e['b'] else e['a']
def split_name(n):
 if ',' in n:
  s,g=n.split(',',1);return norm(g).split(),norm(s).split()
 t=norm(n).split();return t[:-1],t[-1:]
def strip_part(t):return [x for x in t if x not in PART]
def ap_match(author,pub_clean):
 g,s=split_name(author);nat=' '.join(g+s)
 for a,p in ((nat,pub_clean),(' '.join(strip_part(g+s)),' '.join(strip_part(pub_clean.split())))):
  m=match_name(a,p)
  if m:return m
 gs,ss=strip_part(g),strip_part(s);p=strip_part(norm(pub_clean,True).split())
 if gs and ss and len(p)>=2 and all(len(x)>1 for x in p) and all(len(x)>1 for x in gs) and len(ss[-1])>=3:
  if p in ([gs[0]]+[ss[-1]],gs+[ss[-1]],[gs[0]]+ss,gs+ss[:1],[ss[-1]]+[gs[0]]):return 'pt_name_variant'
 k=0
 while k<len(p) and len(p[k])==1:k+=1
 if k and gs and k<=len(gs) and p[:k]==[x[0] for x in gs[:k]] and ss:
  rest=p[k:]
  if rest and len(rest[0])>=3 and (rest==ss or rest==ss[-1:] or rest==ss[:1]):return 'compatible_initials'
 return ''
def clean_pub(p):return re.sub(r'[\[\]]','',p or '').strip(' ,;.:/')
def flags(r):
 pub=clean_pub(r['publisher']);pl=low(pub);pc=norm(CORP.sub(' ',norm(pl,True)),True) if pl else ''
 a700=json.loads(r['a700']);a701=json.loads(r['a701']);a702=json.loads(r['a702'])
 auth=[];con=[]
 for e in a700+a701:
  n=nm(e)
  if n and n not in auth:auth.append(n)
 for e in a702:
  n=nm(e)
  if not n:continue
  tgt=auth if e['rel'] in ('070',) else con
  if n not in tgt:tgt.append(n)
 corp=[low(c).strip(' /') for c in json.loads(r['c710'])+json.loads(r['c711']) if c.strip()]
 out=dict(authors_personal=json.dumps(auth,ensure_ascii=False),contributors=json.dumps(con,ensure_ascii=False),publisher=pub)
 out['unidentified_publisher']=(not pc) or bool(re.fullmatch(r's\W*n\W*(?:e\W*c\W*)?|sem editor|f\W*s\W*n\W*e\W*c\W*|s\W*n\W*r\W*i\W*p\W*d\W*',pl.strip()))
 corp_self=any(norm(c,True)==pc and len(pc)>3 for c in corp);expl=bool(EXPL.search(pl))
 ap=False;why=[]
 if expl and (auth or not corp):ap=True;why.append('explicit_author_statement')
 elif expl and corp:corp_self=True
 if pc and not out['unidentified_publisher']:
  for a in auth:
   m=ap_match(a,pc)
   if m:ap=True;why.append(m)
 out['ap_pure']=bool(pc) and not out['unidentified_publisher'] and any(ap_consistent(a,pc.split(),PART_PT) for a in auth)
 out['ap_consistent']=ap or out['ap_pure']
 out['contributor_match']=bool(pc) and any(ap_match(a,pc) for a in con)
 svc=mixed=False;tiers=set();names=[];unv=False
 for s in SERV:
  if s['regex'].search(pl):
   names.append(s['name_pattern'])
   if s['scope']=='mixed':mixed=True
   else:
    if s['start_year'] and r['pub_year'] and int(r['pub_year'])<int(s['start_year']):continue
    svc=True;tiers.add(s['tier'])
 out.update(author_is_publisher=ap,service_imprint=svc,service_mixed=mixed,service_platform='platform' in tiers,service_author_services='author_services' in tiers,
  corporate_self=corp_self,self_published_combined=ap or svc,classification_reason=';'.join(sorted(set(why))),matched_services=';'.join(names),explicit=expl)
 out['government']=bool(GOV.search(pl)) or bool(GOV.search(' '.join(corp)))
 out['reprint']=bool(REPRINT.search(low(r['edition'])+' '+low(r['notes'])[:200]))
 out['amazon_imprint']=bool(re.search(r'create\s?space|independently published|amazon',pl))
 return out
def main():
 df=pd.read_parquet(ROOT/'data/interim/pt_raw.parquet');log={'records_total':len(df)}
 y=df.pubdate.str.extract(r'(?<!\d)(1[5-9]\d\d|20\d\d)(?!\d)')[0]
 y2=pd.to_numeric(df.f100.str[9:13],errors='coerce')
 df['pub_year']=pd.to_numeric(y,errors='coerce');df['year_src']=df.pub_year.notna().map({True:'210d',False:''})
 m=df.pub_year.isna()&y2.between(1500,2100);df.loc[m,'pub_year']=y2[m];df.loc[m,'year_src']='100/9-12'
 df['cat_year']=pd.to_numeric(df.f100.str[:4],errors='coerce')
 for k,msk in [('not_leader_a_m',~((df.ltype=='a')&(df.llevel=='m'))),('not_PT',df.country!='PT'),('form_not_print',~df.f106.isin(['r',''])),('nonprint_extent',df.extent.map(lambda x:bool(NONPRINT_EXT.match(x))))]:
  log['excluded_'+k]=int(msk.sum())
 keep=(df.ltype=='a')&(df.llevel=='m')&(df.country=='PT')&df.f106.isin(['r',''])&~df.extent.map(lambda x:bool(NONPRINT_EXT.match(x)))
 d=df[keep].copy();log['records_print_pt']=len(d);log['missing_pub_year']=int(d.pub_year.isna().sum())
 rows=[];bad=0;noisbn=[]
 for i,raw in zip(d.index,d.isbn_raw):
  isb,b=parse_isbns(raw);bad+=b
  if not isb:noisbn.append(i);continue
  for k in isb:rows.append((i,k))
 log['invalid_isbn_tokens']=bad;log['print_records_without_valid_isbn']=len(noisbn)
 x=pd.DataFrame(rows,columns=['idx','isbn13']);log['isbn_rows_before_dedup']=len(x)
 d['score']=(d.publisher!='').astype(int)*2+((d.a700!='[]')).astype(int)*2+(d.title!='').astype(int)+d.pub_year.notna().astype(int)+(d.extent!='').astype(int)+(d.edition!='').astype(int)
 x=x.join(d[['id','score','cat_year']],on='idx').sort_values(['isbn13','score','cat_year','id'],ascending=[True,False,True,True]).drop_duplicates('isbn13')
 log['isbn_rows_after_dedup']=len(x)
 cache={};res=[]
 recs=d.loc[x.idx.unique()].to_dict('index')
 for idx in x.idx.unique():
  r=recs[idx];r['pub_year']=None if pd.isna(r['pub_year']) else int(r['pub_year']);cache[idx]=flags(r)
 for idx,isbn in zip(x.idx,x.isbn13):
  r=recs[idx];o=dict(cache[idx]);o.update(isbn13=isbn,record_id=r['id'],pub_year=r['pub_year'],cat_year=r['cat_year'],year_src=r['year_src'],title=r['title'],publisher_full=r['publisher'],edition=r['edition'],extent=r['extent'],lang=r['lang'],notes=r['notes'][:300],place=r['place'],dl=r['dl'],agency=r['agency']);res.append(o)
 R=pd.DataFrame(res);R['pub_year']=R.pub_year.astype('Int64');R['cat_year']=R.cat_year.astype('Int64')
 g=R.isbn13
 R['isbn_group']=g.map(lambda s:'978-972/989 (PT)' if s.startswith(('978972','978989')) else '979-8' if s.startswith('9798') else '979-10 (FR)' if s.startswith('97910') else '978-1 (US/UK etc.)' if s.startswith('9781') else '978-85 (BR)' if s.startswith('97885') else '978-84 (ES)' if s.startswith('97884') else '978-other' if s.startswith('978') else '979-other')
 R.to_parquet(ROOT/'data/interim/pt_classified.parquet',compression='zstd')
 nn=[]
 for idx in noisbn:
  r=d.loc[idx].to_dict();r['pub_year']=None if pd.isna(r['pub_year']) else int(r['pub_year']);o=flags(r)
  nn.append(dict(pub_year=r['pub_year'],ap_consistent=o['ap_consistent'],ap_pure=o['ap_pure'],author_is_publisher=o['author_is_publisher'],service_imprint=o['service_imprint'],self_published_combined=o['self_published_combined']))
 pd.DataFrame(nn).to_parquet(ROOT/'data/interim/pt_noisbn.parquet')
 json.dump(log,open(OUT/'build_log.json','w'),indent=1);print(json.dumps(log,indent=1));print(R.shape,R[['author_is_publisher','service_imprint','service_mixed','corporate_self','self_published_combined']].sum().to_dict())
if __name__=='__main__':main()
