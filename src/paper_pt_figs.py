import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=pd.read_csv('output/paper_pt/robust_series.csv').set_index('y'); a=pd.read_csv('output/paper_pt/audit_annual_series.csv').set_index('y')
ser=pd.read_csv('output/paper_pt/audit_9892_serial_quantiles.csv').set_index('y')
lg=lambda p:np.log(p/(1-p))
# Fig 1: timeline + tariff
fig,ax=plt.subplots(figsize=(10,3.6)); ax.axis('off')
txt=("Policy timeline and tariff (APEL 'Normas de serviço', page read 2026-11-09; prices excl. VAT)\n"
"• until 31 Dec 2014: ISBN service co-funded by State and APEL; effectively free to users (Observador, 10 Sep 2015)\n"
"• 11 Dec 2014: APEL notice announcing charges (user-supplied; host unreachable here, NOT independently read)\n"
"• 1 Jan 2015: charging begins; applications via online form only (Normas page: 'formulário disponibilizado exclusivamente online')\n"
"• Tariff (current page): single author-edition ISBN €15 | 10-ISBN prefix €100 (professional) / €150 (non-professional)\n"
"     100-ISBN €500/€750 | 1,000-ISBN €3,000/€4,500 | initial registration of non-members €25 (listed under 'other tariffs')\n"
"• Author-edition prefixes 978-989-20 (to ~2019, serial space 0001-9999 exhausted) and 978-989-33 (first appears in BNP 2019); max 3 ISBNs per entity\n"
"• 989-20 'includes individuals OR organisations wishing to publish one title' (APEL 2014 report, fn.18)")
ax.text(0,1,txt,va='top',fontsize=8.5,family='monospace'); plt.savefig('output/paper_pt/fig1_timeline_tariff.png',dpi=150,bbox_inches='tight'); plt.close()
# Fig 4/5: event-time with pre-trend extrapolation
fig,ax=plt.subplots(1,2,figsize=(12,4))
for axx,(col,lab) in zip(ax,[('ap_cons','AP name-match (consistent)'),('author_ed','Author-edition prefixes 989-20+33')]):
    y=lg(d[col]/d.n); yrs=list(range(2005,2015)); b=np.polyfit(yrs,y.loc[yrs],1)
    axx.plot(y.index,(1/(1+np.exp(-y)))*100,'o-',label=lab)
    t=np.arange(2005,2019); axx.plot(t,(1/(1+np.exp(-np.polyval(b,t))))*100,'--',c='gray',label='2005-14 trend extrapolated')
    for B in (2010,2011,2012,2013):  # placebo extrapolations (pre windows start 2005)
        ys=list(range(2005,B)); bb=np.polyfit(ys,y.loc[ys],1); tt=np.arange(B,B+4); axx.plot(tt,(1/(1+np.exp(-np.polyval(bb,tt))))*100,c='#bbb',lw=1)
    axx.axvline(2014.5,ls=':',c='k'); axx.set_title(lab+' — % of catalogued print ISBNs'); axx.legend(fontsize=7); axx.set_xlabel('publication year')
plt.tight_layout(); plt.savefig('output/paper_pt/fig5_event_time_placebo.png',dpi=150); plt.close()
# serial plot
fig,ax=plt.subplots(figsize=(6,4)); s=ser.loc[2007:2019]
ax.plot(s.index,s.med,'o-',label='median serial'); ax.fill_between(s.index,s.q10,s.q90,alpha=.2,label='10-90th pct'); ax.axvline(2014.5,ls=':',c='k'); ax.set_ylabel('4-digit serial in 978-989-20-NNNN'); ax.set_xlabel('publication year'); ax.legend(); ax.set_title('Sequential allocation: ~900 serials/yr from 2013, no break at 2015')
plt.tight_layout(); plt.savefig('output/paper_pt/fig3_serial_allocation.png',dpi=150)
