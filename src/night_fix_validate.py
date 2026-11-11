"""Re-score LLM-labelled validation rows under each fix (standalone and combined). IPW weights = original stratum size / labelled n in stratum."""
import sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import pandas as pd,numpy as np
OUT=ROOT/'output/night_fixed'
SPAN={'es':(2007,2021),'pt':(2005,2025)}
def wil(k,n):
 if not n:return (np.nan,np.nan)
 z=1.96;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return round(c-h,3),round(c+h,3)
rows=[]
for s in ['uk','nz','fr','qc','es','pt']:
 F=pd.read_parquet(OUT/f'rowflags_{s}.parquet')
 if s in SPAN:F=F[F.pub_year.between(*SPAN[s])]
 F['svc_all']=F.svc_orig|F.svc_add;F['strat_f']=F.ap_stored|F.svc_orig
 Nf,Nu=int(F.strat_f.sum()),int((~F.strat_f).sum())
 V=pd.read_csv(ROOT/f'output/validation_labelled/validation_{s}_labelled.csv',dtype={'record_key':str})
 V['key']=V.record_key.str.split(':',n=1).str[-1] if s in('uk','nz','fr') else V.record_key
 kc='record_id' if s in('uk','nz','fr','qc') else 'isbn13'
 U=F.drop_duplicates(kc).set_index(kc)
 V=V.drop(columns=['pub_year'],errors='ignore').drop_duplicates('record_key').join(U,on='key',how='left');V=V[V.label.astype(str).isin(['0','1'])&V.ap_orig.notna()].copy();V['y']=V.label.astype(int)
 nf=(V.stratum=='flagged').sum();nu=(V.stratum=='unflagged').sum();V['w']=np.where(V.stratum=='flagged',Nf/nf,Nu/nu)
 def fl(ap,svc,newsvc_only=False):
  f=(V.stratum=='flagged')
  return np.where(f,ap|svc,(ap&~V.ap_orig.astype(bool))|(svc&~V.svc_orig.astype(bool)))
 specs={'original':(V.ap_orig.astype(bool),V.svc_orig.astype(bool)),'a_org_guard':(V.ap_org.astype(bool),V.svc_orig.astype(bool)),'a_dead_guard':(V.ap_dead.astype(bool),V.svc_orig.astype(bool)),
  'b_corporate':(V.ap_corp.astype(bool),V.svc_orig.astype(bool)),'c_services':(V.ap_orig.astype(bool),V.svc_all.astype(bool)),'d_single_token':(V.ap_single.astype(bool),V.svc_orig.astype(bool)),'all_fixes':(V.ap_all.astype(bool),V.svc_all.astype(bool))}
 for nm,(ap,svc) in specs.items():
  f=pd.Series(fl(ap,svc),index=V.index).astype(bool)
  tp=(f&(V.y==1));fp=(f&(V.y==0));fn=(~f&(V.y==1))
  r=dict(source=s,variant=nm,n_labelled=len(V),sample_TP=int(tp.sum()),sample_FP=int(fp.sum()),sample_FN=int(fn.sum()),
   precision=tp.sum()/max(1,f.sum()),prec_lo=wil(tp.sum(),f.sum())[0],prec_hi=wil(tp.sum(),f.sum())[1])
  TP,FN=(V.w*tp).sum(),(V.w*fn).sum();r['ipw_recall']=TP/(TP+FN) if TP+FN else np.nan;r['ipw_TP']=round(TP);r['ipw_FN']=round(FN);r['ipw_flagged']=round((V.w*f).sum())
  rows.append(r)
R=pd.DataFrame(rows);R.to_csv(OUT/'validation_rescored.csv',index=False)
print(R.round(3).to_string(index=False))
