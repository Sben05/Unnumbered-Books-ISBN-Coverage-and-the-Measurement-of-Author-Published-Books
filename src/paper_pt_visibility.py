"""Visibility + validation: match BNP national-bibliography print books (2010-2019) to the Open Library editions dump (CC0, local, data/raw/open-library)
by normalised title + publication year (+/-1), identically for books with and without an ISBN. Outcomes: in OL at all; OL record carries an ISBN
(validation: ISBN exists though BNP record has none); OL record came from a commercial feed (amazon / bwb / promise / bookseller source_records)."""
import duckdb, glob, re, unicodedata, pandas as pd, numpy as np
c=duckdb.connect(); fs=sorted(glob.glob('data/raw/open-library/data/editions/*.parquet'))
def nt(s):
    s=unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9 ]',' ',s); s=re.sub(r'\s+',' ',s).strip(); return s[:60]
c.create_function('nt',nt,['VARCHAR'],'VARCHAR')
ol=c.execute(f"""select nt(title) t, try_cast(regexp_extract(publish_date,'(19|20)\\d\\d',0) as int) y,
   (coalesce(isbn_13,'')<>'' or coalesce(isbn_10,'')<>'') has_isbn,
   regexp_matches(coalesce(source_records,''),'(?i)amazon|bwb|promise|bookseller|harvard_bookstore|ingram') commercial,
   regexp_matches(coalesce(source_records,''),'(?i)marc') library_marc,
   coalesce(publish_country,'') pc, coalesce(languages,'') lang
   from read_parquet({fs!r})
   where try_cast(regexp_extract(publish_date,'(19|20)\\d\\d',0) as int) between 2008 and 2022
     and (lang like '%por%' or pc in ('po','pt','po ') )""").df()
print('OL candidate editions (Portuguese, 2008-22):',len(ol)); ol=ol[ol.t.str.len()>=8]
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2010,2019)].copy()
R['t']=R.title.map(nt); R=R[R.t.str.len()>=8]
# aggregate OL by title,year
agg=ol.groupby(['t','y']).agg(ol_n=('has_isbn','size'),ol_isbn=('has_isbn','max'),ol_comm=('commercial','max'),ol_marc=('library_marc','max')).reset_index()
hits=[]
for dy in (-1,0,1):
    a=agg.copy(); a['y']=a.y-dy; hits.append(a)
H=pd.concat(hits).groupby(['t','y']).agg(ol_isbn=('ol_isbn','max'),ol_comm=('ol_comm','max'),ol_marc=('ol_marc','max')).reset_index()
R['y']=R.pub_year.astype(int)
M=R.merge(H,on=['t','y'],how='left'); M['in_ol']=M.ol_isbn.notna()
for k in ['ol_isbn','ol_comm','ol_marc']: M[k]=M[k].fillna(False).astype(bool)
M['grp']=np.where(M.ap,'self-published (AP)','other')+' | '+np.where(M.has_isbn,'ISBN','no ISBN')
M['period']=np.where(M.pub_year<=2014,'2010-14','2015-19')
T=M.groupby(['grp','period']).agg(books=('id','size'),in_ol=('in_ol','mean'),ol_with_isbn=('ol_isbn','mean'),ol_commercial=('ol_comm','mean')).round(3)
print(T.to_string()); T.to_csv('output/paper_pt/visibility_openlibrary.csv')
# validation: of BNP no-ISBN books found in OL, share whose OL edition has an ISBN
v=M[(~M.has_isbn)&M.in_ol]; print('BNP no-ISBN books found in OL:',len(v),'| of which OL edition has ISBN: %.3f'%v.ol_isbn.mean())
print(v[['pub_year','ap','title','publisher']].head(12).to_string())
# regression-style comparison: in_ol ~ no-ISBN within AP and within other, controlling year (linear prob, descriptive)
import statsmodels.formula.api as smf
M['noisbn']=(~M.has_isbn).astype(int); M['apx']=M.ap.astype(int); M['in_olx']=M.in_ol.astype(int)
m=smf.ols('in_olx ~ noisbn*apx + C(pub_year)',data=M).fit(cov_type='HC1'); print(m.params[['noisbn','apx','noisbn:apx']].round(4).to_dict(), m.bse[['noisbn','apx','noisbn:apx']].round(4).to_dict())
M[['id','pub_year','ap','has_isbn','in_ol','ol_isbn','ol_comm','ol_marc']].to_parquet('data/interim/pt_visibility_ol.parquet')
