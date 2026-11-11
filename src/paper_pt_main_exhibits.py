"""Main exhibits for the paper: Fig 1 four sources (index 2013=100), Table 2 robustness of the AP no-ISBN shift, Fig 4 reconciliation."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
lg=lambda p:np.log(p/(1-p))
yrs=list(range(2010,2020))
cerlalc_ae={2013:718,2014:988,2015:617,2016:606,2017:884,2018:957,2019:778}            # CERLALC 2020 Tabla 4.3
isbn_tot={2010:17329,2011:16714,2012:17131,2013:19060,2014:25000,2015:18715,2016:18367,2017:19155,2018:18627,2019:18916}  # APEL 2014 report (2010-13), CERLALC T4.1 (2014-16), APEL transparency (2017-19)
dl_mono={2010:16818,2011:16471,2012:14756,2013:15284,2014:16841,2015:16530,2016:16138,2017:15724,2018:14309,2019:15008}  # Pordata/BNP
nb=pd.read_csv('output/paper_pt/natbib_isbn_by_ap_year.csv').set_index('pub_year'); nb.index=nb.index.astype(int)
T=pd.DataFrame({'agency ISBNs to author-publishers (CERLALC)':pd.Series(cerlalc_ae),'agency ISBNs, all (APEL/CERLALC)':pd.Series(isbn_tot),
  'legal-deposit monograph registrations (BNP/Pordata)':pd.Series(dl_mono),'self-published books in national bibliography':nb.ap.loc[yrs],
  '… with ISBN':nb.ap_isbn.loc[yrs],'… without ISBN':nb.ap_noisbn.loc[yrs],'other books in national bibliography':(nb.books-nb.ap).loc[yrs]}).loc[yrs]
T.to_csv('output/paper_pt/table1_four_sources.csv'); print(T.to_string())
I=100*T/T.loc[2013]
fig,ax=plt.subplots(figsize=(9,4.8))
sty={'agency ISBNs to author-publishers (CERLALC)':('#c0392b','-','o'),'agency ISBNs, all (APEL/CERLALC)':('#e67e22','--','s'),
     'legal-deposit monograph registrations (BNP/Pordata)':('#555','-','^'),'self-published books in national bibliography':('#2c7fb8','-','D'),
     '… with ISBN':('#2c7fb8',':','.'),'… without ISBN':('#8e44ad','-.','x')}
for k,(c,ls,mk) in sty.items(): ax.plot(I.index,I[k],ls=ls,c=c,marker=mk,label=k)
ax.axvline(2014.5,c='k',ls=':'); ax.axhline(100,c='#ccc',lw=.8); ax.set_ylabel('index, 2013 = 100'); ax.legend(fontsize=7.5,loc='upper left'); ax.set_title('Portugal: four sources around the 1 Jan 2015 ISBN charge')
plt.tight_layout(); plt.savefig('output/paper_pt/fig1_four_sources.png',dpi=150); plt.close()
# Table 2: robustness of the AP no-ISBN shift (2010-14 vs 2015-19), self-published vs other books
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt]
bn=pd.read_parquet('data/interim/bnp_csv_bibliografianacional.parquet',columns=['id','dl']); R=R.merge(bn,on='id',how='left')
m=R.dl.str.extract(r'^\s*(\d{5,7})\s*/\s*(\d{2})\b'); R['dl_year']=pd.to_numeric(m[1],errors='coerce')+2000
def did(df,flag,yearcol='pub_year'):
    df=df[df[yearcol].between(2010,2019)]; pre=df[yearcol]<=2014; f=df[flag]; no=~df.has_isbn
    a0,a1=no[f&pre].mean(),no[f&~pre].mean(); b0,b1=no[~f&pre].mean(),no[~f&~pre].mean()
    return dict(sp_pre=a0,sp_post=a1,other_pre=b0,other_post=b1,diff_pp=100*((a1-a0)-(b1-b0)),logit_diff=(lg(a1)-lg(a0))-(lg(b1)-lg(b0)),n_sp=int(f.sum()))
rows={'main: AP (consistent rule), publication year':did(R,'ap'),
      'AP original rule':did(R,'ap_orig'),
      'exclude records with unidentified publisher (s.n.)':did(R[~R.nopub],'ap'),
      'exclude government publications':did(R[~R.gov],'ap'),
      'printing year from legal-deposit number':did(R,'ap','dl_year'),
      'exclude 2014 (spike year)':did(R[R.pub_year!=2014],'ap')}
# pre-trend version: AP no-ISBN share vs linear 2005-14 trend
s=R[R.pub_year.between(2005,2019)].groupby(['pub_year','ap']).has_isbn.apply(lambda x:(~x).mean()).unstack()
g=lg(s[True])-lg(s[False]); pre=g.loc[2005:2014]; b=np.polyfit(pre.index,pre.values,1); dev=(g.loc[2015:2019]-np.polyval(b,g.loc[2015:2019].index)).mean()
T2=pd.DataFrame(rows).T; T2.loc['gap vs linear 2005-14 trend (logit, mean 2015-19)']=[np.nan]*6+[np.nan]; T2.loc['gap vs linear 2005-14 trend (logit, mean 2015-19)','logit_diff']=dev
T2.to_csv('output/paper_pt/table2_robustness.csv'); print(T2.round(3).to_string())
# Fig 4 reconciliation
st=pd.read_csv('output/paper_pt/stockpile_test.csv').set_index('next_DL_year')
imp=(st.serial_advance*st.ap_share_next).loc[2014:2019]
fig,ax=plt.subplots(figsize=(8,4.2))
ax.plot(st.loc[2010:2019].index,st.loc[2010:2019].serial_advance,'o-',c='#555',label='author-edition (989-20) serials advanced per year (all applicants)')
ax.plot(imp.index,imp,'s-',c='#2c7fb8',label='× share of those books whose publisher is the author (individuals)')
ax.plot(list(cerlalc_ae),list(cerlalc_ae.values()),'D--',c='#c0392b',label='CERLALC: ISBNs to author-publishers')
ax.axvline(2014.5,c='k',ls=':'); ax.set_xlabel('year (printing year for serial-based series)'); ax.legend(fontsize=7.5); ax.set_title('Reconciling agency and library counts')
plt.tight_layout(); plt.savefig('output/paper_pt/fig4_reconciliation.png',dpi=150)
print(pd.DataFrame({'serial_advance':st.serial_advance,'ap_share':st.ap_share_next,'implied_individuals':st.serial_advance*st.ap_share_next,'cerlalc':pd.Series(cerlalc_ae)}).loc[2013:2019].round(1))
