"""Stockpiling test: author-edition ISBNs (978-989-20-NNNN) are numbered sequentially at assignment; DL numbers are assigned at printing.
For each DL year Y, frontier F(Y) = 90th percentile of 989-20 serials on books printed in DL-year Y. Share of books printed in DL-year Y+1
whose serial <= F(Y) ('old' ISBNs, assigned before Y+1). A jump for Y+1=2015 = ISBNs obtained free in 2014 and used after the fee."""
import pandas as pd, numpy as np
bn=pd.read_parquet('data/interim/bnp_csv_bibliografianacional.parquet',columns=['id','dl'])
R=pd.read_parquet('data/interim/pt_natbib_records.parquet'); R=R[R.print_like&R.pt]
d=R.merge(bn,on='id',how='left'); m=d.dl.str.extract(r'^\s*(\d{5,7})\s*/\s*(\d{2})\b')
d['dln']=pd.to_numeric(m[0],errors='coerce'); d['dly']=pd.to_numeric(m[1],errors='coerce')+2000
q=d.groupby('dly').dln.quantile([.01,.99]).unstack(); d=d.join(q,on='dly'); d=d[(d.dln>=d[0.01])&(d.dln<=d[0.99])]
a=d[d.isbn_first.str.startswith('97898920')].copy(); a['serial']=a.isbn_first.str[8:12].astype(int)
rows=[]
for Y in range(2009,2020):
    cur=a[a.dly==Y]; nxt=a[a.dly==Y+1]
    if len(cur)<30 or len(nxt)<30: continue
    F=cur.serial.quantile(.9); Fmed=cur.serial.median()
    rows.append(dict(next_DL_year=Y+1,books_next=len(nxt),frontier_p90_prev=F,share_old_serial=(nxt.serial<=F).mean(),
                     median_serial=nxt.serial.median(),serial_advance=nxt.serial.median()-Fmed,ap_share_next=nxt.ap.mean()))
S=pd.DataFrame(rows); print(S.round(3).to_string(index=False)); S.to_csv('output/paper_pt/stockpile_test.csv',index=False)
