"""Reproduce the revision from frozen record-level inputs; no network required."""
from pathlib import Path
import hashlib
import json
import math
import platform
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
FIG = ROOT / 'figures'
for p in [OUT, FIG]:
    p.mkdir(exist_ok=True)


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n)) / den
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return center-half, center+half


def cells(frame, flag='ap'):
    f = frame[flag]
    return dict(ap_isbn=int((f & frame.has_isbn).sum()),
                ap_noisbn=int((f & ~frame.has_isbn).sum()),
                other_isbn=int((~f & frame.has_isbn).sum()),
                other_noisbn=int((~f & ~frame.has_isbn).sum()))


def rates(frame, flag='ap'):
    c = cells(frame, flag)
    k, n = c['ap_isbn'], c['ap_isbn'] + c['ap_noisbn']
    ko, no = c['other_isbn'], c['other_isbn'] + c['other_noisbn']
    lo, hi = wilson(k, n)
    return dict(**c, ap_total=n, other_total=no,
                ap_rate=k/n, other_rate=ko/no,
                ap_low=lo, ap_high=hi)


def comparison(frame, label, flag='ap', year='pub_year', exclude2014=False, equal_year=False):
    z = frame[frame[year].between(2010, 2019)]
    if exclude2014:
        z = z[z[year] != 2014]
    a, b = z[z[year] <= 2014], z[z[year] >= 2015]
    ar, br = rates(a, flag), rates(b, flag)
    if equal_year:
        ag = a.groupby(year).apply(lambda g: pd.Series(rates(g, flag)), include_groups=False)
        bg = b.groupby(year).apply(lambda g: pd.Series(rates(g, flag)), include_groups=False)
        r0, r1 = ag.ap_rate.mean(), bg.ap_rate.mean()
        o0, o1 = ag.other_rate.mean(), bg.other_rate.mean()
    else:
        r0, r1, o0, o1 = ar['ap_rate'], br['ap_rate'], ar['other_rate'], br['other_rate']
    return dict(specification=label, pre_n=ar['ap_total'], post_n=br['ap_total'],
                pre_rate=r0, post_rate=r1, change_pp=100*(r1-r0),
                other_change_pp=100*(o1-o0), differential_pp=100*((r1-r0)-(o1-o0)))


def logit(p):
    return np.log(p / (1-p))


