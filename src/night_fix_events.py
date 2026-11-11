"""Event-study + placebo inference on the FIXED (and, for reproduction, ORIGINAL) author=publisher series.
Logic copied from night_events.py / night_placebo.py. Usage: night_fix_events.py [ap|combined]. Writes output/night_fixed/."""
import sys,numpy as np,pandas as pd
from pathlib import Path
from scipy.optimize import nnls
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'output/night_fixed'
KIND=sys.argv[1] if len(sys.argv)>1 else 'ap'
SFX='' if KIND=='ap' else '_combined'
def lg(p):p=np.clip(p,1e-6,1-1e-6);return np.log(p/(1-p))
def load(version):
 S={}
 for s in ['uk','nz','fr','qc','es','pt']:
  d=pd.read_csv(OUT/f'fixed_by_year_{s}.csv').set_index('pub_year')
  if s=='es':d=d.loc[2007:]   # original es_by_year starts 2007
  if s=='pt':d=d.loc[2005:2025]
  num=d[('ap_' if KIND=='ap' else 'combined_')+version]
  S[s]=num/d.print_isbns
 return S
events={'es':2012,'pt':2015,'fr':2019};donors_for={'es':['nz','uk','fr'],'pt':['nz','uk','fr'],'fr':['nz','qc','uk']};PREd={'es':5,'pt':7,'fr':7};POST=4
def est(S,treated,donors,E,PRE):
 w_=lambda u:lg(S[u].reindex(range(E-PRE,E+POST+1)))
 y=w_(treated);D=pd.DataFrame({d:w_(d) for d in donors});pre=list(range(E-PRE,E))
 D=D[[d for d in D if D.loc[pre,d].notna().all()]]
 did=(y-y.loc[pre].mean())-(D-D.loc[pre].mean()).mean(axis=1)
 def detr(s):b=np.polyfit(np.array(pre),s.loc[pre].values,1);return s-np.polyval(b,np.array(s.index))
 did_tr=detr(y)-pd.DataFrame({d:detr(D[d]) for d in D}).mean(axis=1)
 A=D.loc[pre].values;b=y.loc[pre].values;w,_=nnls(np.vstack([A,1e3*np.ones(A.shape[1])]),np.append(b,1e3));w=w/w.sum() if w.sum()>0 else w
 sc=y-pd.Series(D.values@w,index=D.index)
 return dict(did=did,did_tr=did_tr,sc=sc,w=dict(zip(D.columns,np.round(w,3))),pre_rmse=float(np.sqrt((sc.loc[pre]**2).mean())),donors=list(D.columns))
def summary(S):
 rows=[];ev=[];pl=[]
 for u,E in events.items():
  r=est(S,u,donors_for[u],E,PREd[u])
  for m in ['did','did_tr','sc']:
   for t,v in r[m].items():ev.append(dict(unit=u,event=E,method=m,k=int(t-E),effect_logit=v))
  for d in donors_for[u]:
   try:r2=est(S,d,[x for x in donors_for[u] if x!=d],E,PREd[u])
   except Exception:continue
   for m in ['did','did_tr','sc']:
    for t,v in r2[m].items():pl.append(dict(treated=u,placebo=d,method=m,k=int(t-E),effect_logit=v))
 ev=pd.DataFrame(ev);pl=pd.DataFrame(pl)
 for u,E in events.items():
  for m in ['did','did_tr','sc']:
   e=ev[(ev.unit==u)&(ev.method==m)&ev.k.between(0,3)].effect_logit.mean()
   p=pl[(pl.treated==u)&(pl.method==m)&pl.k.between(0,3)].groupby('placebo').effect_logit.mean()
   rows.append(dict(unit=u,event=E,method=m,mean_post_k0_3=e,n_placebos=len(p),placebo_abs_max=p.abs().max(),rank_abs_effect=(p.abs()>=abs(e)).sum()+1 if len(p) else np.nan,pct_effect=np.expm1(e)*100))
 return pd.DataFrame(rows)
