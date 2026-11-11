"""H-C: ISBN-less AP records around fee dates (ES 2012, PT 2015). FR/NZ/QC classified files contain only ISBN-bearing records, so no controls exist there."""
import pandas as pd, numpy as np, os
from statsmodels.stats.proportion import proportion_confint as wil
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); OUT='output/night_h'
rows=[]
cfg={'es':('es_classified_apc','es_noisbn','author_is_publisher',2012),'pt':('pt_classified','pt_noisbn','ap_consistent',2015)}
for k,(cf,nf,flag,ev) in cfg.items():
    a=pd.read_parquet(f'data/interim/{cf}.parquet',columns=['pub_year',flag]); n=pd.read_parquet(f'data/interim/{nf}.parquet',columns=['pub_year',flag])
    a=a[a.pub_year.between(2000,2020)].assign(pub_year=lambda d:d.pub_year.astype(int)); n=n.dropna(subset=['pub_year']); n=n[n.pub_year.between(2000,2020)].assign(pub_year=lambda d:d.pub_year.astype(int))
    g=pd.DataFrame({'isbn_all':a.groupby('pub_year').size(),'isbn_ap':a.groupby('pub_year')[flag].sum(),'noisbn_all':n.groupby('pub_year').size(),'noisbn_ap':n.groupby('pub_year')[flag].sum()}).fillna(0)
    g['noisbn_share_of_ap']=g.noisbn_ap/(g.noisbn_ap+g.isbn_ap); g['noisbn_share_of_nonap']=(g.noisbn_all-g.noisbn_ap)/((g.noisbn_all-g.noisbn_ap)+(g.isbn_all-g.isbn_ap))
    g['ap_share_isbn']=g.isbn_ap/g.isbn_all; g['ap_share_noisbn']=g.noisbn_ap/g.noisbn_all; g['country']=k; g['event']=ev
    rows.append(g.reset_index())
    pre=g.loc[ev-3:ev-1]; post=g.loc[ev:ev+2]
    def sh(d,col_n,col_d): 
        x=d[col_n].sum(); N=d[col_d].sum(); lo,hi=wil(x,N,method='wilson'); return x/N,lo,hi,int(x),int(N)
    for lab,(num,den) in {'noISBN share of AP records':(('noisbn_ap',None)),}.items(): pass
    out=[]
    for lab,fn in [('noISBN share of AP',lambda d:(d.noisbn_ap.sum(),(d.noisbn_ap+d.isbn_ap).sum())),('noISBN share of non-AP',lambda d:((d.noisbn_all-d.noisbn_ap).sum(),((d.noisbn_all-d.noisbn_ap)+(d.isbn_all-d.isbn_ap)).sum()))]:
        for w,d in (('pre',pre),('post',post)):
            x,N=fn(d); lo,hi=wil(x,N,method='wilson'); out.append((k,lab,w,x/N,lo,hi,int(x),int(N)))
    o=pd.DataFrame(out,columns=['country','measure','window','share','lo','hi','x','N']); print(o.round(4).to_string(index=False))
    # DiD on log odds: AP vs non-AP, pre->post, bootstrap by binomial resampling of the 4 cells
    rng=np.random.default_rng(0)
    cells={(m,w):(r.x,r.N) for m,w,r in [(r.measure,r.window,r) for r in o.itertuples()]}
    def lo_(x,N): x=min(max(x,.5),N-.5); return np.log(x/(N-x))
    est=(lo_(*cells[('noISBN share of AP','post')])-lo_(*cells[('noISBN share of AP','pre')]))-(lo_(*cells[('noISBN share of non-AP','post')])-lo_(*cells[('noISBN share of non-AP','pre')]))
    bs=[]
    for _ in range(2000):
        v={c:(rng.binomial(int(N),x/N),N) for c,(x,N) in cells.items()}
        bs.append((lo_(*v[('noISBN share of AP','post')])-lo_(*v[('noISBN share of AP','pre')]))-(lo_(*v[('noISBN share of non-AP','post')])-lo_(*v[('noISBN share of non-AP','pre')])))
    print(k,'DiD logit(noISBN share) AP vs non-AP:',round(est,3),np.percentile(bs,[2.5,97.5]).round(3))
    o['did']=est; o['did_lo'],o['did_hi']=np.percentile(bs,[2.5,97.5]); o.to_csv(f'{OUT}/hc_{k}_windows.csv',index=False)
G=pd.concat(rows); G.to_csv(f'{OUT}/hc_by_year.csv',index=False)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(11,4))
for a,(k,g) in zip(ax,G.groupby('country')):
    a.plot(g.pub_year,g.noisbn_share_of_ap,'o-',label='AP records'); a.plot(g.pub_year,g.noisbn_share_of_nonap,'s--',label='non-AP records'); a.axvline(g.event.iloc[0]-.5,c='grey',ls=':'); a.set_title(f'{k.upper()}: share of records with no ISBN'); a.legend()
plt.tight_layout(); plt.savefig(f'{OUT}/hc_noisbn.png',dpi=140)
