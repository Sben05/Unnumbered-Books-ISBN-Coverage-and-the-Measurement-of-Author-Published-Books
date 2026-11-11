"""Night-vis step 2: placebo-tested ISBN-visibility result. ITS (Newey-West), sup-F with block bootstrap, rank among placebo breaks 2008-2020,
placebo series (PT non-AP, ES AP, ES non-AP), PC1 bundle, ES 2012 analogue, total-AP decomposition. Outputs in output/night_vis/."""
import os,warnings; warnings.filterwarnings('ignore')
import numpy as np,pandas as pd,statsmodels.api as sm
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); OUT='output/night_vis'
rng=np.random.default_rng(20261109); YRS=np.arange(2005,2025); n=len(YRS); BOOT=2000; L=3; LAGS=2
C=pd.read_csv(f'{OUT}/vis_counts.csv')
def lg(k,N): p=(np.asarray(k,float)+.5)/(np.asarray(N,float)+1); return np.log(p/(1-p))
NAMES=['i_isbn_share','ii_small_block','iii_first_use','iv_multi_author']
LAB={'i_isbn_share':'(i) share of records with ISBN','ii_small_block':'(ii) share on <=10-number prefixes','iii_first_use':'(iii) share on prefixes first used that year','iv_multi_author':'(iv) share on multi-author prefixes'}
def build(c,g):
    d=C[(C.country==c)&(C.group==g)].set_index('year').loc[YRS]
    raw={'i_isbn_share':d.isbn_rec/(d.isbn_rec+d.noisbn_rec),'ii_small_block':d.small/d.n_books,'iii_first_use':d.firstuse/d.n_books,'iv_multi_author':d.multi/d.n_books}
    den={'i_isbn_share':d.isbn_rec+d.noisbn_rec}|{k:d.n_books for k in NAMES[1:]}
    num={'i_isbn_share':d.isbn_rec,'ii_small_block':d.small,'iii_first_use':d.firstuse,'iv_multi_author':d.multi}
    lgt={k:lg(num[k],den[k]) for k in NAMES}
    Z=np.column_stack([lgt[k] for k in NAMES]); Z=(Z-Z.mean(0))/Z.std(0)
    u,s,vt=np.linalg.svd(Z,full_matrices=False); v=vt[0]
    if v[0]<0: v=-v
    pc=Z@v; lgt['bundle_pc1']=pc/pc.std()
    ve=(s**2/np.sum(s**2))[0]
    return raw,lgt,v,ve,d
S={}; RAW={}; LOAD=[]
for c in ['pt','es']:
    for g in ['AP','nonAP']:
        raw,lgt,v,ve,d=build(c,g); S[(c,g)]=lgt; RAW[(c,g)]=raw
        LOAD.append(dict(series=f'{c.upper()} {g}',**{f'load_{k}':x for k,x in zip(NAMES,v)},var_explained=ve))
pd.DataFrame(LOAD).to_csv(f'{OUT}/vis_bundle_loadings.csv',index=False)
ALL=NAMES+['bundle_pc1']
def design(E,t=YRS):
    post=(t>=E).astype(float); return np.column_stack([np.ones(len(t)),t-E,post,post*(t-E)])
def its(y,E,t=YRS,mask=None):
    X=design(E,t)
    if mask is not None: X,y=X[mask],y[mask]
    r=sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':LAGS},use_t=True); ci=r.conf_int()[2]
    return dict(level=r.params[2],lo=ci[0],hi=ci[1],p=r.pvalues[2],slope_chg=r.params[3],slope_p=r.pvalues[3],pre_slope=r.params[1])
CAND=list(range(2008,2021))
def Fstat(y,E):
    X0=np.column_stack([np.ones(n),np.arange(n)]); X1=design(E)
    s0=np.sum((y-X0@np.linalg.lstsq(X0,y,rcond=None)[0])**2); s1=np.sum((y-X1@np.linalg.lstsq(X1,y,rcond=None)[0])**2)
    return ((s0-s1)/2)/(s1/(n-4))
