"""Triple-difference across fee events. Unit = country-year gap g = logit(AP no-ISBN share) - logit(other-books no-ISBN share).
Effect(E) = [mean gap over E..E+3 - mean gap over E-4..E-1] for the treated country minus the same change averaged over control countries.
Events: ES 2012 (charge from Dec 2011), PT 2015, FR 2019 (post = 2019-2021 only). Controls never charging in window: PL, EE, NZ (free); LV excluded (data from 2014); UK only for ES (paid throughout, coverage ends 2018).
Inference: binomial parametric bootstrap (sampling noise) + placebo-treated controls (rank among placebo effects). No causal claim."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
P=pd.read_csv('output/paper_pt/ddd_panel.csv').set_index(['country','y']).sort_index()
lg=lambda p:np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4)))
def gap(df):
    pa=df.ap_noisbn/(df.ap_isbn+df.ap_noisbn); pn=df.nonap_noisbn/(df.nonap_isbn+df.nonap_noisbn); return lg(pa)-lg(pn)
events={'ES':(2012,4,4),'PT':(2015,4,4),'FR':(2019,4,3)}
controls={'ES':['PL','EE','NZ','UK'],'PT':['PL','EE','NZ'],'FR':['PL','EE','NZ']}
rng=np.random.default_rng(7)
def change(df,E,npre,npost):
    g=gap(df); return g.loc[E:E+npost-1].mean()-g.loc[E-npre:E-1].mean()
def unit(c,E,npre,npost,boot=False):
    d=P.loc[c].loc[E-npre:E+npost-1].copy()
    if boot:
        n1=(d.ap_isbn+d.ap_noisbn); n2=(d.nonap_isbn+d.nonap_noisbn)
        d['ap_noisbn']=rng.binomial(n1.astype(int),d.ap_noisbn/n1); d['ap_isbn']=n1-d.ap_noisbn
        d['nonap_noisbn']=rng.binomial(n2.astype(int),d.nonap_noisbn/n2); d['nonap_isbn']=n2-d.nonap_noisbn
    return change(d,E,npre,npost)
rows=[]; paths={}
for t,(E,npre,npost) in events.items():
    ctrl=controls[t]
    est=unit(t,E,npre,npost)-np.mean([unit(c,E,npre,npost) for c in ctrl])
    bs=[unit(t,E,npre,npost,True)-np.mean([unit(c,E,npre,npost,True) for c in ctrl]) for _ in range(2000)]
    # placebo: each control treated, compared with the other controls (same window); treated country not used
    pl=[unit(c,E,npre,npost)-np.mean([unit(k,E,npre,npost) for k in ctrl if k!=c]) for c in ctrl]
    loo={c:unit(t,E,npre,npost)-np.mean([unit(k,E,npre,npost) for k in ctrl if k!=c]) for c in ctrl}
    rows.append(dict(event=f'{t} {E}',effect_logit=est,ci_low=np.percentile(bs,2.5),ci_high=np.percentile(bs,97.5),
        odds_ratio=np.exp(est),placebo_effects=' '.join(f'{c}:{v:+.2f}' for c,v in zip(ctrl,pl)),rank_abs=1+sum(abs(v)>=abs(est) for v in pl),n_placebo=len(pl),
        loo_min=min(loo.values()),loo_max=max(loo.values()),controls='+'.join(ctrl)))
    g_t=gap(P.loc[t]); g_c=pd.concat([gap(P.loc[c]) for c in ctrl],axis=1).mean(axis=1)
    base_t=g_t.loc[E-npre:E-1].mean(); base_c=g_c.loc[E-npre:E-1].mean()
    paths[t]=pd.DataFrame({'treated':g_t-base_t,'controls':g_c-base_c}).loc[E-npre-2:E+npost+1]
R=pd.DataFrame(rows); R.to_csv('output/paper_pt/ddd_events_summary.csv',index=False); pd.set_option('display.width',250); print(R.round(3).to_string(index=False))
fig,ax=plt.subplots(1,3,figsize=(14,3.8),sharey=True)
for a,(t,(E,_,_)) in zip(ax,events.items()):
    d=paths[t]; k=d.index-E; a.plot(k,d.treated,'o-',c='#c0392b',label=f'{t} (treated)'); a.plot(k,d.controls,'s--',c='#555',label='controls (PL, EE, NZ'+(', UK' if t=='ES' else '')+')')
    a.axvline(-0.5,c='k',ls=':'); a.axhline(0,c='#ccc',lw=.8); a.set_title(f'{t}: fee in {E}'); a.set_xlabel('years from first exposed year'); a.legend(fontsize=7)
ax[0].set_ylabel('gap (AP vs other books, no-ISBN logit)\nrelative to own pre-period mean')
plt.tight_layout(); plt.savefig('output/paper_pt/fig_ddd_event_studies.png',dpi=150)
# fake event years for PT (placebo timing) with same controls, windows must fit data
fk=[]
for E in range(2011,2018):
    if E-4<2008 or E+4>2019: continue
    est=unit('PT',E,4,4)-np.mean([unit(c,E,4,4) for c in controls['PT']]); fk.append((E,est))
F=pd.DataFrame(fk,columns=['fake_event_year','effect_logit']); F.to_csv('output/paper_pt/ddd_pt_fake_dates.csv',index=False); print(F.round(3).to_string(index=False))
