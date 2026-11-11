"""PHASE 4 robustness: level-shift-vs-pre-trend statistic at B=2015 for PT series; placebo breaks; windows; excl-2014; finite-resolution inference.
Stat(B) = mean_{t=B..B+3}[ y_t - fitted_pre_trend(t) ] with the trend fitted by OLS on y over [lo, B-1]. y = log(count) or logit(share).
Inference: rank of |Stat(2015)| among placebo breaks B in 2010..2016 using the same pre-window length rule; p_min = 1/(#breaks). Not a significance test in the usual sense."""
import duckdb, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
c=duckdb.connect(); P="data/interim/pt_classified.parquet"
r="(?i)associa|f[aá]brica|grupo|instituto|comunidade|freguesia|c[aâ]mara|munic|centro|ordem|ag[eê]ncia|funda|universidade|escola|junta|clube|sociedade"
q=f"""select pub_year y, count(*) n,
 sum(ap_consistent::int) ap_cons, sum(author_is_publisher::int) ap_orig, sum(ap_pure::int) ap_pure,
 sum((isbn13 like '97898920%' or isbn13 like '97898933%')::int) author_ed,
 sum(((isbn13 like '97898920%' or isbn13 like '97898933%') and not ap_consistent)::int) author_ed_nonAP,
 sum(((isbn13 like '97898920%' or isbn13 like '97898933%') and ap_consistent)::int) ap_in_author_ed,
 sum((ap_consistent and not (isbn13 like '97898920%' or isbn13 like '97898933%'))::int) ap_not_author_ed,
 sum((ap_consistent and isbn13 like '978989%' and not (isbn13 like '97898920%' or isbn13 like '97898933%'))::int) ap_989_other,
 sum((ap_consistent and not government and not regexp_matches(coalesce(publisher_full,''),'{r}'))::int) ap_cons_noinst,
 sum((ap_consistent and coalesce(edition,'') ~ '(?i)1\\.?[ªa]|primeira|1st' )::int) ap_cons_firstedlike,
 sum((isbn13 like '978972%' or isbn13 like '978989%')::int) n_pt
 from '{P}' where pub_year between 2005 and 2019 group by 1 order by 1"""
d=c.execute(q).df().set_index('y')
nn=c.execute("select cast(pub_year as int) y, sum(ap_consistent::int) noisbn_ap from 'data/interim/pt_noisbn.parquet' where pub_year between 2005 and 2019 group by 1").df().set_index('y')
d=d.join(nn); d['ap_total_incl_noisbn']=d.ap_cons+d.noisbn_ap
lg=lambda p:np.log(p/(1-p))
S={}
for k in ['ap_cons','ap_orig','ap_pure','author_ed','author_ed_nonAP','ap_in_author_ed','ap_not_author_ed','ap_989_other','ap_cons_noinst']:
    S[k+' (logit share)']=lg(d[k]/d.n)
S['ap_total_incl_noisbn (log count)']=np.log(d.ap_total_incl_noisbn); S['noisbn_ap (log count)']=np.log(d.noisbn_ap)
S['author_ed (log count)']=np.log(d.author_ed); S['n print ISBNs (log count)']=np.log(d.n)
def stat(y,B,lo,H=4,excl=()):
    yrs=[t for t in range(lo,B) if t not in excl]; x=np.array(yrs); b=np.polyfit(x,y.loc[yrs].values,1)
    post=[t for t in range(B,B+H) if t in y.index]; return float(np.mean([y.loc[t]-np.polyval(b,t) for t in post])), len(yrs)
rows=[]
for name,y in S.items():
    for label,lo,excl in [('pre 2005-14',2005,()),('pre 2008-14',2008,()),('pre 2010-14',2010,()),('pre 2005-14 excl 2014',2005,(2014,)),('pre 2007-13 (2014 dropped)',2007,(2014,))]:
        s15,npre=stat(y,2015,lo,excl=excl)
        maxB=2013 if excl else 2014
        pl=[stat(y,B,lo,excl=excl)[0] for B in range(lo+4,maxB+1)]
        allv=pl+[s15]; rank=1+sum(abs(v)>=abs(s15) for v in pl)
        rows.append(dict(series=name,window=label,stat2015=s15,n_pre=npre,pct=100*(np.exp(s15)-1) if 'log count' in name or True else None,placebo_mean=np.mean(pl),placebo_sd=np.std(pl),rank_abs=rank,n_breaks=len(allv),p_min_resolution=1/len(allv)))
R=pd.DataFrame(rows); R.to_csv('output/paper_pt/robust_level_shift.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(R[R.window.isin(['pre 2005-14','pre 2005-14 excl 2014'])][['series','window','stat2015','rank_abs','n_breaks','placebo_sd']].round(3).to_string(index=False))
d.to_csv('output/paper_pt/robust_series.csv')
# Figure: counts of the alternative measures
fig,ax=plt.subplots(1,3,figsize=(15,4))
ax[0].plot(d.index,d.ap_cons,label='AP name-match (consistent)',lw=2); ax[0].plot(d.index,d.author_ed,label='Author-edition prefixes 989-20+33',lw=2); ax[0].plot(d.index,d.ap_total_incl_noisbn,label='AP incl. ISBN-less',lw=1.5,ls='--')
ax[0].set_title('Counts, catalogued print books by publication year'); ax[0].legend(fontsize=7)
ax[1].plot(d.index,d.ap_in_author_ed,label='AP & author-ed prefix'); ax[1].plot(d.index,d.ap_989_other,label='AP & other 989 prefix'); ax[1].plot(d.index,d.author_ed_nonAP,label='author-ed prefix & not AP (inst./imprint)'); ax[1].set_title('Cross-classification'); ax[1].legend(fontsize=7)
ax[2].plot(d.index,d.ap_cons/d.n*100,label='AP share %'); ax[2].plot(d.index,d.author_ed/d.n*100,label='author-ed prefix share %'); ax[2].set_title('Shares of catalogued print ISBNs'); ax[2].legend(fontsize=7)
for a in ax: a.axvline(2014.5,ls=':',c='k'); a.set_xlabel('publication year')
plt.tight_layout(); plt.savefig('output/paper_pt/fig_ap_vs_author_edition.png',dpi=150)
