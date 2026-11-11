"""Stacked event study + synthetic control over ISBN-fee introductions (ES 2012, PT 2015, FR 2019).
Outcome: logit AP share (author=publisher). Descriptive; AP rules differ by country so only within-unit changes are used."""
import numpy as np, pandas as pd, json
from scipy.optimize import nnls
R='output/'
def lg(p): p=np.clip(p,1e-6,1-1e-6); return np.log(p/(1-p))
a=pd.read_csv(R+'selfpub/all_by_year.csv'); a['ap']=a.author_is_publisher/a.print_isbns
S={s:g.set_index('pub_year').ap for s,g in a.groupby('source')}
es=pd.read_csv(R+'spain/es_by_year.csv').set_index('pub_year'); S['es']=es.ap/es.print_isbns
pt=pd.read_csv(R+'portugal/pt_ap_consistent_by_year.csv').set_index('pub_year'); S['pt']=pt.ap_consistent/pt.print_isbns
# FR is free until Mar 2019: usable as free-ISBN control for ES/PT; ES/PT charged after 2012/2015.
events={'es':2012,'pt':2015,'fr':2019}
donors_for={'es':['nz','uk','fr'],'pt':['nz','uk','fr'],'fr':['nz','qc','uk']}
PREd={'es':5,'pt':7,'fr':7}; POST=4; PRE=7
def window(u,E,span):
    s=S[u]; yrs=[y for y in range(E-PRE,E+POST+1) if y in s.index and (y<=span or True)]
    return lg(s.reindex(range(E-PRE,E+POST+1)))
def est(treated,donors,E):
    global PRE
    PRE=PREd[[k for k,v in events.items() if v==E][0]]
    y=window(treated,E,0); D=pd.DataFrame({d:window(d,E,0) for d in donors})
    pre=list(range(E-PRE,E)); post=[t for t in range(E,E+POST+1)]
    ok=[d for d in D if D.loc[pre,d].notna().sum()>=PRE-1 and D.loc[pre,d].notna().all()]
    D=D[ok]; mean_pre=lambda s:s.loc[pre].mean()
    # DiD (pre-mean normalised) vs equal-weight donors
    did=(y-mean_pre(y))-(D-D.loc[pre].mean()).mean(axis=1)
    # DiD with donor-specific linear pre-trend removed from both
    def detr(s):
        t=np.array(pre); b=np.polyfit(t,s.loc[pre].values,1); return s-np.polyval(b,np.array(s.index))
    did_tr=detr(y)-pd.DataFrame({d:detr(D[d]) for d in D}).mean(axis=1)
    # synthetic control: nonneg weights, normalised to sum 1, fit on pre
    A=D.loc[pre].values; b=y.loc[pre].values
    A2=np.vstack([A,1e3*np.ones(A.shape[1])]); b2=np.append(b,1e3)
    w,_=nnls(A2,b2); w=w/w.sum() if w.sum()>0 else w
    sc=y-(D.values@w if False else pd.Series(D.values@w,index=D.index))
    pre_rmse=float(np.sqrt(((sc.loc[pre])**2).mean()))
    return dict(did=did,did_tr=did_tr,sc=sc,w=dict(zip(D.columns,np.round(w,3))),pre_rmse=pre_rmse,donors=list(D.columns))
rows=[];res={}
for u,E in events.items():
    r=est(u,donors_for[u],E); res[u]=r
    for name in ['did','did_tr','sc']:
        for t,v in r[name].items():
            rows.append(dict(unit=u,event=E,method=name,k=int(t-E),effect_logit=v))
    print(u,E,'donors',r['donors'],'sc weights',r['w'],'pre_rmse',round(r['pre_rmse'],3))
ev=pd.DataFrame(rows); ev.to_csv(R+'night/event_effects.csv',index=False)
# in-space placebos: each donor pseudo-treated at the same calendar year against the other donors (excl. the true treated)
pl=[]
for u,E in events.items():
    for d in donors_for[u]:
        others=[x for x in donors_for[u] if x!=d]
        try: r=est(d,others,E)
        except Exception as e: continue
        for name in ['did','did_tr','sc']:
            for t,v in r[name].items(): pl.append(dict(treated=u,placebo=d,event=E,method=name,k=int(t-E),effect_logit=v,pre_rmse=r['pre_rmse']))
pl=pd.DataFrame(pl); pl.to_csv(R+'night/placebo_effects.csv',index=False)
# summary: mean effect over k=0..3 (post), rank vs placebos, plus ratio to pre RMSE
out=[]
for u,E in events.items():
    for m in ['did','did_tr','sc']:
        e=ev[(ev.unit==u)&(ev.method==m)&(ev.k.between(0,3))].effect_logit.mean()
        e1=ev[(ev.unit==u)&(ev.method==m)&(ev.k.between(1,3))].effect_logit.mean()
        p=pl[(pl.treated==u)&(pl.method==m)&(pl.k.between(0,3))].groupby('placebo').effect_logit.mean()
        out.append(dict(unit=u,event=E,method=m,mean_post_k0_3=e,mean_post_k1_3=e1,n_placebos=len(p),
            placebo_mean=p.mean(),placebo_abs_max=p.abs().max(),rank_abs_effect=(p.abs()>=abs(e)).sum()+1,
            pct_effect=np.expm1(e)*100))
out=pd.DataFrame(out); out.to_csv(R+'night/event_summary.csv',index=False); print(out.round(3).to_string())
# pooled: equal-weight average of three events by k
pool=ev[ev.method.isin(['did','did_tr'])].groupby(['method','k']).effect_logit.mean().unstack(0)
pool.to_csv(R+'night/pooled_by_k.csv'); print(pool.round(3))
json.dump({u:{'w':r['w'],'pre_rmse':r['pre_rmse']} for u,r in res.items()},open(R+'night/sc_weights.json','w'),indent=1)
