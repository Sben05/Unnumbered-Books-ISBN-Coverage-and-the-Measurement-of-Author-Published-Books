"""Within-Portugal dose-response. Per-ISBN price implied by APEL tariff (excl. VAT): single author ISBN 15; 10-block 10 (professional) / 15 (non-professional); 100-block 5 / 7.5; 1,000-block 3 / 4.5.
Groups (publisher size 2005-12 -> typical block): AP/single = 15; tiny, small = 10-15 (use 12.5); medium = 5-7.5 (6.25); large = 3-4.5 (3.75).
Prediction if price drives it: change in no-ISBN share (2015-18 vs 2011-14) rises with per-ISBN price. Estimate group changes (logit and pp) with bootstrap CIs; slope of change on log price."""
import re, unicodedata, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2011,2018)].copy(); R['y']=R.pub_year.astype(int)
allR=pd.read_parquet('data/interim/pt_natbib_records.parquet'); allR=allR[allR.print_like&allR.pt&allR.pub_year.between(2005,2012)]
def norm(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',s)).strip()
allR['pk']=allR.publisher.map(norm); R['pk']=R.publisher.map(norm)
cnt=allR[(~allR.ap)&(allR.pk!='')].groupby('pk').size()
def grp(r):
    if r.ap: return 'self-published (single ISBN)'
    n=cnt.get(r.pk,0); return 'large' if n>=100 else 'medium' if n>=20 else 'small' if n>=5 else 'tiny' if n>=1 else 'new'
R['g']=[grp(r) for r in R.itertuples()]; R['noisbn']=(~R.has_isbn).astype(int); R['post']=(R.y>=2015).astype(int)
price={'self-published (single ISBN)':15.0,'tiny':12.5,'small':12.5,'medium':6.25,'large':3.75}
lg=lambda p:np.log(np.clip(p,1e-3,1-1e-3)/(1-np.clip(p,1e-3,1-1e-3)))
rows=[]; rng=np.random.default_rng(4)
for g,p in price.items():
    d=R[R.g==g]; a=d[d.post==0].noisbn.values; b=d[d.post==1].noisbn.values
    ch=lg(b.mean())-lg(a.mean()); bs=[lg(rng.choice(b,len(b)).mean())-lg(rng.choice(a,len(a)).mean()) for _ in range(2000)]
    rows.append(dict(group=g,price_eur_per_isbn=p,books_pre=len(a),books_post=len(b),noisbn_pre=a.mean(),noisbn_post=b.mean(),change_pp=100*(b.mean()-a.mean()),change_logit=ch,ci_low=np.percentile(bs,2.5),ci_high=np.percentile(bs,97.5)))
T=pd.DataFrame(rows); print(T.round(3).to_string(index=False)); T.to_csv('output/paper_pt/price_gradient.csv',index=False)
w=1/((T.ci_high-T.ci_low)/3.92)**2; x=np.log(T.price_eur_per_isbn); b=np.polyfit(x,T.change_logit,1,w=np.sqrt(w)); print('weighted slope of change (logit) on log price: %.2f per log-euro (positive = bigger change at higher price)'%b[0])
print('Spearman(price, change):',round(T.price_eur_per_isbn.corr(T.change_logit,method='spearman'),2),'| excluding self-published:',round(T[~T.group.str.startswith('self')].price_eur_per_isbn.corr(T[~T.group.str.startswith('self')].change_logit,method='spearman'),2))
fig,ax=plt.subplots(figsize=(6.2,4.2)); ax.errorbar(T.price_eur_per_isbn,T.change_logit,yerr=[T.change_logit-T.ci_low,T.ci_high-T.change_logit],fmt='o',c='#c0392b',capsize=4)
for _,r in T.iterrows(): ax.annotate(r.group,(r.price_eur_per_isbn,r.change_logit),xytext=(5,5),textcoords='offset points',fontsize=8)
ax.axhline(0,c='#999',lw=.8); ax.set_xscale('log'); ax.set_xlabel('implied price per ISBN (EUR, excl. VAT, log scale)'); ax.set_ylabel('change in no-ISBN share, 2015-18 vs 2011-14 (logit)'); ax.set_title('Within-Portugal price gradient')
plt.tight_layout(); plt.savefig('output/paper_pt/fig_price_gradient.png',dpi=150)
