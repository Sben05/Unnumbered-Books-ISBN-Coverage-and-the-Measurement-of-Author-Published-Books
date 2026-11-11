"""H7/H9: France 2019 fee event with Amazon-issued (979-8 / CreateSpace-type) AP records removed from numerator AND denominator."""
import duckdb, numpy as np, pandas as pd
c=duckdb.connect(); S={}
for f in ['fr','qc','nz']:
    d=c.execute(f"select pub_year y, count(*) filter (where not (us_9798 or amazon_imprint)) n, count(*) filter (where author_is_publisher and not (us_9798 or amazon_imprint)) ap from 'data/interim/{f}_classified.parquet' where pub_year between 2008 and 2022 group by 1 order by 1").df().set_index('y')
    S[f]=d.ap/d.n
def lg(p): return np.log(p/(1-p))
def eff(t,donors,E,PRE,POSTK):
    pre=list(range(E-PRE,E)); yrs=list(range(E-PRE,E+POSTK+1)); y=lg(S[t].reindex(yrs)); D=pd.DataFrame({d:lg(S[d].reindex(yrs)) for d in donors})
    det=lambda s: s-np.polyval(np.polyfit(pre,s.loc[pre].values,1),np.array(s.index))
    did=(y-y.loc[pre].mean())-(D-D.loc[pre].mean()).mean(axis=1)
    dt=det(y)-pd.DataFrame({d:det(D[d]) for d in D}).mean(axis=1)
    return did, dt
for POSTK in (1,2):
    for t,don in [('fr',['nz','qc'])]:
        did,dt=eff(t,don,2019,7 if True else 7,POSTK)
        print('post years 0..',POSTK,'DiD by k',did.round(3).tolist(),' mean post',round(did.loc[2019:].mean(),3),'| trend-adj',dt.round(3).tolist(),round(dt.loc[2019:].mean(),3))
# placebo: pseudo events 2013-2016 (3 post yrs not needed: use same 0..2) for fr,nz,qc vs the others
res=[]
for E in range(2012,2017):
    for t in ['fr','nz','qc']:
        don=[x for x in ['fr','nz','qc'] if x!=t]
        try: did,dt=eff(t,don,E,min(5,E-2008),2); res.append((t,E,did.loc[E:].mean(),dt.loc[E:].mean()))
        except Exception as e: pass
P=pd.DataFrame(res,columns=['t','E','did','dt']); print(P.round(3).to_string()); P.to_csv('output/night/fr_noamz_placebos.csv',index=False)
