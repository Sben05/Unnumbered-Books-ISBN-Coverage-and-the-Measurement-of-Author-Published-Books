"""Apply record-only read labels to a validation CSV and write validation_read.md. usage: extra_validation.py <cc> <outdir> <labels.json>
labels.json: {"uncertain_flagged":[idx..],"wrong_flagged":[idx..],"missed_likely":[idx..],"unflagged_uncertain":[idx..],"notes":"..."}  (idx = row number in the CSV, 0-based)"""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import pandas as pd
cc,outd,lab=sys.argv[1:4];P=ROOT/'output'/outd/f'validation_{cc}.csv';L=json.load(open(lab));S=pd.read_csv(P,keep_default_na=False,dtype=str)
g=[]
for i,r in S.iterrows():
 i=int(i)
 if r['sample']=='flagged':g.append('0' if i in L['wrong_flagged'] else '?' if i in L['uncertain_flagged'] else '1')
 else:g.append('1' if i in L['missed_likely'] else '?' if i in L['unflagged_uncertain'] else '0')
S['gold_self_published']=g;S.to_csv(P,index=False)
nf=(S['sample']=='flagged').sum();tp=sum(1 for i,r in S.iterrows() if r['sample']=='flagged' and r.gold_self_published=='1');un=sum(1 for i,r in S.iterrows() if r['sample']=='flagged' and r.gold_self_published=='?')
nu=(S['sample']=='unflagged').sum();miss=sum(1 for i,r in S.iterrows() if r['sample']=='unflagged' and r.gold_self_published=='1');unu=sum(1 for i,r in S.iterrows() if r['sample']=='unflagged' and r.gold_self_published=='?')
md=f"""# Record-only validation read ({cc})

Scope: {nf} flagged + {nu} unflagged records drawn at random (seed 20261109, years 1995-2023) from `{P.name}`, read from the catalogue record only (title, author, publisher string, edition, place). No web lookups. Labels: 1 = reads as self-published, 0 = does not, ? = cannot tell from the record. One reader (the model), no second rater, so these are impressions, not audited precision.

- Flagged precision (record-only): {tp}/{nf} = {tp/nf:.1%} clearly consistent; {un} uncertain; {nf-tp-un} judged wrong. Range if all uncertain were wrong/right: {tp/nf:.1%} to {(tp+un)/nf:.1%}.
- Unflagged: {miss} likely missed self-publications, {unu} uncertain, out of {nu} (proxy for false-negative rate among unflagged: {miss/nu:.1%} to {(miss+unu)/nu:.1%}).
- Flagged rows uncertain: {L['uncertain_flagged']}; wrong: {L['wrong_flagged']}. Unflagged likely missed: {L['missed_likely']}; uncertain: {L['unflagged_uncertain']}.

{L.get('notes','')}
"""
(ROOT/'output'/outd/'validation_read.md').write_text(md);print(md)