def eff(S,treated,donors,E,PRE,POSTK=3):
 pre=list(range(E-PRE,E));yrs=list(range(E-PRE,E+POSTK+1));y=lg(S[treated].reindex(yrs));D=pd.DataFrame({d:lg(S[d].reindex(yrs)) for d in donors})
 if y.isna().any():return None
 D=D.dropna(axis=1)
 if D.shape[1]<2:return None
 def detr(s):b=np.polyfit(pre,s.loc[pre].values,1);return s-np.polyval(b,np.array(s.index))
 did=(y-y.loc[pre].mean())-(D-D.loc[pre].mean()).mean(axis=1);dt=detr(y)-pd.DataFrame({d:detr(D[d]) for d in D}).mean(axis=1)
 p=slice(E,E+POSTK);return did.loc[p].mean(),dt.loc[p].mean()
def inference(S):
 pool=['nz','uk','fr','qc'];rows=[]
 for E in range(2000,2017):
  for PRE_ in (5,7):
   for u in pool:
    if u=='fr' and E+3>=2019:continue
    donors=[d for d in pool if d!=u and not(d=='fr' and E+3>=2019)]
    r=eff(S,u,donors,E,PRE_)
    if r:rows.append(dict(unit=u,E=E,PRE=PRE_,did=r[0],did_tr=r[1]))
 P=pd.DataFrame(rows);out=[]
 for u,E,pr,don in [('es',2012,5,['nz','uk','fr']),('pt',2015,7,['nz','uk','fr']),('fr',2019,7,['nz','qc'])]:
  r=eff(S,u,don,E,pr)
  for i,m in enumerate(['did','did_tr']):
   sub=P[P.PRE==pr][m];out.append(dict(unit=u,event=E,donors='+'.join(don),method=m,effect_logit=r[i],pct=np.expm1(r[i])*100,n_placebo=len(sub),placebo_sd=sub.std(),z=r[i]/sub.std(),p_two_sided=float((sub.abs()>=abs(r[i])).mean()),p_one_sided_fall=float((sub<=r[i]).mean())))
 return pd.DataFrame(out)
if __name__=='__main__':
 res={}
 for v in ['orig','fixed']:
  S=load(v);es_=summary(S);pi=inference(S);es_.insert(0,'version',v);pi.insert(0,'version',v);res[v]=(es_,pi,S)
 pd.concat([res['orig'][0],res['fixed'][0]]).to_csv(OUT/f'event_summary{SFX}.csv',index=False)
 pd.concat([res['orig'][1],res['fixed'][1]]).to_csv(OUT/f'placebo_inference{SFX}.csv',index=False)
 pd.set_option('display.width',250)
 print(pd.concat([res['orig'][0],res['fixed'][0]]).round(3).to_string());print(pd.concat([res['orig'][1],res['fixed'][1]]).round(3).to_string())
 fig,ax=plt.subplots(2,3,figsize=(13,7),sharey=True)
 for r_,v in enumerate(['orig','fixed']):
  S=res[v][2]
  for a_,(u,E) in zip(ax[r_],events.items()):
   pr=PREd[u];yrs=list(range(E-pr,E+4));y=lg(S[u].reindex(yrs));y=y-y.loc[:E-1].mean()
   for d in donors_for[u]:
    z=lg(S[d].reindex(yrs));a_.plot([t-E for t in yrs],z-z.loc[:E-1].mean(),color='#bbb',lw=1.2);a_.text(3.1,(z-z.loc[:E-1].mean()).iloc[-1],d,fontsize=7,color='#777')
   a_.plot([t-E for t in yrs],y,color='#c0392b' if v=='fixed' else '#2c6fbb',lw=2.4,marker='o');a_.axvline(-0.5,ls='--',c='k',lw=.8);a_.set_title(f'{u.upper()} fee {E} ({v})',fontsize=10)
 ax[0][0].set_ylabel('logit share minus own pre-mean');ax[1][0].set_ylabel('logit share minus own pre-mean')
 fig.suptitle(f'{KIND} share around ISBN-fee introductions: original (blue, top) vs fixed rules (red, bottom); controls grey',fontsize=10)
 plt.tight_layout();plt.savefig(OUT/f'event_study{SFX}.png',dpi=130)
