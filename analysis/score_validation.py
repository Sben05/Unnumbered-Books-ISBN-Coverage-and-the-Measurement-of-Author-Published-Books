"""Score independently adjudicated labels. Never generates or imputes human labels.

Usage: python score_validation.py validation/LABELS_2000.csv
The completed sheet must have Y/N labels and an external reviewer assertion.
"""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python score_validation.py COMPLETED_LABELS.csv')
    labels = pd.read_csv(sys.argv[1],keep_default_na=False)
    if not {'sample_id','human_label','reviewer'}.issubset(labels.columns):
        raise SystemExit('Need sample_id, human_label and reviewer columns.')
    if not labels.sample_id.is_unique:
        raise SystemExit('Duplicate sample IDs.')
    if not labels.human_label.isin(['Y','N']).all() or labels.reviewer.str.strip().eq('').any():
        raise SystemExit('Human validation pending: all rows need adjudicated Y/N labels and reviewer names. Resolve U with evidence first; never silently drop U.')
    key_path = ROOT/'validation/DO_NOT_SHOW_CODERS_key.csv'
    if not key_path.exists():
        raise SystemExit('The blinded sampling key is kept locally and is not published on GitHub. Obtain it from the study author before scoring adjudicated labels.')
    key = pd.read_csv(key_path)
    z = key.merge(labels[['sample_id','human_label','reviewer']],on='sample_id',validate='one_to_one',how='inner')
    if len(z) != len(labels) or len(z) not in (800,2000):
        raise SystemExit('Use the complete 800-record pilot or 2,000-record full design; no unknown IDs.')
    if len(z)==800 and set(z.sample_id) != set(key[key.pilot].sample_id):
        raise SystemExit('The 800 rows do not match the pilot design.')
    strata=['pub_year','predicted_ap','isbn_present']
    z['truth']=z.human_label.eq('Y')
    counts=z.groupby(strata).size()
    assert len(counts)==40
    z['sample_n']=z.groupby(strata).sample_id.transform('size')
    z['weight']=z.population_n/z.sample_n
    def estimate(data,truth):
        w=data.weight.to_numpy();pred=data.predicted_ap.to_numpy();isbn=data.isbn_present.to_numpy()
        year=data.pub_year.to_numpy();ans={}
        for period, mask in [('pre',year<=2014),('post',year>=2015)]:
            true_total=np.sum(w*truth*mask)
            ans[period+'_precision']=np.sum(w*truth*pred*mask)/np.sum(w*pred*mask)
            ans[period+'_recall']=np.sum(w*truth*pred*mask)/true_total if true_total else np.nan
            ans[period+'_isbn_rate']=np.sum(w*truth*isbn*mask)/true_total if true_total else np.nan
        ans['change_pp']=100*(ans['post_isbn_rate']-ans['pre_isbn_rate'])
        for yearval in [2014,2015]:
            mask=year==yearval;total=np.sum(w*truth*mask);with_isbn=np.sum(w*truth*isbn*mask)
            ans[f'total_{yearval}']=total;ans[f'isbn_{yearval}']=with_isbn
        if all(ans[k]>0 for k in ['total_2014','total_2015','isbn_2014','isbn_2015']):
            observed=np.log(ans['isbn_2015']/ans['isbn_2014'])
            coverage=observed-np.log(ans['total_2015']/ans['total_2014'])
            ans['headline_coverage_log_change']=coverage
            ans['headline_coverage_fraction']=coverage/observed if observed else np.nan
        return ans
    est=estimate(z,z.truth.to_numpy())
    # Stratified nonparametric bootstrap: conditional on metadata truth and sample design.
    # At zero observed error this degenerates; report exact zero-error bounds separately.
    rng=np.random.default_rng(20261110);groups=list(z.groupby(strata).indices.values());boot=[]
    for _ in range(2000):
        picked=np.concatenate([rng.choice(ix,len(ix),replace=True) for ix in groups])
        zz=z.iloc[picked]
        boot.append(estimate(zz,zz.truth.to_numpy()))
    b=pd.DataFrame(boot)
    table=pd.DataFrame([dict(metric=k,estimate=v,bootstrap_low=b[k].quantile(.025),bootstrap_high=b[k].quantile(.975)) for k,v in est.items()])
    dest=ROOT/'results';dest.mkdir(exist_ok=True)
    table.to_csv(dest/'human_validation_estimates.csv',index=False)
    rows=[]
    for values,g in z.groupby(strata):
        errors=int((g.truth!=g.predicted_ap).sum());n=len(g);N=int(g.population_n.iloc[0])
        rows.append(dict(zip(strata,values),sample_n=n,population_n=N,errors=errors,
                         one_sided_95_zero_error_upper=1-.05**(1/n) if errors==0 else np.nan))
    pd.DataFrame(rows).to_csv(dest/'human_validation_strata.csv',index=False)
    (dest/'human_validation_notes.json').write_text(json.dumps(dict(n=len(z),
      bootstrap='2,000 resamples within year × predicted class × ISBN cells; intervals are conditional on adjudicated labels, omit finite population correction, and are unreliable at zero observed error. Use stratum zero-error bounds as a separate sensitivity diagnostic.',
      identification='No inference on books absent from the bibliography or on causal reform effects.'),indent=2)+'\n')
    print(table.to_string(index=False))


if __name__=='__main__':
    main()
