"""Serial-number discontinuity: 978-989-20-NNNN serials are allocated sequentially. Frontier at 1 Jan 2015 ~ p90 serial of books printed in DL-year 2014 (5,273).
Outcome: is the serial ever observed on a catalogued book (BNP print monograph, any year)? Use rate by serial block; compare below vs above the frontier; placebo cutoffs.
Caveat: use ~ publication of an ISBN-bearing, catalogued book; unobserved = never published, published without being catalogued, or unpublished still."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, duckdb
c=duckdb.connect()
s=c.execute("select distinct cast(substr(isbn13,9,4) as int) ser from 'data/interim/pt_classified.parquet' where isbn13 like '97898920%'").df().ser
used=np.zeros(10000,dtype=int); used[s.values]=1
def rate(lo,hi): return used[lo:hi].mean()
B=100; centers=np.arange(50,9950,B); r=np.array([rate(k-50,k+50) for k in centers])
F=5273
def rd(cut,h=600):
    l=used[max(1,cut-h):cut]; rr=used[cut:cut+h]; d=rr.mean()-l.mean(); se=np.sqrt(l.var()/len(l)+rr.var()/len(rr)); return d,se,l.mean(),rr.mean()
d,se,lm,rm=rd(F); print('Frontier ~%d: use rate below %.3f above %.3f diff %.3f (SE %.3f)'%(F,lm,rm,d,se))
pl=[(k,)+rd(k)[:2] for k in range(1500,8500,250) if abs(k-F)>600]
P=pd.DataFrame(pl,columns=['cut','diff','se']); print('placebo cutoffs: median |diff| %.3f, 90th %.3f, max %.3f; n=%d'%(P['diff'].abs().median(),P['diff'].abs().quantile(.9),P['diff'].abs().max(),len(P)))
print('use rate by 500-serial block:'); print(pd.Series([rate(k,k+500) for k in range(500,9500,500)],index=range(500,9500,500)).round(3).to_string())
for h in (300,600,1000): dd,sse,_,_=rd(F,h); print('bandwidth',h,'diff %.3f se %.3f'%(dd,sse))
for Fx in (4700,5000,5600,5900): dd,sse,_,_=rd(Fx); print('alt frontier',Fx,'diff %.3f se %.3f'%(dd,sse))
fig,ax=plt.subplots(figsize=(9,3.8)); ax.plot(centers,r,'o-',ms=3); ax.axvline(F,c='k',ls='--',label='~1 Jan 2015 frontier (est.)'); ax.set_xlabel('author-edition serial (978-989-20-NNNN), allocation order'); ax.set_ylabel('share of serials seen on a catalogued book'); ax.legend(); plt.tight_layout(); plt.savefig('output/paper_pt/fig_serial_use_rate.png',dpi=150)
