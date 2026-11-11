import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
OUT=ROOT/'output/selfpub';F=OUT/'figures';P=pd.read_csv(OUT/'panel.csv')
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
C={'nz':'#1b7f5c','uk':'#245a9b','fr':'#bd4d30','qc':'#8a5fb3','us':'#444444','amz':'#d98e04'};L={'nz':'New Zealand (free ISBN)','uk':'UK (paid)','fr':'France','qc':'Québec (free)','us':'US, Library of Congress (paid)','amz':'US-centred Amazon marketplace'}
def sh(s,col,lo,hi):
    d=P[(P.source==s)&P.pub_year.between(lo,hi)];return d.pub_year,100*d[col]/d.n
# 1 author=publisher shares
fig,ax=plt.subplots(figsize=(10,5.6))
for s,lo,hi in [('nz',1995,2022),('uk',1995,2014),('us',1995,2011),('fr',2005,2021),('qc',2010,2021)]:
    x,y=sh(s,'ap',lo,hi);ax.plot(x,y,color=C[s],lw=2.2,label=L[s])
ax.axvline(2007.5,color='#999',ls='--',lw=1);ax.text(2007.7,ax.get_ylim()[1]*.93,'Kindle / CreateSpace era',fontsize=8,color='#666')
ax.set(ylabel='Author = publisher, % of print ISBNs',xlabel='Publication year',title='Self-publishing under the author’s own name, national bibliographies');ax.legend(frameon=False,fontsize=9);ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(F/'ap_share_all.png');plt.close(fig)
# 2 Amazon timeline
amz=P[(P.source=='amz')&P.pub_year.between(2000,2022)].set_index('pub_year')
fig,(a1,a2)=plt.subplots(1,2,figsize=(12,5))
a1.semilogy(amz.index,amz.amazon_imprint.clip(lower=1),color=C['amz'],lw=2.4,label='CreateSpace / “Independently published” print records');
a1.semilogy(amz.index,amz.i9798.clip(lower=1),color='#222',lw=1.6,ls=':',label='979-8 ISBNs (US block, Amazon KDP era)');a1.set(title='Amazon-issued ISBNs on Amazon',ylabel='records (log scale)',xlabel='Publication year');a1.legend(frameon=False,fontsize=8);a1.grid(alpha=.2)
for s,lo,hi in [('nz',2000,2022),('uk',2000,2014),('us',2000,2011)]:
    x,y=sh(s,'ap',lo,hi);a2.plot(x,y,color=C[s],lw=2.2,label=L[s])
a2.axvline(2007.5,color='#999',ls='--',lw=1);a2.set(title='…and author=publisher shares in national bibliographies',ylabel='% of print ISBNs',xlabel='Publication year');a2.legend(frameon=False,fontsize=8);a2.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(F/'amazon_timeline.png');plt.close(fig)
# 3 Amazon marketplace share vs Bowker
fig,ax=plt.subplots(figsize=(8.5,5))
x,y=sh('amz','sp',1999,2022);ax.plot(x,y,color=C['amz'],lw=2.4,label='Amazon sample: combined self-published share')
ax.scatter([2007,2012],[11,40],color='k',zorder=3,label='Bowker (ISBN share, published figures)');ax.set(ylabel='% of print ISBNs',xlabel='Publication year',title='Marketplace self-publishing boom (US-centred)');ax.legend(frameon=False,fontsize=9);ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(F/'amazon_vs_bowker.png');plt.close(fig)
# 4 FR/QC gap
g=pd.read_csv(OUT/'frqc_gap_series.csv');fig,(a1,a2)=plt.subplots(1,2,figsize=(12,5))
for s,col,lab in [('fr',C['fr'],'France (free until Mar 2019)'),('qc',C['qc'],'Québec (free)')]:
    x,y=sh(s,'ap',2010,2021);a1.plot(x,y,color=col,lw=2.3,marker='o',ms=3,label=lab)
a1.axvline(2018.8,color='#777',ls='--',lw=1);a1.set(title='Author = publisher share',ylabel='%',xlabel='Publication year');a1.legend(frameon=False);a1.grid(axis='y',alpha=.2)
d=g[g.outcome=='ap'];se=np.sqrt(d['var']);a2.errorbar(d.pub_year,d.gap,yerr=1.96*se,color='k',marker='o',ms=4,capsize=2,lw=1.2)
pre=d[d.pub_year<=2018];b=np.polyfit(pre.pub_year,pre.gap,1);xs=np.arange(2010,2022);a2.plot(xs,np.polyval(b,xs),color='#999',ls='--',label='pre-2019 linear trend')
a2.axvline(2018.8,color='#777',ls='--',lw=1);a2.set(title='France − Québec gap in log-odds (author=publisher)',xlabel='Publication year',ylabel='log-odds difference');a2.legend(frameon=False);a2.grid(alpha=.2);fig.tight_layout();fig.savefig(F/'frqc_parallel_trends.png');plt.close(fig)
# 5 per-capita
pc=pd.read_csv(OUT/'per_capita.csv');fig,ax=plt.subplots(figsize=(9,5))
for s,lo,hi in [('nz',1995,2022),('qc',2010,2021),('fr',1995,2021),('uk',1995,2014),('us',1995,2011)]:
    d=pc[(pc.source==s)&pc.pub_year.between(lo,hi)];ax.plot(d.pub_year,d.ap_per_m,color=C[s],lw=2.2,label=L[s])
ax.set(yscale='log',ylabel='author=publisher print ISBNs per million people (log)',xlabel='Publication year',title='Self-publishing per capita');ax.legend(frameon=False,fontsize=9);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(F/'per_capita_ap.png');plt.close(fig)
print('figs done')
