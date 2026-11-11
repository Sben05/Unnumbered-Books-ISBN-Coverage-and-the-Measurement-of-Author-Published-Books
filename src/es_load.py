"""Spain BNE monograph CSVs (CP1252) -> one Parquet of raw string columns."""
import sys,glob,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import pandas as pd
files=sorted(glob.glob(str(ROOT/'data/interim/_es_extract/*.csv')),key=lambda p:int(re.search(r'_(\d+)-CP',p).group(1)))
dfs=[]
for f in files:
 d=pd.read_csv(f,sep=';',encoding='cp1252',dtype=str,keep_default_na=False,quotechar='"',on_bad_lines='warn');d['_file']=Path(f).name;dfs.append(d)
cols={tuple(d.columns[:-1]) for d in dfs};print('distinct headers',len(cols))
df=pd.concat(dfs,ignore_index=True);print(df.shape)
df.to_parquet(ROOT/'data/interim/es_raw.parquet',compression='zstd')
