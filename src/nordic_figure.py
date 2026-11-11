"""Combined figure: NO/SE (free ISBN, Nordic) vs NZ/QC (free) and FR/UK (paid); % of print ISBNs flagged self-published (author=publisher or service imprint)."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd,numpy as np
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from nordic_common import wilson
S=[('norway','NO','Norway (free)','#1b7837','-'),('sweden','SE','Sweden (free)','#5aae61','-'),('nz','NZ','New Zealand (free)','#2166ac','--'),('qc','QC','Quebec (free)','#67a9cf','--'),('fr','FR','France (paid)','#b2182b','-.'),('uk','UK','UK (paid)','#ef8a62','-.')]
rows=[]
for k,cc,lab,col,ls in S:
 f=ROOT/('output/%s/%s_by_year.csv'%(k,cc.lower()))
 if cc in('NO','SE'):
  if not f.exists():continue
  d=pd.read_csv(f).rename(columns={'combined':'k','print_isbns':'n'})[['pub_year','k','n']]
  d['ap']=pd.read_csv(f)['ap']
 else:
  c=pd.read_parquet(ROOT/f'data/interim/{k}_classified.parquet',columns=['pub_year','self_pub','author_is_publisher'])
  g=c.groupby('pub_year').agg(k=('self_pub','sum'),n=('self_pub','size'),ap=('author_is_publisher','sum')).reset_index()
  d=g
 d=d[d.pub_year.between(1995,2022)].copy();d['label']=lab;d['cc']=cc;d['share']=d.k/d.n;d['ap_share']=d.ap/d.n
 d[['wl','wh']]=[wilson(a,b) for a,b in zip(d.k,d.n)];rows.append((d,col,ls))
fig,axs=plt.subplots(1,2,figsize=(12,4.6),sharex=True)
for d,col,ls in rows:
 axs[0].plot(d.pub_year,d.share*100,color=col,ls=ls,lw=1.8,label=d.label.iloc[0]);axs[0].fill_between(d.pub_year,d.wl*100,d.wh*100,color=col,alpha=.08)
 axs[1].plot(d.pub_year,d.ap_share*100,color=col,ls=ls,lw=1.8,label=d.label.iloc[0])
axs[0].set_title('Self-published share: author=publisher or service imprint',fontsize=10);axs[1].set_title('Author = publisher only',fontsize=10)
for a in axs:a.set_xlabel('Publication year');a.set_ylabel('% of print ISBNs');a.spines[['top','right']].set_visible(False)
axs[0].legend(frameon=False,fontsize=8)
fig.text(.01,.01,'Descriptive. Same classifier (classify_selfpub.flags) with Nordic phrase/service additions. Coverage differs: NO = nb.no records with 978-82 ISBN (incl. no print/e-book split); SE = Svensk bibliografi print monographs; cataloguing practice differs by agency. Shaded = 95% Wilson CI.',fontsize=6)
fig.tight_layout(rect=(0,.04,1,1));(ROOT/'output/nordics').mkdir(exist_ok=True);fig.savefig(ROOT/'output/nordics/nordics_vs_nz_qc_fr_uk.png',dpi=160)
pd.concat([d[['label','pub_year','k','n','share','ap','ap_share','wl','wh']] for d,_,_ in rows]).to_csv(ROOT/'output/nordics/combined_series.csv',index=False)
