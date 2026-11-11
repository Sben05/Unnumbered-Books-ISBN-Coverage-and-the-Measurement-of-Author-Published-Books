"""Record-only hand validation (read by the analyst from title/author/publisher strings; no web lookups). Labels are hard-coded below by sample row index
(row order = sha1 order within stratum, as in validation_<cc>.csv). flagged: 1=looks like genuine self-publication, 0=false positive, '?'=cannot tell.
unflagged: 1=looks self-published but missed, 0=not self-published on the record, '?'=cannot tell."""
import sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
from nordic_common import wilson
LAB={
 'no':dict(flag_fp=[15,19,40,49,27],flag_unc=[5,31],un_miss=[13,29],un_unc=[9,21,54,35]),
}
def apply(cc,name,notes):
 L=LAB[cc];p=ROOT/f'output/{name}/validation_{cc}.csv';v=pd.read_csv(p,dtype={'gold_label':object})
 f=v.index[v.stratum=='flagged'];u=v.index[v.stratum=='unflagged']
 for i,ix in enumerate(f):v.loc[ix,'gold_label']='0' if i in L['flag_fp'] else '?' if i in L['flag_unc'] else '1'
 for i,ix in enumerate(u):v.loc[ix,'gold_label']='1' if i in L['un_miss'] else '?' if i in L['un_unc'] else '0'
 v.to_csv(p,index=False)
 nf=len(f);fp=len(L['flag_fp']);unc=len(L['flag_unc']);tp_lo=nf-fp-unc;tp_hi=nf-fp
 lo=wilson(tp_lo,nf);hi=wilson(tp_hi,nf);nu=len(u);m=len(L['un_miss']);mu=len(L['un_unc'])
 txt=f"""# Record-only validation read: {cc.upper()} ({nf} flagged + {nu} unflagged)
Sample: first {nf} flagged and first {nu} unflagged rows ordered by SHA-1 of `{cc}-validation-v1|<isbn13>` (validation_{cc}.csv). Judged by me from the catalogue record only (title, authors, publisher string, matched rule); no web lookups. Labels in `gold_label` (1/0/?). These are single-reader impressions, not an independent gold standard.

**Flagged precision.** {nf-fp-unc} look like genuine self-publication, {fp} look like false positives (flagged row indices {L['flag_fp']}), {unc} cannot be told (rows {L['flag_unc']}). Precision {tp_lo}/{nf} = {tp_lo/nf:.0%} (strict, uncertain counted as wrong) to {tp_hi}/{nf} = {tp_hi/nf:.0%} (uncertain counted as right); 95% Wilson interval across both: {lo[0]:.0%} to {hi[1]:.0%}.
**Unflagged misses.** {m} of {nu} unflagged look self-published on the record (rows {L['un_miss']}), {mu} uncertain (rows {L['un_unc']}). Implied miss share among unflagged {m/nu:.0%} to {(m+mu)/nu:.0%} (very imprecise, n={nu}); this is not a recall estimate for the whole universe.
{notes}
"""
 (ROOT/f'output/{name}/validation_read.md').write_text(txt);print(txt)
if __name__=='__main__':
 cc=sys.argv[1];name={'no':'norway','se':'sweden'}[cc]
 notes={'no':"""
Patterns seen. True positives: Kolofon (self-publishing service) titles; author name = publisher name (full or initials). False positives: foundations/institutes listed with an author-like co-publisher string (Stiftelsen Psykiatrisk opplysning, Bergensklinikkene, Vox), and a society named after a long-dead author (Gabriel Scott selskabet). Initial-only matches ('A. Selnes') are plausible but unprovable. Misses: family-name imprints ('Dijkmanske forl.', 'Steens forlag' with a co-author Steen) and tiny unknown imprints; the classifier does not look for these. Many unflagged records are institutional/research reports (NIVA, NTNU doctoral theses, ministries), which is why the denominator is not 'trade books' only."""}[cc]
 apply(cc,name,notes)
