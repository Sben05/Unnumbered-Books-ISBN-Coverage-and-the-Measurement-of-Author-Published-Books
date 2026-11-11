"""By-year tables (Wilson CIs, per million), sensitivity variants, validation sample and figure for an extra country.
usage: extra_analysis.py <cc> <iso3> <outdir> <label>"""
import sys,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
warnings.filterwarnings('ignore')
from extra_common import *
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
cc,iso3,outd,label=sys.argv[1:5];OUT=ROOT/'output'/outd;OUT.mkdir(parents=True,exist_ok=True)
R=pd.read_parquet(ROOT/f'data/interim/{cc}_classified.parquet')
B=by_year(R,iso3);B.insert(0,'country',iso3);B.to_csv(OUT/f'{cc}_by_year.csv',index=False)
# sensitivity
R9=R[R.pub_year.between(1995,2023)].copy();R9['pub_year']=R9.pub_year.astype(int);T=pd.Series(True,index=R9.index)
V={'main_combined':(T,R9.self_published_combined),'ap_consistent':(T,R9.ap_consistent),'ap_strict':(T,R9.author_is_publisher),'exclude_government':(~R9.government,R9.self_published_combined),
 'exclude_reprints':(~R9.reprint,R9.self_published_combined),'exclude_unidentified_publisher':(~R9.unidentified_publisher,R9.self_published_combined),'include_mixed_candidates':(T,R9.self_published_combined|R9.service_mixed),'explicit_phrase_only':(T,R9.explicit)}
S=[]
for k,(den,num) in V.items():
 for y,idx in R9[den].groupby('pub_year').groups.items():
  n=len(idx);kk=int(num.loc[idx].sum());a,b=wilson(kk,n);S.append(dict(variant=k,pub_year=y,denominator=n,numerator=kk,share=kk/n,wilson_low=a,wilson_high=b))
pd.DataFrame(S).to_csv(OUT/f'{cc}_sensitivity.csv',index=False)
# no-ISBN records
try:
 N=pd.read_parquet(ROOT/f'data/interim/{cc}_noisbn.parquet');N=N[N.pub_year.between(1995,2023)]
 NB=N.groupby('pub_year').agg(records_without_isbn=('record_id','size'),combined=('self_published_combined','sum'),ap_consistent=('ap_consistent','sum')).reset_index();NB['share_combined']=NB.combined/NB.records_without_isbn;NB.to_csv(OUT/f'{cc}_noisbn_by_year.csv',index=False)
except Exception as e:print('noisbn skipped',e)
# ISBN prefix composition
R9['isbn_prefix']=R9.isbn13.str[:7]
# figure
fig,ax=plt.subplots(figsize=(8.5,4.4))
for c,col,lab in [('combined','#1f3b73','Combined (AP or service)'),('ap_consistent','#c8572b','Author = publisher (consistent rule)'),('service','#2a8c6e','Service imprint')]:
 ax.plot(B.pub_year,B['share_'+c]*100,marker='o',ms=3,color=col,label=lab,lw=1.6);ax.fill_between(B.pub_year,B[c+'_wilson_low']*100,B[c+'_wilson_high']*100,color=col,alpha=.12)
ax.set_ylabel('% of print ISBNs');ax.set_xlabel('Publication year');ax.set_title(f'{label}: self-published share of catalogued print ISBNs',fontsize=10);ax.legend(frameon=False,fontsize=8);ax.spines[['top','right']].set_visible(False)
fig.text(.01,.01,'Descriptive; 95% Wilson CIs (nominal). Classifier precision from a 60-record read (see validation_read.md).',fontsize=6.5);fig.tight_layout(rect=(0,.03,1,1));fig.savefig(OUT/f'{cc}_shares.png',dpi=150)
S2=validation_sample(R,OUT/f'validation_{cc}.csv')
print(B[['pub_year','print_isbns','combined','share_combined','ap_consistent','share_ap_consistent','service','print_isbns_per_million']].to_string())