def level(y,E):
    X=design(E); return np.linalg.lstsq(X,y,rcond=None)[0][2]
def breaktest(y,E):
    Fs={e:Fstat(y,e) for e in CAND}; sup=max(Fs.values()); best=max(Fs,key=Fs.get)
    rankF=1+sum(v>Fs[E] for v in Fs.values())
    lv={e:level(y,e) for e in CAND}; rank_lv=1+sum(v<lv[E] for v in lv.values()) if lv[E]<0 else 1+sum(v>lv[E] for v in lv.values())  # rank by |level| in own direction
    rank_abs=1+sum(abs(v)>abs(lv[E]) for v in lv.values())
    X0=np.column_stack([np.ones(n),np.arange(n)]); b=np.linalg.lstsq(X0,y,rcond=None)[0]; f=X0@b; e0=y-f; e0=e0-e0.mean()
    cs=0; ce=0; k=int(np.ceil(n/L))
    for _ in range(BOOT):
        st=rng.integers(0,n,k); eb=np.concatenate([e0[(s+np.arange(L))%n] for s in st])[:n]; yb=f+eb
        Fb={e:Fstat(yb,e) for e in CAND}; cs+=max(Fb.values())>=sup; ce+=Fb[E]>=Fs[E]
    return dict(best_break=best,supF=sup,F_event=Fs[E],rank_F_event=rankF,rank_abs_level=rank_abs,n_cand=len(CAND),p_supF_block=(cs+1)/(BOOT+1),p_Fevent_block=(ce+1)/(BOOT+1),Fs=Fs)
def run(c,g,E,outs=ALL):
    res=[]; Fall={}
    for o in outs:
        y=S[(c,g)][o]; a=its(y,E); b=breaktest(y,E); Fall[o]=b.pop('Fs')
        res.append(dict(series=f'{c.upper()} {g}',event=E,outcome=o,**a,**b))
    return res,Fall
rows=[]; FALL={}
for c,g,E in [('pt','AP',2015),('pt','nonAP',2015),('es','AP',2015),('es','nonAP',2015),('es','AP',2012),('es','nonAP',2012),('pt','AP',2012)]:
    r,F=run(c,g,E); rows+=r; FALL[(c,g,E)]=F
R=pd.DataFrame(rows)
# gaps (differences of logit series): PT AP - PT nonAP ; PT AP - ES AP
for lab,(a,b) in {'GAP PT AP - PT nonAP':(('pt','AP'),('pt','nonAP')),'GAP PT AP - ES AP':(('pt','AP'),('es','AP'))}.items():
    for o in ALL:
        y=S[a][o]-S[b][o]; it=its(y,2015); bt=breaktest(y,2015); bt.pop('Fs'); R=pd.concat([R,pd.DataFrame([dict(series=lab,event=2015,outcome=o,**it,**bt)])],ignore_index=True)
# Holm
def holm(p):
    p=np.asarray(p,float); o=np.argsort(p); m=len(p); adj=np.empty(m); run_=0
    for i,idx in enumerate(o): run_=max(run_,(m-i)*p[idx]); adj[idx]=min(1,run_)
    return adj
