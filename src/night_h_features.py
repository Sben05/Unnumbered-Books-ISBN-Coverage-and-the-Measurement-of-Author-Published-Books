"""Hypothesis H-A/H-B feature builder. Writes output/night_h/feat_<c>.parquet (one row per classified record with ISBN)."""
import pandas as pd, numpy as np, re, json, isbnlib, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
OUT='output/night_h'; os.makedirs(OUT,exist_ok=True)

def to13(s):
    d=re.sub(r'[^0-9Xx]','',s)
    if len(d)==13: return d
    if len(d)==10:
        b='978'+d[:9]; c=(10-sum(int(x)*(1 if i%2==0 else 3) for i,x in enumerate(b))%10)%10
        return b+str(c)
    return None
def first13(x):
    for t in re.findall(r'[0-9][0-9\- ]{8,16}[0-9Xx]',str(x)):
        r=to13(t)
        if r: return r
    return None
def pages(s):
    s=str(s or '')
    m=re.search(r'\((?:[^()]*?)\)',s) if s.startswith('1 vol') else None
    if m: s=m.group(0)
    m=re.search(r'(\bp\b|\bpp\b|\bpages?\b|páginas|\bP\.)',s,flags=re.I)
    if not m: return np.nan
    nums=[int(x) for x in re.findall(r'\d+',s[:m.start()]) if len(x)<5]
    nums=[n for n in nums if n>0]
    return float(sum(nums)) if nums else np.nan
def qcpages(s):
    m=re.search(r'(\d+)\s*(?:p\.|pages)',str(s)); return float(m.group(1)) if m else np.nan
def mask_parts(i):
    try:
        m=isbnlib.mask(i)
    except Exception: return None
    return m
def add_prefix(df):
    cache={}
    pre=[];rl=[];pl=[]
    for i in df.isbn13.values:
        m=cache.get(i[:11]) if False else mask_parts(i)
        if not m: pre.append(None);rl.append(np.nan);pl.append(np.nan);continue
        p=m.split('-')
        pre.append('-'.join(p[:3])); rl.append(len(p[2])); pl.append(len(p[3]))
    df['prefix']=pre; df['reglen']=rl; df['publen']=pl; return df
def poetry(u,t): return bool(re.search(r'(^|\s)82\S*-1(\D|$)',u)) or bool(re.search(r'poes|poesi|poem|poet',t,re.I))
def feats_udc(u):
    u=str(u or ''); lit=bool(re.match(r'\s*82',u))
    return lit, bool(re.search(r'(^|\s)82\S*-1(\D|$)',u)), bool(re.search(r'(^|\s)929|82\S*-94',u))
def first_ed(e):
    e=str(e or '').strip().lower()
    if e=='' : return True
    return bool(re.match(r'^\[?(1\.?\s?[ªaºo]?|1st|first|primera|première|prim|premi)',e)) or 'primera' in e or '1ª' in e
def build(name):
    if name=='es':
        c=pd.read_parquet('data/interim/es_classified_apc.parquet'); c['ap']=c.ap_consistent
        r=pd.read_parquet('data/interim/es_raw.parquet',columns=['ISBN','Descripción física','Edición','Lengua de publicación','CDU','Tema','Género/Forma','Tipo de documento'])
        r['isbn13']=r.ISBN.map(first13); r=r.dropna(subset=['isbn13']).drop_duplicates('isbn13')
        c=c.merge(r,on='isbn13',how='left'); matched=c['Descripción física'].notna()
        c['pages']=c['Descripción física'].map(pages); c['illus']=c['Descripción física'].fillna('').str.contains(r'\bil\.|ilustr',case=False)
        c['first_ed']=c['Edición'].map(first_ed); c['nonmaj_lang']=(c['Lengua de publicación'].fillna('')!='spa')&c['Lengua de publicación'].notna()
        t=c['CDU'].fillna('').map(feats_udc); c['lit']=[x[0] for x in t]; c['biog']=[x[2] for x in t]
        c['poetry']=[ (x[1] or bool(re.search(r'poes',str(a)+str(b),re.I))) for x,a,b in zip(t,c['Tema'],c['Género/Forma'])]
        c['has_genre']=c['CDU'].fillna('').str.len()>0; c['joined']=matched
    elif name=='pt':
        c=pd.read_parquet('data/interim/pt_classified.parquet'); c['ap']=c.ap_consistent
        r=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','illus','udc','notes']).drop_duplicates('id')
        c=c.merge(r,left_on='record_id',right_on='id',how='left',suffixes=('','_r'))
        c['pages']=c['extent'].map(pages); c['illus']=c['illus'].fillna('').str.len()>0
        c['first_ed']=c['edition'].map(first_ed); c['nonmaj_lang']=(c['lang'].fillna('')!='por')&c['lang'].notna()
        t=c['udc'].fillna('').map(feats_udc); c['lit']=[x[0] for x in t]; c['poetry']=[x[1] for x in t]; c['biog']=[x[2] for x in t]
        c['has_genre']=c['udc'].fillna('').str.len()>0; c['joined']=c['id'].notna()
    else:
        c=pd.read_parquet(f'data/interim/{name}_classified.parquet'); c['ap']=c.author_is_publisher
        if name=='fr': c=c[~c.us_9798.fillna(False)&~c.isbn13.str.startswith('9798')]
        if name=='qc':
            c['pages']=c.physical_description.map(qcpages); c['illus']=c.physical_description.str.contains(r'\d\s*(?:p\.|pages)\s*:\s*(?:ill|illustr)',case=False)
            c['nonmaj_lang']=c.language.fillna('')!='français'
            dw=c.notes.fillna('').str.extract(r'Dewey group=(.*)$')[0].fillna('')
            c['lit']=dw.str.contains('Littérature',case=False); c['has_genre']=dw!=''; c['poetry']=False; c['biog']=False
        else:
            c['pages']=c.physical_description.map(pages); c['illus']=c.physical_description.fillna('').str.contains(r'\bill|illustr',case=False)
            c['nonmaj_lang']=~c.language.fillna('').str.startswith('fre' if name=='fr' else 'eng')
            c['lit']=False;c['poetry']=False;c['biog']=False;c['has_genre']=False
        c['first_ed']=c['edition'].map(first_ed); c['joined']=True
    c['country']=name
    c=c[c.pub_year.between(1995,2023)].copy()
    c=add_prefix(c)
    cols=['country','isbn13','pub_year','ap','pages','illus','first_ed','nonmaj_lang','lit','poetry','biog','has_genre','joined','prefix','reglen','publen']
    if name in('es','pt'): cols.append('publisher')
    if name in ('es','pt'): c['author1']=c.authors_personal.astype(str)
    else: c['author1']=c.authors_personal.astype(str)
    cols.append('author1')
    c[cols].to_parquet(f'{OUT}/feat_{name}.parquet'); print(name,len(c),c.ap.sum(),c[['pages','joined','has_genre','lit','poetry']].mean().round(3).to_dict(),flush=True)
if __name__=='__main__':
    import sys
    for n in (sys.argv[1:] or ['es','pt','nz','qc','fr']): build(n)
