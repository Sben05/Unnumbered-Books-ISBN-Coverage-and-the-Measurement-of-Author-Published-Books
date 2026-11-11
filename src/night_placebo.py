"""Placebo-in-space-and-time inference for the fee event studies. Treated effect = mean k=0..3 post gap (logit).
Placebo pool: control units x fake event years (correlated across adjacent years -> p-values are rough)."""
import numpy as np, pandas as pd, itertools
exec(open('src/night_events.py').read().split("rows=[];res={}")[0])  # reuse loaders
def eff(treated,donors,E,PRE_,POSTK=3):
    pre=list(range(E-PRE_,E)); yrs=list(range(E-PRE_,E+POSTK+1))
    y=lg(S[treated].reindex(yrs)); D=pd.DataFrame({d:lg(S[d].reindex(yrs)) for d in donors})
    if y.isna().any(): return None
    D=D.dropna(axis=1)
    if D.shape[1]<2: return None
    def detr(s):
        b=np.polyfit(pre,s.loc[pre].values,1); return s-np.polyval(b,np.array(s.index))
    did=(y-y.loc[pre].mean())-(D-D.loc[pre].mean()).mean(axis=1)
    dt=detr(y)-pd.DataFrame({d:detr(D[d]) for d in D}).mean(axis=1)
    p=slice(E,E+POSTK)
    return did.loc[p].mean(), dt.loc[p].mean()
pool=['nz','uk','fr','qc']
rows=[]
for E in range(2000,2017):
  for PRE_ in (5,7):
    for u in pool:
        donors=[d for d in pool if d!=u]
        if u=='fr' and E+3>=2019: continue
        donors=[d for d in donors if not (d=='fr' and E+3>=2019)]
        r=eff(u,donors,E,PRE_)
        if r: rows.append(dict(unit=u,E=E,PRE=PRE_,did=r[0],did_tr=r[1]))
P=pd.DataFrame(rows); P.to_csv('output/night/placebo_pool.csv',index=False)
tr=[('es',2012,5,['nz','uk','fr']),('pt',2015,7,['nz','uk','fr']),('fr',2019,7,['nz','qc'])]
out=[]
for u,E,pr,don in tr:
    r=eff(u,don,E,pr)
    for i,m in enumerate(['did','did_tr']):
        sub=P[P.PRE==pr][m]
        out.append(dict(unit=u,event=E,donors='+'.join(don),method=m,effect_logit=r[i],pct=np.expm1(r[i])*100,
          n_placebo=len(sub),placebo_sd=sub.std(),z=r[i]/sub.std(),p_two_sided=float((sub.abs()>=abs(r[i])).mean()),
          p_one_sided_fall=float((sub<=r[i]).mean())))
O=pd.DataFrame(out); O.to_csv('output/night/placebo_inference.csv',index=False); print(O.round(3).to_string())
# pooled mean of ES+PT (the two 'paid-after-free' falls) vs placebo pair means
a_=O[O.unit.isin(['es','pt'])].groupby('method').effect_logit.mean(); print(a_)
