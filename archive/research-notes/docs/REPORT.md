# Self-published share of print-book ISBNs: UK vs NZ, France vs Québec

Descriptive only. Read METHODS.md §7 before quoting any number. Share = flagged self-published ÷ print ISBNs in each national bibliography (author = publisher OR known self-publishing service).

## Headline

| Pair | Window | Paid side | Free side |
|---|---|---|---|
| UK vs NZ | 1995–2014 | UK 0.8% → 2.6% (early 3 yrs → late 3 yrs, +1.8 pp; slope 0.16 pp/yr) | **NZ 4.0% → 12.6% (+8.6 pp; 0.51 pp/yr)** |
| France vs Québec, both free | 2010–2018 | France 6.2% → 13.4% (+7.3 pp; 0.78 pp/yr) | Québec 3.8% → 7.1% (+3.2 pp; 0.44 pp/yr) |
| France vs Québec, France charging | 2018 → 2021 | France 13.4% → 14.0% (+0.6 pp) | Québec 7.1% → 9.6% (+2.5 pp) |

1. **UK vs NZ fits the "free grows faster" pattern**, by a wide margin: NZ's share rose about 3× faster per year and ended near 5× the UK level (2013: NZ 13.6%, UK 2.3%). The NZ rise is mostly author = publisher (e.g. 2014: 512 of 522 flags), i.e. authors using their own name as imprint on free ISBNs. NZ's series is smooth and not service-driven.
2. **The UK is a weak comparator.** Its share is driven by services (AuthorHouse, Xlibris), which spike in 2007–2011 and then drop out of the UK count because the imprints' stated place moved from Milton Keynes to Bloomington, Indiana (AuthorHouse: ~1,100 UK-place records in 2009, 40 in 2013, ~1,000 US-place); they are still in the BNB but fail the UK country filter (METHODS §7.1). The UK share after 2011 is therefore a lower bound. Author = publisher alone is flat: 0.87% (1995) → 1.0% (2013).
3. **France vs Québec cannot test the fee hypothesis before 2019**, because France's ISBNs were free then. In 2010–2018 France rose faster than Québec even though both were free. After France began charging (March 2019) its share was flat (13.4 → 14.0%) while Québec's rose (7.1 → 9.6%), the direction the hypothesis predicts, but that is three post-fee years, one noisy break (Édilivre), and a Québec 2021 jump.
4. **France's own trend is clearer in author = publisher:** 1.6% (2009) → 6.7% (2020), tracking BnF's official author-depositor share (r = 0.96) at about two-thirds the level. It accelerated after 2018 (4.1% → 6.7%), while service imprints fell.
5. **NZ and Québec both show a rising self-publishing share with free ISBNs**; NZ's is larger. Both countries also show 979-8 ISBNs from 2018–2020 onward (NZ ~35/yr, Québec ~60/yr), small compared with France (1,229–1,668/yr in 2020–21), so US ISBNs do not explain these gaps.

## Robustness

Across the 14 variants (METHODS §6; 1995–2014 and 2010–2021 pooled), NZ (7.1–8.4%, or 2.8% if initials-only matches are dropped) stays above UK (0.8–1.9%) in every variant that uses author = publisher; services-only is near zero in NZ (0.04%) and QC (0.2%), and 0.8% in the UK. France (3.8–13.3%) vs Québec (4.9–6.6%) depends on the definition. France's pooled share is 11.6% under the main rule but 3.8% with author = publisher only, **below** Québec's 5.8%. So "France is higher than Québec" is a services effect (Édilivre, BoD), not a name-matching effect. The NZ-above-UK gap holds in every variant except services-only (where both are ~0).

## Caveats that change interpretation

- Levels are not comparable across countries (different cataloguing and selection); trends within a country are the more reliable evidence.
- The UK post-2011 service drop is a place-of-publication effect; the UK 2004–05 dip and the France 2016–17 Édilivre dip are unexplained.
- Validation is a small record-only read, not a measured precision/recall.
- UK fee history, BNB selection policy and the start of Québec's free policy are not documented.
- Wilson CIs in the charts reflect sampling only, not classification or coverage error.

## Files

- Figures: `output/selfpub/figures/uk_nz_shares.png`, `fr_qc_shares.png`, `sensitivity.png`
- Tables: `all_by_year.csv`, `uk_nz_by_year.csv`, `fr_qc_by_year.csv`, `sensitivity_by_year.csv`, `trends_and_early_late.csv`, `coverage.csv`, `amazon_and_nz_prefix_context.csv`, `publisher_candidates_*.csv`, `validation_*.csv` (blank gold labels)
