import itertools, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('src/night_placebo.py').read().split("pool=['nz'")[0])
tr=[('es',2012,5,['nz','uk','fr']),('pt',2015,7,['nz','uk','fr']),('fr',2019,7,['nz','qc'])]
loo=[]
for u,E,pr,don in tr:
    for k in range(len(don),1,-1):
        for sub in itertools.combinations(don,k):
            r=eff(u,list(sub),E,pr); 
            if r: loo.append(dict(unit=u,donors='+'.join(sub),did=r[0],did_tr=r[1]))
L=pd.DataFrame(loo); L.to_csv('output/night/leave_one_donor_out.csv',index=False); print(L.round(3).to_string())
fig,ax=plt.subplots(1,3,figsize=(13,3.8),sharey=True)
for a_,(u,E,pr,don) in zip(ax,tr):
    yrs=list(range(E-pr,E+4)); y=lg(S[u].reindex(yrs)); y=y-y.loc[:E-1].mean()
    for d in don:
        z=lg(S[d].reindex(yrs)); a_.plot([t-E for t in yrs],z-z.loc[:E-1].mean(),color='#bbb',lw=1.2)
        a_.text(3.1,(z-z.loc[:E-1].mean()).iloc[-1],d,fontsize=7,color='#777')
    a_.plot([t-E for t in yrs],y,color='#c0392b',lw=2.4,marker='o'); a_.axvline(-0.5,ls='--',c='k',lw=.8)
    a_.set_title(f'{u.upper()} fee {E}',fontsize=10); a_.set_xlabel('years from first exposed year')
ax[0].set_ylabel('logit AP share, minus own pre-mean')
fig.suptitle('Author=publisher share around ISBN-fee introductions (red) vs controls (grey)',fontsize=10)
plt.tight_layout(); plt.savefig('output/night/event_study.png',dpi=150)
