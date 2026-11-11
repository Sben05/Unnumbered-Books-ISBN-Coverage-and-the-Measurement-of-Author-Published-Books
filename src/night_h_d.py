"""H-D: crude implied price elasticity from event-study estimates. ILLUSTRATIVE ONLY (3 events, secondary-sourced fees)."""
import pandas as pd, numpy as np, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); OUT='output/night_h'
pi=pd.read_csv('output/night_fixed/placebo_inference.csv'); pi=pi[pi.version=='fixed']
# effective cash price to a one-book self-publisher (EUR): ES 45; PT non-professional pack of 10 = 150 (a lone author cannot buy fewer; per-ISBN 15 if all used); FR dossier 25 (2019 launch, low-medium confidence) to 37 (current)
price={'es':(45,45,45),'pt':(15,150,150),'fr':(25,31,37)}  # low, central, high
rows=[]
for r in pi.itertuples():
    lo,c,hi=price[r.unit]
    for C in (300,1000,3000):   # illustrative all-in cost of producing a book for an author (EUR)
        for p in (lo,c,hi):
            dlnp=np.log((C+p)/C)
            for kind,eff,sd in (('point',r.effect_logit,0),('lo95',r.effect_logit-1.96*r.placebo_sd,0),('hi95',r.effect_logit+1.96*r.placebo_sd,0)):
                rows.append(dict(unit=r.unit,method=r.method,donors=r.donors,price=p,total_cost_C=C,kind=kind,effect_logit=eff,semi_per_100eur=eff/(p/100),elasticity=eff/dlnp))
R=pd.DataFrame(rows); R.to_csv(f'{OUT}/hd_elasticity_all.csv',index=False)
S=R[(R.method=='did')&(R.total_cost_C==1000)].pivot_table(index=['unit','price'],columns='kind',values=['semi_per_100eur','elasticity']).round(2)
print(S.to_string())
# three-point cross-event slope of effect on log(central price)
E=pi[pi.method=='did'].set_index('unit'); x=np.log([price[u][1] for u in E.index]); y=E.effect_logit.values
sl=np.polyfit(x,y,1); print('units',list(E.index),'effects',y.round(2),'slope per ln(price)',sl.round(2),'corr',np.corrcoef(x,y)[0,1].round(2))
rho=pd.Series(y).corr(pd.Series([price[u][1] for u in E.index]),method='spearman'); print('spearman',rho)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(5.5,4))
for u in E.index:
    e=E.loc[u]; p=price[u][1]; ax.errorbar(p,e.effect_logit,yerr=1.96*e.placebo_sd,fmt='o',capsize=3); ax.annotate(u.upper(),(p,e.effect_logit),xytext=(5,5),textcoords='offset points')
ax.axhline(0,c='k',lw=.6); ax.set_xscale('log'); ax.set_xlabel('assumed cash price to a lone author (EUR, log)'); ax.set_ylabel('DiD effect on logit AP share (fixed rules)'); ax.set_title('Dose-response, 3 points (illustrative)\nbars = +/-1.96 placebo SD')
plt.tight_layout(); plt.savefig(f'{OUT}/hd_dose.png',dpi=140)
