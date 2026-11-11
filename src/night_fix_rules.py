"""Validation-driven rule fixes (a)-(d) applied post hoc to existing classified parquet files. Does not modify existing files.
(a) organisation / dead-author guard on author=publisher name matches  (b) corporate-author match -> corporate_self
(c) extra service imprints from config/selfpub_services_addons.csv      (d) identical single-token author==publisher
Writes output/night_fixed/rowflags_<src>.parquet and fixed_by_year_<src>.csv."""
import sys,re,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from classify_selfpub import norm,raw_norm,match_name
import build_es,build_pt
from ap_consistent import ap_consistent,PART_ES,PART_PT
OUT=ROOT/'output/night_fixed'
ORG=re.compile(r'\b(?:instituto|institute|institut|fundacion|fundacao|fundacio|fondation|foundation|ministries|ministry|ministerio|ministere|ltd|limited|inc|incorporated|gallery|galerie|galeria|society|sociedad|societe|associates|estate|museum|museo|musee|council|university|universidad|universite|church|iglesia|eglise|lda|ltda|unipessoal|s l|s l u|s a|s a u)\b|\b(?:sl|slu)$')
CORPMARK=re.compile(r'&|\b(?:co|company|ltd|limited|inc|corp|associates|society|group|council|trust|museum|gallery)\b')
GENERIC={'editions','edition','books','book','press','group','media','studio','studios','productions','publishing','publications','company','anonymous','anonyme','anonimo','unknown','various','collectif','collective','inconnu','author','auteur','autor','editor','editorial','ediciones','edicoes','editora','independent','self','team','staff'}
with (ROOT/'config/selfpub_services_addons.csv').open() as f:ADD=[dict(x,regex=re.compile(x['name_pattern'])) for x in csv.DictReader(f)]
def death(a):
 m=re.search(r'(1[5-9]\d\d|20\d\d)\s*-\s*(1[5-9]\d\d|20\d\d)',a or '')
 if m and int(m.group(2))>=int(m.group(1)):return int(m.group(2))
 m=re.search(r'\bd\.?\s*(1[5-9]\d\d|20\d\d)\b',a or '')
 return int(m.group(1)) if m else None
def single(a,pstripped,porg):
 t=norm(a).split()
 return len(t)==1 and len(t[0])>=3 and t[0] not in GENERIC and pstripped==t[0] and not porg
def addon_svc(src,year,text):
 for s in ADD:
  if src not in s['sources'].split(';'):continue
  if year and not(int(s['start_year'])<=year<=int(s['end_year'])):continue
  if s['regex'].search(text):return True
 return False
VARS=['orig','org','dead','corp','single','all']
def decide(pairs,expl,single_hits):
 """pairs: list of (matched,org,dead,corp). returns dict variant->bool and corp_self flag."""
 o={}
 o['orig']=expl or any(m for m,_,_,_ in pairs)
 o['org']=expl or any(m and not g for m,g,_,_ in pairs)
 o['dead']=expl or any(m and not d for m,_,d,_ in pairs)
 o['corp']=expl or any(m and not c for m,_,_,c in pairs)
 o['all']=expl or any(m and not g and not d and not c for m,g,d,c in pairs)
 o['single']=o['orig'] or single_hits
 o['all']=o['all'] or single_hits
 o['corp_new']=any(m and c for m,_,_,c in pairs) and not o['all']
 return o
def run_list(src):
 R=pd.read_parquet(ROOT/f'data/interim/{src}_classified.parquet',columns=['record_id','isbn13','pub_year','authors_personal','authors_corporate','publishers','author_is_publisher','service_imprint','self_pub','corporate_self','classification_reason'])
 rows=[]
 for rid,isbn,yr,au,co,pu,ap0,sv0,cs0,why in zip(R.record_id,R.isbn13,R.pub_year,R.authors_personal,R.authors_corporate,R.publishers,R.author_is_publisher,R.service_imprint,R.corporate_self,R.classification_reason):
  au=list(au);pu=list(pu);co=list(co)
  expl='explicit_author_statement' in (why or '')
  cn=[norm(c,True) for c in co];pairs=[];sh=False
  pr=[(p,raw_norm(p),norm(p,True)) for p in pu]
  for a in au:
   dd=death(a);dead=dd is not None and yr is not None and dd<yr;cm=bool(CORPMARK.search(raw_norm(a)))
   for p,pr_,ps in pr:
    org=bool(ORG.search(pr_));m=bool(match_name(a,p))
    corp=cm or any(len(c)>3 and (c==ps or c in ps or ps in c) and len(ps)>3 for c in cn)
    if m:pairs.append((True,org,dead,corp))
    elif single(a,ps,org) and not dead and not cm:sh=True
  o=decide(pairs,expl,sh)
  svc_add=addon_svc(src,yr,'; '.join(x[1] for x in pr))
  rows.append((rid,isbn,yr,bool(ap0),bool(sv0),bool(cs0),svc_add,o['orig'],o['org'],o['dead'],o['corp'],o['single'],o['all'],o['corp_new']))
 return rows
