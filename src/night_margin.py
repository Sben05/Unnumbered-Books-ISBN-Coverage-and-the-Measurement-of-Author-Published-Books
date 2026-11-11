"""H2: extensive vs intensive margin of author=publisher (AP) around fee dates.
New author = first year in which that normalised author name appears as AP in the source (left-censored: ignore first 3 yrs)."""
import duckdb, pandas as pd, numpy as np, re, unicodedata, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
c=duckdb.connect()
cfg={'es':('es_classified_apc','ap_consistent','publisher'),'pt':('pt_classified','ap_consistent','publisher'),
     'fr':('fr_classified','author_is_publisher',None),'uk':('uk_classified','author_is_publisher',None),
     'nz':('nz_classified','author_is_publisher',None),'qc':('qc_classified','author_is_publisher',None)}
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z ]','',s).strip()
rows=[]
for k,(f,flag,_) in cfg.items():
    df=c.execute(f"select pub_year, authors_personal a from 'data/interim/{f}.parquet' where {flag} and pub_year between 1995 and 2023").df()
    def first(a):
        import json
        try: a=json.loads(a) if isinstance(a,str) else list(a)
        except Exception: a=[]
        return norm(a[0].replace(',,',',')) if len(a) else ''
    df['au']=df.a.map(first); df=df[df.au!='']
    first_yr=df.groupby('au').pub_year.min(); df['new']=df.pub_year==df.au.map(first_yr)
    g=df.groupby('pub_year').agg(books=('au','size'),authors=('au','nunique'))
    g['new_authors']=df[df.new].groupby('pub_year').au.nunique(); g=g.fillna(0)
    g['books_per_author']=g.books/g.authors; g['new_share']=g.new_authors/g.authors
    g['country']=k; rows.append(g.reset_index())
M=pd.concat(rows); M.to_csv('output/night/ap_margin_by_year.csv',index=False)
fig,ax=plt.subplots(1,2,figsize=(12,4))
for k,g in M.groupby('country'):
    g=g[(g.pub_year>=2008)&(g.pub_year<=2021)]
    ax[0].plot(g.pub_year,g.authors/g.authors.iloc[0],label=k); ax[1].plot(g.pub_year,g.books_per_author,label=k)
ax[0].set_title('distinct AP authors, indexed 2008=1'); ax[1].set_title('AP books per AP author'); ax[0].legend()
for a in ax:
    for y in (2012,2015,2019): a.axvline(y,ls=':',c='grey')
plt.tight_layout(); plt.savefig('output/night/ap_margin.png',dpi=150)
for k in ['es','pt','fr']:
    print(M[(M.country==k)&M.pub_year.between(2009,2021)][['pub_year','books','authors','new_authors','new_share','books_per_author']].round(3).to_string(index=False))
