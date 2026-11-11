"""Create the manuscript's numerical tables from analysis outputs."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R=ROOT/'results'


def esc(s):
    return str(s).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('–','--')


def table(name, caption, label, spec, headings, rows, note, size=r'\small'):
    tex=[r'\begin{table}[htbp]\centering'+size,
         r'\caption{'+caption+r'}\label{'+label+'}',
         r'\begin{tabular}{'+spec+r'}\toprule',
         ' & '.join(headings)+r'\\\midrule']
    tex += [' & '.join(str(x) for x in row)+r'\\' for row in rows]
    tex += [r'\bottomrule\end{tabular}',r'\notes{'+note+'}',r'\end{table}']
    (R/name).write_text('\n'.join(tex)+'\n')


def main():
    a=pd.read_csv(R/'annual.csv').set_index('year')
    agency=pd.read_csv(ROOT/'provenance/table1_four_sources.csv',index_col=0)
    agency.index=agency.index.astype(int)
    rows=[['Agency assignments to author-publishers']+[f'{int(agency.loc[y].iloc[0]):,}' for y in [2013,2014,2015]]]
    for label,c in [('All classified author-published records','ap_total'),('With an ISBN','ap_isbn'),('Without an ISBN','ap_noisbn')]:
        rows.append([label]+[f'{int(a.loc[y,c]):,}' for y in [2013,2014,2015]])
    rows.append([r'ISBN coverage (\%)']+[f'{100*a.loc[y,"ap_rate"]:.1f}' for y in [2013,2014,2015]])
    table('table_counts.tex','Agency assignments and national-bibliography records','tab:counts',
          'lrrr',['Series','2013','2014','2015'],rows,
          'Agency figures are CERLALC author-publisher assignments. Remaining rows use one BNP-derived record population and the provisional author-publisher classifier. The agency and bibliography populations differ; their levels are not directly subtractable.')
    robust=pd.read_csv(R/'robustness.csv')
    rows=[[esc(x.specification),f'{100*x.pre_rate:.1f}',f'{100*x.post_rate:.1f}',f'{x.change_pp:.1f}',f'{x.differential_pp:.1f}'] for x in robust.itertuples()]
    table('table_robustness.tex','ISBN coverage under alternative comparisons','tab:robust',
          r'p{.41\linewidth}rrrr',
          ['Specification',r'Pre (\%)',r'Post (\%)','Change (pp)','Diff. (pp)'],rows,
          'Pre: 2010--14; post: 2015--19, with the indicated exclusions or dating changes. Diff. is the coverage change relative to other records, not a causal estimate. Equal-year weights differ from the record-weighted main comparison. Legal-deposit dating uses all records with a parseable deposit year and therefore changes inclusion.')
    s=pd.read_csv(R/'classification_scenarios.csv')
    labels=['Uncorrected',r'95\% precision, no omissions (uniform)',
            r'90\% precision, 0.1\% omissions (uniform)',
            r'90\% precision, 0.5\% omissions (uniform)',
            r'Post ISBN negatives: 0.1\% omissions only',
            r'Post ISBN negatives: 0.5\% omissions only',
            r'Post no-ISBN positives: 80\% precision only']
    rows=[[label,f'{100*x.pre_corrected_rate:.1f}',f'{100*x.post_corrected_rate:.1f}',f'{x.change_pp:.1f}'] for label,x in zip(labels,s.itertuples())]
    table('table_sensitivity.tex','Assumed classification errors and pooled ISBN coverage','tab:sensitivity',
          r'p{.56\linewidth}rrr',['Scenario',r'Pre (\%)',r'Post (\%)','Change (pp)'],rows,
          "Illustrative assumptions, not estimated accuracy or confidence bounds. ``Uniform'' applies the stated precision and negative-record omission probabilities across periods and ISBN groups. In ``only'' rows, all other labels are assumed correct. Omission is the probability of a true author-published record among predicted negatives.")
    rows=[[int(y),f'{int(x.ap_total):,}',f'{int(x.ap_isbn):,}',f'{100*x.ap_rate:.1f}',f'[{100*x.ap_low:.1f}, {100*x.ap_high:.1f}]',f'{100*x.other_rate:.1f}'] for y,x in a.iterrows()]
    table('table_annual.tex','Annual counts and ISBN coverage, 2005--19','tab:annual',
          'rrrrrr',['Year','Classified records','With ISBN',r'Coverage (\%)',r'95\% interval',r'Other (\%)'],rows,
          'The first two count columns concern provisionally classified author-published records. Intervals are Wilson binomial reference intervals conditional on the recorded class, not intervals for classification error, missing publications, or a reform effect.')
    # The prior seven-model result is documented rather than conflated with coverage.
    rmse=pd.read_csv(ROOT/'provenance/ml_validation_rmse.csv',index_col=0).iloc[:,0]
    gaps=pd.read_csv(ROOT/'provenance/ml_counterfactual_gaps.csv',index_col=0)
    weights=(1/rmse**2)/(1/rmse**2).sum()
    names=['Five-year mean','Random walk','Five-year linear trend','Seven-year linear trend',
           'All-history linear trend','Donor-series ridge','Synthetic-control forecast']
    model_rows=[[name,f'{rmse.loc[key]:.3f}',f'{weights.loc[key]:.3f}',f'${gaps.loc[2015:2018,key].mean():.3f}$']
                for name,key in zip(names,rmse.index)]
    table('table_ensemble.tex','Earlier forecasts of a different ISBN-based outcome','tab:ensemble',
          'lrrr',['Model','Validation RMSE','Weight','Post gap'],model_rows,
          'Archived prior analysis: author-publisher share among ISBN-bearing print records. Values are rounded. RMSE and gaps are in logit units. Post gap averages 2015--18. These models do not forecast ISBN coverage among all classified author-published records.')
    print('Wrote five numerical manuscript tables.')


if __name__=='__main__':
    main()
