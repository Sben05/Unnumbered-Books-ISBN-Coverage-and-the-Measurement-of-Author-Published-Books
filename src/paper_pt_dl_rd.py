"""Legal-deposit (DL) running number as a printing-time clock. DL numbers 'NNNNNN/YY' form one national sequence (~16k/yr).
Bin books by DL number around each year boundary; compare the 2014->2015 boundary (fee start) with placebo boundaries.
Outcomes: share of author=publisher (AP) books without ISBN; AP share of all deposits; same for non-AP books."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
bn=pd.read_parquet('data/interim/bnp_csv_bibliografianacional.parquet',columns=['id','dl'])
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt]
d=R.merge(bn,on='id',how='left')
m=d.dl.str.extract(r'^\s*(\d{5,7})\s*/\s*(\d{2})\b'); d['dln']=pd.to_numeric(m[0],errors='coerce'); d['dly']=pd.to_numeric(m[1],errors='coerce')+2000
d=d.dropna(subset=['dln','dly'])
# clean: keep numbers inside the central range of their DL year (drops typos)
q=d.groupby('dly').dln.quantile([.01,.99]).unstack(); d=d.join(q,on='dly'); d=d[(d.dln>=d[0.01])&(d.dln<=d[0.99])]
bounds={y:d[d.dly==y].dln.min() for y in range(2009,2020)}   # first number of each DL year
print({y:int(v) for y,v in bounds.items()})
d['noisbn']=(~d.has_isbn).astype(int); d['apn']=d.ap.astype(int)
BW=500; rows=[]
for y,b0 in bounds.items():
    w=d[(d.dln>=b0-12*BW)&(d.dln<b0+12*BW)].copy(); w['k']=np.floor((w.dln-b0)/BW).astype(int)
    g=w.groupby('k').agg(n=('id','size'),ap=('apn','sum'),ap_noisbn=('noisbn',lambda x:(x*w.loc[x.index,'apn']).sum()),
                         nonap_noisbn=('noisbn',lambda x:(x*(1-w.loc[x.index,'apn'])).sum()))
    g['boundary']=y; rows.append(g.reset_index())
G=pd.concat(rows); G['ap_noisbn_share']=G.ap_noisbn/G.ap; G['nonap_noisbn_share']=G.nonap_noisbn/(G.n-G.ap); G['ap_share']=G.ap/G.n
G.to_csv('output/paper_pt/dl_bins_around_boundaries.csv',index=False)
# discontinuity: pooled 6 bins (~3,000 numbers, ~2 months) each side, ratio-of-sums
def jump(g,col_num,col_den,h=6):
    L=g[(g.k<0)&(g.k>=-h)]; Rr=g[(g.k>=0)&(g.k<h)]
    return Rr[col_num].sum()/Rr[col_den].sum()-L[col_num].sum()/L[col_den].sum(), L[col_den].sum(), Rr[col_den].sum()
out=[]
for y,g in G.groupby('boundary'):
    G2=g.assign(nonap=g.n-g.ap)
    j1,nl,nr=jump(G2,'ap_noisbn','ap'); j2,_,_=jump(G2,'nonap_noisbn','nonap'); j3,_,_=jump(G2,'ap','n')
    out.append(dict(boundary=f'{y-1}->{y}',ap_noisbn_jump=j1,ap_books_left=nl,ap_books_right=nr,nonap_noisbn_jump=j2,ap_share_jump=j3))
O=pd.DataFrame(out); O.to_csv('output/paper_pt/dl_boundary_jumps.csv',index=False); print(O.round(3).to_string(index=False))
fig,ax=plt.subplots(1,2,figsize=(13,4.2))
for y,g in G.groupby('boundary'):
    c,lw,z=('#c0392b',2.5,3) if y==2015 else ('#bbb',1,1)
    g=g.sort_values('k'); r=g.ap_noisbn.rolling(3,center=True).sum()/g.ap.rolling(3,center=True).sum()
    ax[0].plot(g.k*BW/1000,100*r,c=c,lw=lw,zorder=z,label='2014→2015 (fee)' if y==2015 else None)
    r2=g.ap.rolling(3,center=True).sum()/g.n.rolling(3,center=True).sum(); ax[1].plot(g.k*BW/1000,100*r2,c=c,lw=lw,zorder=z)
ax[0].set_title('AP books without ISBN, % (3-bin moving)'); ax[1].set_title('AP books as % of all deposits')
for a in ax: a.axvline(0,ls=':',c='k'); a.set_xlabel('thousand DL numbers from first number of new year (~16k = 1 year)')
ax[0].plot([],[],c='#bbb',label='other year boundaries 2009-2019'); ax[0].legend(fontsize=8)
plt.tight_layout(); plt.savefig('output/paper_pt/fig_dl_boundary.png',dpi=150)
