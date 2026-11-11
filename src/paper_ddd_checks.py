"""(3) Heterogeneity by book type in Portugal; (5) negative controls and pooled time placebos; (4) dose-response vs price."""
import numpy as np, pandas as pd, re, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, statsmodels.formula.api as smf
lg=lambda p:np.log(np.clip(p,1e-3,1-1e-3)/(1-np.clip(p,1e-3,1-1e-3)))
# ---------- (3) heterogeneity (PT national bibliography, 2010-19)
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt&R.pub_year.between(2010,2019)].copy()
raw=pd.read_parquet('data/interim/pt_raw.parquet',columns=['id','udc','extent']); raw['id']=raw.id.astype(str); R=R.merge(raw[['id','udc']],on='id',how='left')
R['pages']=pd.to_numeric(R.extent.astype(str).str.extract(r'(\d{1,4})')[0],errors='coerce'); u=R.udc.fillna('')
R['short']=(R.pages<64)
R['poetry']=u.str.startswith('821')&u.str.contains(r'-1(?!\d)')
R['literature']=u.str.startswith('82')
R['history_local']=u.str.startswith(('94','908','929'))
R['religion_phil']=u.str.startswith(('1','2'))
R['applied']=u.str.startswith(('6','37'))
R['noisbn']=(~R.has_isbn).astype(int); R['post']=(R.pub_year>=2015).astype(int); R['apx']=R.ap.astype(int)
def ddd(df):
    c=df.groupby(['apx','post']).noisbn.agg(['mean','size']); 
    try:
        d=(lg(c.loc[(1,1),'mean'])-lg(c.loc[(1,0),'mean']))-(lg(c.loc[(0,1),'mean'])-lg(c.loc[(0,0),'mean']))
    except KeyError: return np.nan,np.nan,np.nan,0
    rng=np.random.default_rng(2); bs=[]
    for _ in range(1500):
        m={k:rng.binomial(int(c.loc[k,'size']),c.loc[k,'mean'])/c.loc[k,'size'] for k in c.index}
        bs.append((lg(m[(1,1)])-lg(m[(1,0)]))-(lg(m[(0,1)])-lg(m[(0,0)])))
    return d,np.percentile(bs,2.5),np.percentile(bs,97.5),int(c.loc[[(1,0),(1,1)],'size'].sum())
rows=[]
for lab,mask in [('all books',R.noisbn>=0),('short (<64 pages)',R.short),('not short (>=64 pages)',~R.short),('poetry',R.poetry),('literature (other than poetry)',R.literature&~R.poetry),
                 ('history / biography / local (UDC 94, 908, 929)',R.history_local),('religion / philosophy (UDC 1, 2)',R.religion_phil),('applied / technical / education (UDC 6, 37)',R.applied)]:
    d,lo,hi,nap=ddd(R[mask]); rows.append(dict(group=lab,self_pub_books=nap,ddd_logit=d,ci_low=lo,ci_high=hi))
H=pd.DataFrame(rows); H.to_csv('output/paper_pt/ddd_pt_heterogeneity.csv',index=False); print(H.round(2).to_string(index=False))
m=smf.ols('noisbn ~ apx*post*short + C(pub_year)',data=R.dropna(subset=['pages'])).fit(cov_type='HC1'); k='apx:post:short[T.True]' if 'apx:post:short[T.True]' in m.params else [x for x in m.params.index if 'apx:post:short' in x][0]
print('triple interaction apx:post:short (LPM):',round(m.params[k],4),'se',round(m.bse[k],4))
# ---------- (5) negative controls
P=pd.read_csv('output/paper_pt/ddd_panel.csv')
P['non_sh']=P.nonap_noisbn/(P.nonap_isbn+P.nonap_noisbn); P['ap_sh']=P.ap_noisbn/(P.ap_isbn+P.ap_noisbn)
def chg(c,col,E,npre=4,npost=4):
    d=P[P.country==c].set_index('y')[col]; return lg(d.loc[E:E+npost-1].mean())-lg(d.loc[E-npre:E-1].mean())
neg=[]
for t,E,ctrl in [('PT',2015,['PL','EE','NZ']),('ES',2012,['PL','EE','NZ','UK'])]:
    neg.append(dict(event=f'{t} {E}',outcome='NEGATIVE CONTROL: other books no-ISBN share',treated_change=chg(t,'non_sh',E),control_mean_change=np.mean([chg(c,'non_sh',E) for c in ctrl])))
    neg.append(dict(event=f'{t} {E}',outcome='MAIN: self-published no-ISBN share',treated_change=chg(t,'ap_sh',E),control_mean_change=np.mean([chg(c,'ap_sh',E) for c in ctrl])))
N=pd.DataFrame(neg); N['difference']=N.treated_change-N.control_mean_change; print(N.round(3).to_string(index=False)); N.to_csv('output/paper_pt/ddd_negative_controls.csv',index=False)
# pooled time placebos: each control as 'treated' at fake years 2012-2015 vs remaining controls (excluding PT, ES, FR)
def gapc(c): 
    d=P[P.country==c].set_index('y'); return lg(d.ap_sh)-lg(d.non_sh)
pl=[]
for c in ['PL','EE','NZ']:
    for E in [2012,2013,2014,2015]:
        others=[k for k in ['PL','EE','NZ'] if k!=c]
        def ch(k): g=gapc(k); return g.loc[E:E+3].mean()-g.loc[E-4:E-1].mean()
        pl.append(dict(country=c,fake_year=E,effect=ch(c)-np.mean([ch(k) for k in others])))
PL=pd.DataFrame(pl); PL.to_csv('output/paper_pt/ddd_pooled_placebos.csv',index=False)
print('pooled placebo |effect|: median %.2f, 90th pct %.2f, max %.2f (n=%d); PT effect 0.58, ES 0.45'%(PL.effect.abs().median(),PL.effect.abs().quantile(.9),PL.effect.abs().max(),len(PL)))
print('share of placebos with |effect| >= 0.58: %.2f ; >= 0.45: %.2f'%((PL.effect.abs()>=0.58).mean(),(PL.effect.abs()>=0.45).mean()))
# ---------- (4) dose-response
E=pd.read_csv('output/paper_pt/ddd_events_summary.csv'); price={'ES 2012':45,'PT 2015':15,'FR 2019':31}
E['price_eur']=E.event.map(price); print(E[['event','price_eur','effect_logit','ci_low','ci_high']].round(2).to_string(index=False))
fig,ax=plt.subplots(figsize=(5.5,4)); ax.errorbar(E.price_eur,E.effect_logit,yerr=[E.effect_logit-E.ci_low,E.ci_high-E.effect_logit],fmt='o',c='#c0392b',capsize=4)
for _,r in E.iterrows(): ax.annotate(r.event,(r.price_eur,r.effect_logit),xytext=(5,5),textcoords='offset points')
ax.axhline(0,c='#999',lw=.8); ax.set_xlabel('single-ISBN price (EUR; FR = midpoint of 25-37, unverified)'); ax.set_ylabel('triple-difference effect (logit)'); ax.set_title('Dose-response? (3 points)')
plt.tight_layout(); plt.savefig('output/paper_pt/fig_ddd_dose.png',dpi=150)