R['holm_family']=''; R['p_its_holm']=np.nan; R['p_supF_holm']=np.nan
m=(R.series=='PT AP')&(R.event==2015); R.loc[m,'p_its_holm']=holm(R.loc[m,'p']); R.loc[m,'p_supF_holm']=holm(R.loc[m,'p_supF_block']); R.loc[m,'holm_family']='PT AP 2015: 4 outcomes + bundle'
m=(R.event==2015)&(~R.series.str.startswith('GAP')); R['p_its_holm_global']=np.nan; R.loc[m,'p_its_holm_global']=holm(R.loc[m,'p']); 
m=(R.series=='ES AP')&(R.event==2012); R.loc[m,'p_its_holm']=holm(R.loc[m,'p']); R.loc[m,'p_supF_holm']=holm(R.loc[m,'p_supF_block']); R.loc[m,'holm_family']='ES AP 2012: 4 outcomes + bundle'
R.to_csv(f'{OUT}/vis_results.csv',index=False)
# PT AP with the +-sign for 'expected fee direction': i,ii,iii down; iv up
# ---- total AP decomposition (PT)
d=C[(C.country=='pt')&(C.group=='AP')].set_index('year').loc[YRS]
T=pd.DataFrame({'with_isbn':d.isbn_rec,'without_isbn':d.noisbn_rec}); T['total']=T.with_isbn+T.without_isbn
allrec=C[(C.country=='pt')].groupby('year')[['isbn_rec','noisbn_rec']].sum().loc[YRS]; T['all_print_records']=allrec.sum(1)
T.to_csv(f'{OUT}/vis_total_ap.csv')
def lin_its(y,E=2015,mask=None,lags=LAGS):
    X=design(E); yy=np.asarray(y,float)
    if mask is not None: X,yy=X[mask],yy[mask]
    return sm.OLS(yy,X).fit(cov_type='HAC',cov_kwds={'maxlags':lags},use_t=True)
def eff(r,horizon):  # mean effect over k=0..horizon-1: level + slope_chg * mean(k)
    w=np.array([0,0,1,np.mean(np.arange(horizon))]); e=w@r.params; se=np.sqrt(w@r.cov_params()@w); return e,e-2.1*se,e+2.1*se
dec=[]
for lab,mask in [('2005-2024',None),('2005-2024 excl. 2014',YRS!=2014),('2009-2024',YRS>=2009)]:
    for h in (1,3,5):
        row=dict(window=lab,horizon_years=h)
        for k in ['with_isbn','without_isbn','total']:
            e,lo,hi=eff(lin_its(T[k].values,mask=mask),h); row[k]=e; row[k+'_lo']=lo; row[k+'_hi']=hi
        row['share_of_isbn_loss_offset_by_noISBN']=-row['without_isbn']/row['with_isbn'] if row['with_isbn']!=0 else np.nan
        dec.append(row)
# joint bootstrap for offset ratio (horizon 3) and total log ITS
X=design(2015); fits={k:np.linalg.lstsq(X,T[k].values.astype(float),rcond=None) [0] for k in ['with_isbn','without_isbn']}
res={k:T[k].values-X@fits[k] for k in fits}; k_=int(np.ceil(n/L)); bs=[]
for _ in range(BOOT):
    st=rng.integers(0,n,k_); idx=np.concatenate([(s+np.arange(L))%n for s in st])[:n]; out={}
    for k in fits:
        yb=X@fits[k]+res[k][idx]; b=np.linalg.lstsq(X,yb,rcond=None)[0]; out[k]=b[2]+b[3]*1.0
    bs.append((out['with_isbn'],out['without_isbn']))
bs=np.array(bs); ratio=-bs[:,1]/bs[:,0]; ok=bs[:,0]<0
dec_df=pd.DataFrame(dec)
lt=lin_its(np.log(T.total.values.astype(float))); ci=lt.conf_int()[2]
lw=lin_its(np.log(T.with_isbn.values.astype(float))); ciw=lw.conf_int()[2]
ln=lin_its(np.log(T.without_isbn.values.astype(float))); cin=ln.conf_int()[2]
ls_=lin_its(lg(T.total,T.all_print_records)); cis=ls_.conf_int()[2]
LOGI=dict(total_level=lt.params[2],total_lo=ci[0],total_hi=ci[1],total_p=lt.pvalues[2],with_level=lw.params[2],with_lo=ciw[0],with_hi=ciw[1],with_p=lw.pvalues[2],without_level=ln.params[2],without_lo=cin[0],without_hi=cin[1],without_p=ln.pvalues[2],totshare_level=ls_.params[2],totshare_lo=cis[0],totshare_hi=cis[1],totshare_p=ls_.pvalues[2],
  offset_ratio_h3_boot_lo=np.percentile(ratio[ok],2.5),offset_ratio_h3_boot_hi=np.percentile(ratio[ok],97.5),offset_ratio_boot_share_isbn_loss_negative=ok.mean())
