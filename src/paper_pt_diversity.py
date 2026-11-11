"""Model C (catalogue representativeness, after Zhu, Shi & Banerjee 2025) and Model B (author-service route) for Portugal.
Genres PRE-SPECIFIED from UDC (before looking at results): 0 general; 1 philosophy/psychology; 2 religion; 3 social sciences; 5 natural sciences; 6 applied sciences;
7 arts/recreation; 81 language; 82 literature split into poetry (-1), fiction (-3), other literature; 9 history/geography/biography; missing UDC dropped.
Per year: Shannon entropy H of the genre distribution of (i) all deposited self-published books, (ii) those with ISBN, (iii) those without;
total-variation distance TVD between (ii) and (i) = how unrepresentative the ISBN-visible subset is. Same for other books as comparison.
Model B: service-imprint books / all deposited books and / ISBN-bearing books. HHI of publisher shares, ISBN-bearing vs all deposited.
Break statistic: mean 2015-19 minus mean 2010-14; placebo: same with fake breaks 2011-2014 (pre-period windows); bootstrap over books within years."""
import numpy as np, pandas as pd, re, unicodedata
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2005,2022)].copy(); R['y']=R.pub_year.astype(int)
raw=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','udc']); raw['id']=raw.id.astype(str); R=R.merge(raw,on='id',how='left')
def genre(u):
    u=(u or '').strip()
    if not u or not u[0].isdigit(): return None
    if u.startswith('82'):
        if re.search(r'-1(?![\d])',u): return 'lit_poetry'
        if re.search(r'-3(?![\d])',u): return 'lit_fiction'
        return 'lit_other'
    if u.startswith('81'): return 'language'
    return {'0':'general','1':'philosophy_psych','2':'religion','3':'social_sci','5':'natural_sci','6':'applied','7':'arts_recreation','9':'history_geo_bio','8':'lit_other','4':'general'}[u[0]]
R['g']=R.udc.map(genre); print('UDC coverage, self-published books 2010-19: %.3f'%R[R.ap&R.y.between(2010,2019)].g.notna().mean())
G=sorted(R.g.dropna().unique())
def dist(d): c=d.g.value_counts(); return (c/c.sum()).reindex(G).fillna(0)
def H(p): p=p[p>0]; return float(-(p*np.log(p)).sum())
rows=[]
for y in range(2008,2023):
    for grp,mask in [('self-published',R.ap),('other',~R.ap)]:
        d=R[mask&(R.y==y)&R.g.notna()]
        if len(d)<30: continue
        pa=dist(d); pi=dist(d[d.has_isbn]); pn=dist(d[~d.has_isbn]) if (~d.has_isbn).sum()>=10 else None
        rows.append(dict(y=y,group=grp,n_all=len(d),n_isbn=int(d.has_isbn.sum()),H_all=H(pa),H_isbn=H(pi),H_noisbn=H(pn) if pn is not None else np.nan,
                         TVD_isbn_vs_all=0.5*float((pi-pa).abs().sum()),
                         poetry_share_all=pa.get('lit_poetry',0),poetry_share_isbn=pi.get('lit_poetry',0)))
T=pd.DataFrame(rows); T.to_csv('output/paper_pt/diversity_by_year.csv',index=False)
pd.set_option('display.width',230); print(T[T.y.between(2010,2019)].round(3).to_string(index=False))
def brk(s,B=2015,w=5): return s.loc[B:B+w-1].mean()-s.loc[B-w:B-1].mean()
rng=np.random.default_rng(1)
def boot(grp,metric,nb=400):
    out=[]
    for _ in range(nb):
        vals={}
        for y in range(2010,2020):
            d=R[(R.ap if grp=='self-published' else ~R.ap)&(R.y==y)&R.g.notna()]; d=d.iloc[rng.integers(0,len(d),len(d))]
            pa=dist(d); pi=dist(d[d.has_isbn])
            vals[y]=0.5*float((pi-pa).abs().sum()) if metric=='TVD' else H(pi)-H(pa)
        out.append(brk(pd.Series(vals)))
    return np.percentile(out,[2.5,97.5])
res=[]
for grp in ['self-published','other']:
    s=T[T.group==grp].set_index('y')
    for metric,col in [('TVD (ISBN subset vs all deposited)','TVD_isbn_vs_all'),('H_isbn - H_all','HD')]:
        ser=s.TVD_isbn_vs_all if col=='TVD_isbn_vs_all' else (s.H_isbn-s.H_all)
        b=brk(ser); pl=[brk(ser,B) for B in (2011,2012,2013,2014)]  # note: windows for fake breaks partly overlap the real post period only for 2014
        ci=boot(grp,'TVD' if col=='TVD_isbn_vs_all' else 'H')
        res.append(dict(group=grp,metric=metric,pre_2010_14=ser.loc[2010:2014].mean(),post_2015_19=ser.loc[2015:2019].mean(),change=b,ci_low=ci[0],ci_high=ci[1],placebo_changes=' '.join(f'{v:+.3f}' for v in pl)))
D=pd.DataFrame(res); print(D.round(4).to_string(index=False)); D.to_csv('output/paper_pt/diversity_summary.csv',index=False)
# ---- Model B: service route with two denominators
sb=R[R.y.between(2005,2022)].groupby('y').apply(lambda d:pd.Series({'books':len(d),'isbn_books':int(d.has_isbn.sum()),'service':int(d.service.sum()),'service_isbn':int((d.service&d.has_isbn).sum()),'ap':int(d.ap.sum())}))
sb['service_share_all_deposited']=sb.service/sb.books; sb['service_share_isbn_books']=sb.service_isbn/sb.isbn_books; sb['author_route_total_share']=(sb.service+sb.ap)/sb.books
print(sb.loc[2008:2022].round(4).to_string()); sb.to_csv('output/paper_pt/service_route_by_year.csv')
lg=lambda p:np.log(p/(1-p))
def its(ser,B=2015,lo=2008):
    pre=ser.loc[lo:B-1]; b=np.polyfit(pre.index,pre.values,1); post=ser.loc[B:B+3]; return float((post-np.polyval(b,post.index)).mean())
for col in ['service_share_all_deposited','service_share_isbn_books']:
    s=lg(sb[col]); print(col,'| level shift vs 2008-14 trend (logit): %.3f | placebo breaks 2011-13: %s'%(its(s),[round(its(s,B),3) for B in (2011,2012,2013)]))
# ---- concentration (HHI of publisher shares), ISBN-bearing vs all deposited
def norm(x): x=unicodedata.normalize('NFKD',str(x)).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',x)).strip()
R['pk']=R.publisher.map(norm)
hh=[]
for y in range(2008,2023):
    d=R[(R.y==y)&(R.pk!='')]
    def hhi(x): sh=x.pk.value_counts(normalize=True); return float((sh**2).sum())
    hh.append(dict(y=y,HHI_all_deposited=hhi(d),HHI_isbn_books=hhi(d[d.has_isbn]),top10_share_isbn=float(d[d.has_isbn].pk.value_counts(normalize=True).head(10).sum()),top10_share_all=float(d.pk.value_counts(normalize=True).head(10).sum())))
HH=pd.DataFrame(hh).set_index('y'); print(HH.loc[2010:2019].round(4).to_string()); HH.to_csv('output/paper_pt/publisher_concentration.csv')
