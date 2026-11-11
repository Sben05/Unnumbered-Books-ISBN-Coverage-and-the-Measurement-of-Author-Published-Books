"""Sensitivity variants per Nordic country: shares by year under alternative definitions, plus pooled 5-year blocks. Usage: nordic_extra.py no|se"""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from nordic_common import wilson
cc=sys.argv[1];name={'no':'norway','se':'sweden'}[cc]
R=pd.read_parquet(ROOT/f'data/interim/{cc}_classified.parquet');R['pub_year']=R.pub_year.astype(int)
init=R.author_is_publisher&(R.classification_reason=='compatible_initials');T=pd.Series(True,index=R.index)
V={'main':(T,R.self_pub),'author_only':(T,R.author_is_publisher),'service_only':(T,R.service_imprint),'exclude_initials_matches':(T,R.self_pub&~init),
 'exclude_government':(~R.government,R.self_pub),'exclude_reprints':(~R.reprint_or_new_edition,R.self_pub),'exclude_unidentified_publisher':(~R.unidentified_publisher,R.self_pub),
 'include_mixed_candidates':(T,R.self_pub|R.service_mixed),'exclude_bod_lulu_etc_platforms':(T,R.author_is_publisher|R.service_author_services)}
rows=[]
for k,(den,num) in V.items():
 for y,idx in R[den].groupby('pub_year').groups.items():
  n=len(idx);kk=int(num.loc[idx].sum());lo,hi=wilson(kk,n);rows.append(dict(variant=k,pub_year=y,denominator=n,numerator=kk,share=kk/n,wilson_low=lo,wilson_high=hi))
S=pd.DataFrame(rows);S.to_csv(ROOT/f'output/{name}/{cc}_sensitivity.csv',index=False)
S['block']=(S.pub_year//5*5).astype(str)+'s';P=S.groupby(['variant','block'])[['denominator','numerator']].sum().reset_index();P['share']=P.numerator/P.denominator
print(P.pivot(index='block',columns='variant',values='share').round(4).to_string())
print('top author_is_publisher match types:',R[R.author_is_publisher].classification_reason.value_counts().head(6).to_dict())
print('services:',R[R.service_imprint].matched_services.value_counts().to_dict());print('mixed:',R[R.service_mixed].matched_services.value_counts().to_dict())
print('explicit',int(R.explicit_author_statement.sum()),'unid',int(R.unidentified_publisher.sum()),'gov',int(R.government.sum()))
P.to_csv(ROOT/f'output/{name}/{cc}_sensitivity_5yr.csv',index=False)