def main():
    for row in json.loads((ROOT/'provenance/manifest.json').read_text()):
        path = ROOT / row['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], path
    d = pd.read_csv(ROOT/'inputs/records.csv', dtype={'id':str})
    for col in ['ap','ap_orig','has_isbn','gov','nopub','has_dl','foreign_prefix','author_ed_prefix']:
        assert d[col].dtype == bool, col
    assert d.id.is_unique
    assert d.pub_year.between(2005, 2025).all()
    annual = pd.DataFrame([dict(year=int(y), **rates(g)) for y,g in d[d.pub_year<=2019].groupby('pub_year')])
    annual.to_csv(OUT/'annual.csv',index=False)
    # Equation 5: distinguish actual producer composition from ISBN selection.
    shares=[]
    for r in annual.itertuples():
        s=r.ap_total/(r.ap_total+r.other_total)
        q=r.ap_isbn/(r.ap_isbn+r.other_isbn)
        implied=r.ap_rate*s/(r.ap_rate*s+r.other_rate*(1-s))
        assert abs(q-implied)<1e-12
        if r.year in [2014,2015]:
            shares.append(dict(year=r.year,scenario='Observed',catalogue_share=s,
                               ap_coverage=r.ap_rate,other_coverage=r.other_rate,isbn_share=q))
    base=shares[0];post=shares[1];s=base['catalogue_share']
    q=post['ap_coverage']*s/(post['ap_coverage']*s+post['other_coverage']*(1-s))
    shares.append(dict(year=2015,scenario='2014 catalogue composition; 2015 coverage',
                       catalogue_share=s,ap_coverage=post['ap_coverage'],
                       other_coverage=post['other_coverage'],isbn_share=q))
    pd.DataFrame(shares).to_csv(OUT/'producer_share_example.csv',index=False)
    previous = pd.read_csv(ROOT/'provenance/natbib_isbn_by_ap_year.csv').set_index('pub_year')
    for r in annual.itertuples():
        old = previous.loc[r.year]
        assert r.ap_total == old.ap
        assert r.ap_isbn == old.ap_isbn
        assert r.ap_total + r.other_total == old.books
    rows = [comparison(d,'Pooled 2010–14 vs 2015–19'),
            comparison(d,'Exclude 2014',exclude2014=True),
            comparison(d,'Equal weight to each year',equal_year=True),
            comparison(d,'Original classification rule',flag='ap_orig'),
            comparison(d[~d.nopub],'Exclude unidentified publishers'),
            comparison(d[~d.gov],'Exclude government publications'),
            comparison(d,'Legal-deposit-number year',year='dl_year'),
            comparison(d[d.cat_year_raw <= 2020],'Catalogue entry dated by 2020')]
    robust = pd.DataFrame(rows)
    robust.to_csv(OUT/'robustness.csv',index=False)
    oldr = pd.read_csv(ROOT/'provenance/table2_robustness.csv')
    for new_idx, old_idx in [(0,0),(1,5),(3,1),(4,2),(5,3),(6,4)]:
        assert abs(robust.iloc[new_idx].differential_pp + oldr.iloc[old_idx].diff_pp) < 1e-9

    decomp=[]
    for base,end in [(2014,2015),(2013,2015),(2010,2019)]:
        x = annual.set_index('year').loc[base]; y = annual.set_index('year').loc[end]
        observed = math.log(y.ap_isbn / x.ap_isbn)
        recorded = math.log(y.ap_total / x.ap_total)
        coverage = math.log(y.ap_rate / x.ap_rate)
        assert abs(observed - recorded - coverage) < 1e-12
        decomp.append(dict(baseline=base,end=end,isbn_log_change=observed,
                           catalogue_log_change=recorded,coverage_log_change=coverage,
                           coverage_fraction=coverage/observed,
                           baseline_rate_reference=y.ap_total*x.ap_rate))
    pd.DataFrame(decomp).to_csv(OUT/'decomposition.csv',index=False)

    # Forecast the actual main outcome, using one prespecified holdout block.
    # Mean forecast: most recent five training years. Trend: all training years.
    s=annual.set_index('year').ap_rate
    forecasts=[]; metrics=[]
    for model in ['Five-year mean','Linear logit trend']:
        def predict(train, years):
            v=logit(s.loc[train]); yrs=np.array(years)
            if model=='Five-year mean':
                pred=np.repeat(v.iloc[-5:].mean(),len(yrs))
            else:
                coef=np.polyfit(v.index.to_numpy()-2005,v.values,1)
                pred=np.polyval(coef,yrs-2005)
            return 1/(1+np.exp(-pred))
        vy=list(range(2012,2015)); vp=predict(list(range(2005,2012)),vy)
        fy=list(range(2015,2020)); fp=predict(list(range(2005,2015)),fy)
        metrics.append(dict(model=model,holdout='2012–14',
                            holdout_rmse_pp=100*np.sqrt(np.mean((s.loc[vy].values-vp)**2)),
                            post_mean_gap_pp=100*np.mean(s.loc[fy].values-fp)))
        for y,p in zip(vy+fy,list(vp)+list(fp)):
            forecasts.append(dict(model=model,year=y,predicted=p,observed=s.loc[y],
                                  stage='holdout' if y<2015 else 'post'))
    pd.DataFrame(metrics).to_csv(OUT/'direct_forecast_metrics.csv',index=False)
    pd.DataFrame(forecasts).to_csv(OUT/'direct_forecast_paths.csv',index=False)

    # Error rates are scenarios, never estimated human accuracy.
    # Precision = P(true AP | predicted AP); omission = P(true AP | predicted other).
    pre=cells(d[d.pub_year.between(2010,2014)])
    post=cells(d[d.pub_year.between(2015,2019)])
    scenarios=[]
    def corrected(c,pi,pn,qi,qn):
        a=pi*c['ap_isbn']+qi*c['other_isbn']
        b=pn*c['ap_noisbn']+qn*c['other_noisbn']
        return a/(a+b)
    for label, pars in [
        ('Uncorrected',(1,1,0,0,1,1,0,0)),
        ('Uniform precision 95%; no omissions',(.95,.95,0,0,.95,.95,0,0)),
        ('Uniform precision 90%; omissions 0.1%',(.9,.9,.001,.001,.9,.9,.001,.001)),
        ('Uniform precision 90%; omissions 0.5%',(.9,.9,.005,.005,.9,.9,.005,.005)),
        ('Post ISBN omissions only: 0.1%',(1,1,0,0,1,1,.001,0)),
        ('Post ISBN omissions only: 0.5%',(1,1,0,0,1,1,.005,0)),
        ('Post no-ISBN precision 80% only',(1,1,0,0,1,.8,0,0)),
    ]:
        p0=corrected(pre,*pars[:4]);p1=corrected(post,*pars[4:])
        scenarios.append(dict(scenario=label,pre_corrected_rate=p0,post_corrected_rate=p1,
                              change_pp=100*(p1-p0),assumed_parameters=json.dumps(pars)))
    pd.DataFrame(scenarios).to_csv(OUT/'classification_scenarios.csv',index=False)
    target=corrected(pre,1,1,0,0)
    # q applied solely to ISBN-bearing predicted negatives after 2015.
    q=((target*(post['ap_isbn']+post['ap_noisbn'])-post['ap_isbn'])/
       ((1-target)*post['other_isbn']))

    summary=dict(input_records=len(d),input_years='2005–2025; main analysis ends 2019',
                 main_window_records=int(d.pub_year.between(2010,2019).sum()),
                 post_isbn_negative_omission_tipping_rate=q,
                 post_isbn_negative_omission_tipping_count=q*post['other_isbn'],
                 pre_cells=pre,post_cells=post,
                 headline_decomposition=decomp[0],forecast_metrics=metrics)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (OUT/'environment.json').write_text(json.dumps(dict(python=sys.version,
        platform=platform.platform(),pandas=pd.__version__,numpy=np.__version__,matplotlib=matplotlib.__version__),indent=2)+'\n')

    plt.rcParams.update({'font.family':'serif','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'savefig.dpi':180})
    fig,axes=plt.subplots(1,2,figsize=(10.7,4))
    ax=axes[0]
    ax.plot(annual.year,100*annual.ap_rate,'o-',color='#254b40',label='Classified author-published')
    ax.fill_between(annual.year,100*annual.ap_low,100*annual.ap_high,color='#254b40',alpha=.13,label='95% Wilson interval')
    ax.plot(annual.year,100*annual.other_rate,'s-',color='#8a4443',label='Other records')
    ax.set(ylabel='Records with an ISBN (%)',xlabel='Publication year',ylim=(25,100),title='A. ISBN coverage, 2005–19')
    ax.legend(fontsize=8,loc='lower left')
    ax=axes[1];a=annual[annual.year>=2010].copy();base=a[a.year==2013].iloc[0]
    ax.plot(a.year,100*a.ap_total/base.ap_total,'o-',color='#254b40',label='All classified author-published records')
    ax.plot(a.year,100*a.ap_isbn/base.ap_isbn,'s-',color='#8a4443',label='ISBN-bearing subset')
    ax.set(ylabel='Index (2013 = 100)',xlabel='Publication year',title='B. Two counts within one catalogue')
    ax.legend(fontsize=8,loc='upper left')
    for ax in axes:ax.axvline(2014.5,color='#777',ls=':',lw=1)
    fig.tight_layout();fig.savefig(FIG/'figure1_trends.pdf');fig.savefig(FIG/'figure1_trends.png');plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.5,3.6));dc=decomp[0]
    vals=[dc['catalogue_log_change'],dc['coverage_log_change'],dc['isbn_log_change']]
    ax.barh(['All classified records','ISBN coverage within those records','ISBN-bearing records'],vals,color=['#254b40','#a0784b','#8a4443'])
    for i,v in enumerate(vals):ax.text(v-.008,i,f'{v:.3f}',va='center',ha='right')
    ax.set(xlim=(-.43,0),xlabel='Log change, 2014 to 2015');ax.invert_yaxis()
    fig.tight_layout();fig.savefig(FIG/'figure2_decomposition.pdf');fig.savefig(FIG/'figure2_decomposition.png');plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(10.7,4.3))
    ax=axes[0];ax.barh(robust.specification,robust.change_pp,color='#254b40')
    ax.axvline(0,color='#444',lw=.8);ax.invert_yaxis();ax.set(xlabel='Change in ISBN coverage (percentage points)',title='A. Alternative definitions and windows')
    ax.tick_params(axis='y',labelsize=8)
    ax=axes[1];ax.plot(s.index,100*s,'o-',color='#222',label='Observed')
    for model,col in [('Five-year mean','#254b40'),('Linear logit trend','#8a4443')]:
        f=pd.DataFrame(forecasts);f=f[(f.model==model)&(f.stage=='post')]
        ax.plot(f.year,100*f.predicted,'--',color=col,label=model)
    ax.axvline(2014.5,color='#777',ls=':');ax.set(xlabel='Publication year',ylabel='Records with an ISBN (%)',title='B. Direct outcome and simple forecasts')
    ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(FIG/'figure3_robustness.pdf');fig.savefig(FIG/'figure3_robustness.png');plt.close(fig)
    print(robust.round(4).to_string(index=False))
    print(pd.DataFrame(metrics).round(4).to_string(index=False))
    print(pd.DataFrame(scenarios).drop(columns='assumed_parameters').round(4).to_string(index=False))
    print('Tipping omission fraction (post ISBN negatives only):',q)
    print('All provenance, annual-count, robustness and decomposition checks passed.')


if __name__=='__main__':
    main()
