"""Exploratory: map BNP ISBNs to APEL prefix-holder names (APEL list 'until 31 Dec 2025', no dates) and classify holder as organisation-like vs person-like."""
import pandas as pd, numpy as np, re, duckdb
L=pd.read_excel('data/raw/apel/20251231_Prefixos_ISBN.xlsx'); L.columns=['prefix','holder']; L['p']=L.prefix.str.replace('-','',regex=False)
print('prefix rows',len(L),'distinct holders',L.holder.nunique(), 'lens',L.p.str.len().value_counts().to_dict())
pm={}
for p,h in zip(L.p,L.holder): pm.setdefault(len(p),{})[p]=h
lens=sorted(pm,reverse=True)
c=duckdb.connect()
d=c.execute("select isbn13, pub_year y, ap_consistent ap, publisher_full pub, authors_personal a from 'data/interim/pt_classified.parquet' where pub_year between 2010 and 2019").df()
def holder(i):
    for k in lens:
        h=pm[k].get(i[:k])
        if h: return h
    return None
d['holder']=d.isbn13.map(holder); print('matched share',d.holder.notna().mean().round(3))
org=re.compile(r'(?i)\b(lda|s\.?a\.?|edi[cç][oõ]es|editora|editorial|livros|associa|c[aâ]mara|munic|instituto|universidade|funda[cç]|centro|grupo|produ[cç]|publica|gr[aá]fica|junta|escola|clube|sociedade|ordem|igreja|agência|comunidade|unipessoal|cooperativa|museu|biblioteca)')
d['holder_type']=np.where(d.holder.isna(),'unmatched',np.where(d.holder.fillna('').map(lambda h:bool(org.search(h))),'organisation-like','person-like/other'))
d['author_ed']=d.isbn13.str.startswith('97898920')|d.isbn13.str.startswith('97898933')
t=d[d.ap].groupby(['y','author_ed','holder_type']).size().unstack(fill_value=0); print(t.to_string())
t.to_csv('output/paper_pt/ap_by_prefix_holder_type.csv')
print(d[d.ap&~d.author_ed&d.holder.notna()][['holder','pub']].sample(12,random_state=3).to_string())
print(d[d.author_ed].holder.value_counts().head(3))