def run_json(src):
 mod=build_es if src=='es' else build_pt
 part=PART_ES if src=='es' else PART_PT
 cols=['isbn13','pub_year','authors_personal','publisher','unidentified_publisher','author_is_publisher','service_imprint','corporate_self','classification_reason']
 R=pd.read_parquet(ROOT/f'data/interim/{src}_classified.parquet',columns=cols+(['ap_consistent','record_id'] if src=='pt' else []))
 rows=[]
 for i,(isbn,yr,au,pub,un,ap0,sv0,cs0,why) in enumerate(zip(*[R[c] for c in cols])):
  rid=R.record_id.iat[i] if src=='pt' else isbn
  apc0=bool(R.ap_consistent.iat[i]) if src=='pt' else bool(ap0)
  auth=json.loads(au) if au else [];pl=mod.low(pub);pc=norm(mod.CORP.sub(' ',norm(pl,True)),True) if pl else ''
  expl='explicit_author_statement' in (why or '');pairs=[];sh=False;prn=raw_norm(pub or '');org=bool(ORG.search(prn))
  for a in auth:
   dd=death(a);dead=dd is not None and yr is not None and dd<yr;cm=bool(CORPMARK.search(raw_norm(a)))
   m=bool(pc) and bool(mod.ap_match(a,pc))
   if src=='pt' and not m:m=bool(pc) and not un and ap_consistent(a,pc.split(),part)
   if m:pairs.append((True,org,dead,cm))
   elif pc and single(a,pc,org) and not dead and not cm:sh=True
  o=decide(pairs,expl,sh)
  rows.append((rid,isbn,yr,apc0,bool(sv0),bool(cs0),False,o['orig'],o['org'],o['dead'],o['corp'],o['single'],o['all'],o['corp_new']))
 return rows
COLS=['record_id','isbn13','pub_year','ap_stored','svc_orig','corp_self_orig','svc_add','ap_orig','ap_org','ap_dead','ap_corp','ap_single','ap_all','corp_new']
def main(srcs):
 for s in srcs:
  rows=run_list(s) if s in('uk','nz','fr','qc') else run_json(s)
  D=pd.DataFrame(rows,columns=COLS);D['record_id']=D.record_id.astype(str);D['isbn13']=D.isbn13.astype(str)
  D['recon_ok']=D.ap_orig==D.ap_stored
  print(s,len(D),'AP reproduction mismatches:',int((~D.recon_ok).sum()),flush=True)
  D.to_parquet(OUT/f'rowflags_{s}.parquet',compression='zstd')
  D['svc_all']=D.svc_orig|D.svc_add
  g=D.groupby('pub_year');Y=pd.DataFrame({'print_isbns':g.size(),'ap_orig':g.ap_orig.sum(),'ap_org_only':g.ap_org.sum(),'ap_dead_only':g.ap_dead.sum(),'ap_corp_only':g.ap_corp.sum(),'ap_single_only':g.ap_single.sum(),'ap_fixed':g.ap_all.sum(),
   'svc_orig':g.svc_orig.sum(),'svc_fixed':g.svc_all.sum(),'corp_self_orig':g.corp_self_orig.sum(),'corp_self_added':g.corp_new.sum()})
  Y['combined_orig']=(D.ap_orig|D.svc_orig).groupby(D.pub_year).sum();Y['combined_fixed']=(D.ap_all|D.svc_all).groupby(D.pub_year).sum()
  Y.reset_index().to_csv(OUT/f'fixed_by_year_{s}.csv',index=False)
if __name__=='__main__':main(sys.argv[1:] or ['uk','nz','fr','qc','es','pt'])
