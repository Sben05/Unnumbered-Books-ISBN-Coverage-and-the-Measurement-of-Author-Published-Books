"""Continuous DL-time series (bins of 2,000 DL numbers ~ 6-7 weeks), 2011-2019: AP no-ISBN share, non-AP no-ISBN share, AP deposits per bin."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
bn=pd.read_parquet('data/interim/bnp_csv_bibliografianacional.parquet',columns=['id','dl'])
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt]
d=R.merge(bn,on='id',how='left'); m=d.dl.str.extract(r'^\s*(\d{5,7})\s*/\s*(\d{2})\b')
d['dln']=pd.to_numeric(m[0],errors='coerce'); d['dly']=pd.to_numeric(m[1],errors='coerce')+2000; d=d.dropna(subset=['dln','dly'])
q=d.groupby('dly').dln.quantile([.01,.99]).unstack(); d=d.join(q,on='dly'); d=d[(d.dln>=d[0.01])&(d.dln<=d[0.99])]
d=d[d.dln.between(321484,466000)]; B=2000; d['bin']=(d.dln//B)*B
g=d.groupby('bin').agg(n=('id','size'),ap=('ap','sum'),ap_noisbn=('has_isbn',lambda x:((~x)&d.loc[x.index,'ap']).sum()),noisbn=('has_isbn',lambda x:(~x).sum()))
g['ap_noisbn_share']=g.ap_noisbn/g.ap; g['nonap_noisbn_share']=(g.noisbn-g.ap_noisbn)/(g.n-g.ap)
g['se']=np.sqrt(g.ap_noisbn_share*(1-g.ap_noisbn_share)/g.ap)
g.to_csv('output/paper_pt/dl_series_2000bins.csv')
fee=386362; ann=fee-int(16000*20/365)   # ~11 Dec 2014 notice, approx 20 days before year start
pre=g[g.index<ann-6000]; post=g[(g.index>=fee)&(g.index<fee+5*16000)]
print('AP no-ISBN share: pre-2014 bins %.3f (books %d) | first 5 DL-years after fee %.3f (books %d)'%(pre.ap_noisbn.sum()/pre.ap.sum(),pre.ap.sum(),post.ap_noisbn.sum()/post.ap.sum(),post.ap.sum()))
for lo,hi,lab in [(fee-8000,fee,'last half of DL-2014'),(fee,fee+8000,'first half DL-2015'),(fee+8000,fee+16000,'second half DL-2015'),(fee+16000,fee+32000,'DL-2016')]:
    s=g[(g.index>=lo)&(g.index<hi)]; print(lab,'%.3f'%(s.ap_noisbn.sum()/s.ap.sum()),'AP books',int(s.ap.sum()),'| nonAP %.3f'%((s.noisbn.sum()-s.ap_noisbn.sum())/(s.n.sum()-s.ap.sum())))
fig,ax=plt.subplots(figsize=(11,4))
x=g.index/1000; ax.errorbar(x,100*g.ap_noisbn_share,yerr=196*g.se,fmt='o',ms=3,c='#c0392b',alpha=.6,label='AP books without ISBN (bin of 2,000 DL numbers ≈ 6 wks)')
ax.plot(x,100*g.ap_noisbn_share.rolling(5,center=True).mean(),c='#c0392b',lw=2)
ax.plot(x,100*g.nonap_noisbn_share,c='#555',lw=1.5,label='all other books without ISBN')
for y in range(2012,2020):
    b=g.index[g.index>=0]; 
ax.axvline(fee/1000,c='k',ls='--',label='first DL number of 2015 (fee starts 1 Jan)'); ax.axvline(ann/1000,c='k',ls=':',lw=1,label='~11 Dec 2014 notice')
ax.set_xlabel('legal-deposit running number (thousands); ~16k per year'); ax.set_ylabel('%'); ax.legend(fontsize=8); ax.set_ylim(0,100)
plt.tight_layout(); plt.savefig('output/paper_pt/fig_dl_series.png',dpi=150)