dec_df.to_csv(f'{OUT}/vis_total_decomp.csv',index=False); pd.Series(LOGI).to_csv(f'{OUT}/vis_total_log_its.csv')
bt=breaktest(np.log(T.total.values.astype(float)),2015); bt.pop('Fs'); pd.Series(bt).to_csv(f'{OUT}/vis_total_break.csv')
print(R[['series','event','outcome','level','lo','hi','p','p_its_holm','best_break','F_event','rank_F_event','p_supF_block','p_supF_holm']].round(3).to_string())
print(dec_df.round(1).to_string()); print(pd.Series(LOGI).round(3)); print(bt)
# ---- figures
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,3,figsize=(14,7)); cols={'PT AP':'#1f5fa8','PT nonAP':'#888888','ES AP':'#d98a1f'}
for ax,o in zip(axs.flat,ALL):
    for (c,g),lab in [(('pt','AP'),'PT AP'),(('pt','nonAP'),'PT nonAP'),(('es','AP'),'ES AP')]:
        y=S[(c,g)][o] if o=='bundle_pc1' else RAW[(c,g)][o]
        ax.plot(YRS,y,'o-' if lab=='PT AP' else '.--',c=cols[lab],lw=2 if lab=='PT AP' else 1,ms=4,label=lab)
    ax.axvline(2014.5,c='k',ls=':'); ax.axvline(2011.5,c='#d98a1f',ls=':'); ax.set_title(LAB.get(o,'Bundle: PC1 of standardised logits (z)'),fontsize=9)
axs[0,0].legend(fontsize=7); axs.flat[-1].axis('off')
ax=axs[1,2]; ax.axis('on'); 
for o in ALL: ax.plot(CAND,[FALL[('pt','AP',2015)][o][e] for e in CAND],'o-',ms=3,label=o)
ax.axvline(2015,c='k',ls=':'); ax.set_title('PT AP: break F-stat by candidate year'); ax.legend(fontsize=6)
plt.tight_layout(); plt.savefig(f'{OUT}/vis_series.png',dpi=140); plt.close()
fig,ax=plt.subplots(1,2,figsize=(12,4))
ax[0].plot(YRS,T.with_isbn,'o-',label='AP with ISBN'); ax[0].plot(YRS,T.without_isbn,'s-',label='AP without ISBN'); ax[0].plot(YRS,T.total,'^-',c='k',label='total AP')
b=lin_its(T.total.values.astype(float)); Xp=design(2015); pre=YRS<2015
for k,c_ in [('with_isbn','C0'),('without_isbn','C1'),('total','k')]:
    bb=np.linalg.lstsq(Xp[pre][:,:2],T[k].values[pre].astype(float),rcond=None)[0]; ax[0].plot(YRS[YRS>=2014],(Xp[:,:2]@bb)[YRS>=2014],':',c=c_)
ax[0].axvline(2014.5,c='grey',ls=':'); ax[0].set_title('PT AP records; dotted = 2005-14 linear trend'); ax[0].legend(fontsize=7)
h=dec_df[dec_df.window=='2005-2024']
for k,c_ in [('with_isbn','C0'),('without_isbn','C1'),('total','k')]:
    ax[1].errorbar(h.horizon_years+(0.08*['with_isbn','without_isbn','total'].index(k)),h[k],yerr=[h[k]-h[k+'_lo'],h[k+'_hi']-h[k]],fmt='o',c=c_,label=k,capsize=3)
ax[1].axhline(0,c='grey'); ax[1].set_xticks([1,3,5]); ax[1].set_xlabel('horizon (years after 2015)'); ax[1].set_title('ITS mean effect vs trend, records/yr (95% CI)'); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig(f'{OUT}/vis_total_ap.png',dpi=140)
