"""BNP catalogue (UNIMARC / MARCXchange XML, 27 files) -> data/interim/pt_raw.parquet (one row per bibliographic record)."""
import sys,glob,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
from multiprocessing import Pool
import pandas as pd
from pt_xml import records
def sf(fields,code,first=True):
 v=[t.strip() for _,_,s in fields for c,t in s if c==code and t.strip()];return (v[0] if v else '') if first else v
def rec(r):
 g=lambda t:r.get(t,[])
 f200=g('200');f210=g('210');f215=g('215');f205=g('205')
 notes=' | '.join(t for tag in ('300','304','305','306','307','316','317','320','327','328','330','500') for _,_,s in g(tag) for c,t in s if c=='a' and t)[:400]
 def names(tag):return [dict(a=sf([x],'a'),b=sf([x],'b'),f=sf([x],'f'),rel=sf([x],'4')) for x in g(tag)]
 corp=lambda tag:[' '.join(filter(None,[sf([x],'a'),sf([x],'b')])) for x in g(tag)]
 lead=r['leader']
 return dict(id=(g('001') or [''])[0],lstatus=lead[5:6],ltype=lead[6:7],llevel=lead[7:8],
  isbn_raw=json.dumps([dict(a=sf([x],'a'),b=sf([x],'b'),d=sf([x],'d'),z=sf([x],'z')) for x in g('010')],ensure_ascii=False),
  has_issn=bool(g('011')),dl=' ; '.join(f"{sf([x],'a')} {sf([x],'b')}" for x in g('021')),
  f100=(sf(g('100'),'a')),lang=sf(g('101'),'a'),country=sf(g('102'),'a'),f105=sf(g('105'),'a'),f106=sf(g('106'),'a'),
  title=sf(f200,'a'),subtitle=sf(f200,'e'),resp=sf(f200,'f'),resp2=sf(f200,'g'),edition=sf(f205,'a'),
  place=sf(f210,'a'),publisher=sf(f210,'c'),pubdate=sf(f210,'d'),manuf_place=sf(f210,'e'),manufacturer=sf(f210,'g'),manuf_date=sf(f210,'h'),f210_n=len(f210),
  extent=sf(f215,'a'),illus=sf(f215,'c'),size=sf(f215,'d'),notes=notes,
  a700=json.dumps(names('700'),ensure_ascii=False),a701=json.dumps(names('701'),ensure_ascii=False),a702=json.dumps(names('702'),ensure_ascii=False),
  c710=json.dumps(corp('710'),ensure_ascii=False),c711=json.dumps(corp('711'),ensure_ascii=False),c712=json.dumps(corp('712'),ensure_ascii=False),
  has_url=bool(g('856')),agency=sf(g('801'),'b'),f900=(sf(g('900'),'a')+' '+sf(g('900'),'d')).strip(),has_966=bool(g('966')),udc=sf(g('675'),'a'))
def parse(path):
 rows=[rec(r) for r in records(path)];d=pd.DataFrame(rows);d['_file']=Path(path).name;return d
if __name__=='__main__':
 files=sorted(glob.glob(str(ROOT/'data/interim/_pt_extract/*.xml')))
 with Pool(6) as p:dfs=p.map(parse,files,chunksize=1)
 df=pd.concat(dfs,ignore_index=True);print(df.shape);df.to_parquet(ROOT/'data/interim/pt_raw.parquet',compression='zstd')
