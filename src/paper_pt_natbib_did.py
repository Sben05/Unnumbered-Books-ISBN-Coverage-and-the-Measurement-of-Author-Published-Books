"""Within-catalogue comparison: share of books WITHOUT ISBN, author=publisher (AP) vs all other books, BNP national bibliography.
Gap_t = logit(noISBN share | AP) - logit(noISBN share | non-AP). Level shift at 2015 vs 2010-14 mean; placebo breaks; binomial-bootstrap CI."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
g=pd.read_csv('output/paper_pt/natbib_isbn_by_ap_year.csv').set_index('pub_year'); g.index=g.index.astype(int)
lg=lambda p:np.log(p/(1-p))
g['nonap']=g.books-g.ap
g['gap']=lg(g.ap_noisbn/g.ap)-lg(g.nonap_noisbn/g.nonap)
def shift(gap,B,pre=5,post=5):
    return gap.loc[B:B+post-1].mean()-gap.loc[B-pre:B-1].mean()
est=shift(g.gap,2015)
pl={B:shift(g.gap,B) for B in range(2010,2021) if B!=2015}
rng=np.random.default_rng(1); bs=[]
for _ in range(4000):
    a=rng.binomial(g.ap,g.ap_noisbn/g.ap)/g.ap; n=rng.binomial(g.nonap,g.nonap_noisbn/g.nonap)/g.nonap
    gg=pd.Series(lg(np.clip(a,1e-4,1-1e-4))-lg(np.clip(n,1e-4,1-1e-4)),index=g.index); bs.append(shift(gg,2015))
lo,hi=np.percentile(bs,[2.5,97.5])
res=pd.DataFrame([dict(stat='level shift in gap, 2015-19 vs 2010-14 (logit)',estimate=est,binomial_ci_low=lo,binomial_ci_high=hi,
   rank_abs_among_breaks_2010_2020=1+sum(abs(v)>=abs(est) for v in pl.values()),n_breaks=len(pl)+1)])
res.to_csv('output/paper_pt/natbib_did_summary.csv',index=False); print(res.round(3).to_string(index=False))
print('placebo shifts:',{k:round(v,3) for k,v in pl.items()})
for lab,(a,b) in {'pre 2010-14':(2010,2014),'post 2015-19':(2015,2019),'late 2021-25':(2021,2025)}.items():
    s=g.loc[a:b]; print(lab,'AP noISBN share %.3f | nonAP %.3f | AP total/yr %.0f | AP with ISBN/yr %.0f | AP no ISBN/yr %.0f'%(s.ap_noisbn.sum()/s.ap.sum(),s.nonap_noisbn.sum()/s.nonap.sum(),s.ap.mean(),s.ap_isbn.mean(),s.ap_noisbn.mean()))
fig,ax=plt.subplots(1,2,figsize=(12,4))
ax[0].plot(g.index,100*g.ap_noisbn/g.ap,'o-',c='#c0392b',label='author = publisher books')
ax[0].plot(g.index,100*g.nonap_noisbn/g.nonap,'o-',c='#555',label='all other books')
ax[0].set_ylabel('% of books with no ISBN'); ax[0].set_title('BNP national bibliography: books without ISBN')
ax[1].bar(g.index-0.2,g.ap_isbn,0.4,label='AP with ISBN',color='#2c7fb8'); ax[1].bar(g.index+0.2,g.ap_noisbn,0.4,label='AP without ISBN',color='#c0392b')
ax[1].set_title('Author = publisher books, counts')
for a in ax: a.axvline(2014.5,ls=':',c='k'); a.legend(fontsize=8); a.set_xlabel('publication year')
plt.tight_layout(); plt.savefig('output/paper_pt/fig_natbib_noisbn_ap_vs_other.png',dpi=150)
