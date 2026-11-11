# RESULTS: self-publishing and ISBN cost (UK, NZ, France, Québec, US)

Everything in one place. Part A: UK/NZ and France/Québec headline study. Part B: US, Amazon and econometric tests. Part C: all year-by-year tables, sensitivity checks, coverage, validation. Definitions, sources and known biases: [METHODS.md](METHODS.md). Descriptive only; no causal claims beyond what Part B states.

## Figures

![uk_nz_shares](output/selfpub/figures/uk_nz_shares.png)

![fr_qc_shares](output/selfpub/figures/fr_qc_shares.png)

![sensitivity](output/selfpub/figures/sensitivity.png)

![ap_share_all](output/selfpub/figures/ap_share_all.png)

![amazon_timeline](output/selfpub/figures/amazon_timeline.png)

![amazon_vs_bowker](output/selfpub/figures/amazon_vs_bowker.png)

![frqc_parallel_trends](output/selfpub/figures/frqc_parallel_trends.png)

![per_capita_ap](output/selfpub/figures/per_capita_ap.png)


# Part A. UK vs NZ and France vs Québec


Descriptive only. Read METHODS.md §7 before quoting any number. Share = flagged self-published ÷ print ISBNs in each national bibliography (author = publisher OR known self-publishing service).

### Headline

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

### Robustness

Across the 14 variants (METHODS §6; 1995–2014 and 2010–2021 pooled), NZ (7.1–8.4%, or 2.8% if initials-only matches are dropped) stays above UK (0.8–1.9%) in every variant that uses author = publisher; services-only is near zero in NZ (0.04%) and QC (0.2%), and 0.8% in the UK. France (3.8–13.3%) vs Québec (4.9–6.6%) depends on the definition. France's pooled share is 11.6% under the main rule but 3.8% with author = publisher only, **below** Québec's 5.8%. So "France is higher than Québec" is a services effect (Édilivre, BoD), not a name-matching effect. The NZ-above-UK gap holds in every variant except services-only (where both are ~0).

### Caveats that change interpretation

- Levels are not comparable across countries (different cataloguing and selection); trends within a country are the more reliable evidence.
- The UK post-2011 service drop is a place-of-publication effect; the UK 2004–05 dip and the France 2016–17 Édilivre dip are unexplained.
- Validation is a small record-only read, not a measured precision/recall.
- UK fee history, BNB selection policy and the start of Québec's free policy are not documented.
- Wilson CIs in the charts reflect sampling only, not classification or coverage error.

### Files

- Figures: `output/selfpub/figures/uk_nz_shares.png`, `fr_qc_shares.png`, `sensitivity.png`
- Tables: `all_by_year.csv`, `uk_nz_by_year.csv`, `fr_qc_by_year.csv`, `sensitivity_by_year.csv`, `trends_and_early_late.csv`, `coverage.csv`, `amazon_and_nz_prefix_context.csv`, `publisher_candidates_*.csv`, `validation_*.csv` (blank gold labels)


# Part B. US, Amazon and econometric tests


Descriptive and quasi-experimental; none of this is a randomized design. Read METHODS.md §7–8 for data limits. All tables are in `output/selfpub/`, figures in `output/selfpub/figures/`. Code: `econ_frqc.py`, `econ_amazon.py`, `econ_did.py`, `econ_figures.py`.

**Outcome used for tests:** *author = publisher* share (AP), because it needs no list of services and the services lists are the least reliable part. The combined share (AP OR service) is reported as a check.

### 0. New data

| Source | What | Caveat |
|---|---|---|
| US, Library of Congress | MDSConnect BooksAll 2016 (MARC21), 10.7M records; 1.79M print ISBNs 1995–2016 after filters | LoC catalogues what it selects, not all US publishing. Counts fall from 2012 (cataloguing lag in a 2016 snapshot), so the **US window is 1995–2011**. |
| Amazon | Amazon Reviews 2023 "Books" product metadata (McAuley Lab), 4.45M products, 2.71M print ISBNs 1995–2022 | A marketplace catalogue, not a national one. No country field. Skews to products with reviews. Treat as a **US-centred marketplace series**. |
| Harvard bibliographic dataset | not used | LoC covers the same ground more fully; Harvard's release is a research-library selection. |

Sanity check on Amazon: Bowker reports self-published = **11% of US ISBNs in 2007 and 40% in 2012** (infodocket/ProQuest summaries of Bowker releases); the Amazon sample gives 6.2% and 23.7% for the combined measure. Same shape, lower level, as expected for a reviews-biased sample (`figures/amazon_vs_bowker.png`).

### 1. US vs New Zealand (general)

| | 1995–2011 level of AP share | Per million people, 2010 |
|---|---|---|
| NZ (free ISBN) | 3.2% → 10.5% | 89.5 |
| US, LoC (paid ISBN) | 0.37% → 0.25% (flat/falling) | 0.7 |
| Québec (free) | – | 38.4 |
| France | – | 19.9 |
| UK (paid) | 0.9% → 0.8% | 9.9 |

Regression (binomial GLM, year fixed effects, year-clustered SEs, 1995–2011, break 2007; `did_amazon_era.csv`): relative to the US-LoC series, NZ's AP share rose by an **odds ratio of 2.98 (bootstrap CI 2.32–3.61)** after 2007, and **2.12 (p = 0.002)** with country-specific linear trends. But the US LoC is a selected catalogue that did not absorb the Amazon boom (see §3), so this contrast mostly shows that **a national legal-deposit catalogue in a paid-ISBN country did not record the self-publishing rise at all**.

### 2. New Zealand after Amazon

- **Unknown-break test (sup-F, residual bootstrap):** NZ's AP log-odds has a structural break in **2007** (F = 22.8, p = 0.001); the combined share has the same break year (F = 23.0, p = 0.001). The Amazon sample's CreateSpace/Independently-published print records go from 933 (2007) to 2,722 (2008) to 5,417 (2009), the same window (`figures/amazon_timeline.png`). 2007 is also the year of the Kindle launch, but that is a coincidence of timing, not tested.
- **NZ authors stayed in the national system.** NZ records carrying US 979-8 ISBNs are only 24–37 a year in 2020–22 (about 1% of NZ print ISBNs). Only 3–6.5% (2013–22) of NZ's 978-0-473 / 978-1-06 pool ISBNs show up in the Amazon sample at all. Free local ISBNs absorbed the Amazon-era surge instead of Amazon's.
- **Mechanism, entry:** NZ's AP publishers per year rise from 174 (2006) to 362 (2009) and 428 (2016), mostly new names (entrants 139 → 273). The UK shows a similar jump in 2007 (212 → 342 entrants), so the 2007 surge is a shared technology shock; NZ's response is larger in share terms.
- **Mechanism, the agency's small-publisher pool:** inside NZ's 978-0-473 / 978-1-06 pool, AP ISBNs go from 170 (2006) to 357 (2009) and 371 (2012), while AP ISBNs outside the pool stay roughly flat at 50–100. The pool itself grows from 760 to 1,231 ISBNs a year. The NZ surge ran through the National Library's free pool, not through established publishers (a descriptive count, not a causal test).
- **Honest caveat:** UK AP also rose in 2007 (0.69% → 0.91% by 2008, +31%; NZ +70%), and the NZ–UK difference shrinks with country trends (OR 1.29, p = 0.27). **The NZ-vs-UK comparison supports "bigger rise where ISBNs are free" without country trends (OR 1.79, CI 1.54–2.10) but is not significant once pre-existing trends are allowed.** Using the combined measure the sign reverses (OR 0.66) because the UK's author-services boom (AuthorHouse etc.) lifts the UK numerator.

### 3. UK and US after Amazon: leakage out of the national bibliography

- Amazon sample, CreateSpace/"Independently published" print records in 2012: **24,169**. The same imprints in national bibliographies in 2012: **UK 35, US (LoC) 57, NZ 2, France 0, Québec 0** (`amazon_issued_capture.csv`). National bibliographies in the UK and US essentially do not see Amazon-issued ISBNs; the LoC does not catalogue them and BNB hardly does.
- The AP share in those bibliographies is flat (~1% UK, ~0.3% US-LoC; AP only) through the boom, while marketplace-level self-publishing went from 6% (2007) to 24% (2012) to 49% (2021) in the Amazon sample, and 11% → 40% (2007 → 2012) in Bowker's published figures.
- Reading: in paid-ISBN countries, the 2008–2015 self-publishing boom happened largely **outside the national ISBN agency and legal-deposit record**, via Amazon's free ISBNs (CreateSpace, then KDP "Independently published", then 979-8 from 2020: ~50,000 records a year by 2020). In free-ISBN countries (NZ, Québec) it stayed inside. This is the mechanism that makes national-bibliography shares a measure of *how self-publishers use the national agency*, not of total self-publishing, and it is the main reason cross-country levels must not be compared as if they measured the same thing.
- UK break tests: AP break 2001 (artefact of a drop in 2001–02, not an Amazon effect); combined break 2007 (F = 14.4, p = 0.004), driven by AuthorHouse/Xlibris.

### 4. France vs Québec before and after March 2019

Test unit: yearly gap in log-odds, d_t = logit(p_FR) − logit(p_QC) (binomial variance, no pooling across two units), 2010–2021. Figure: `figures/frqc_parallel_trends.png`.

**Pre-2019 (2010–2018), author = publisher: the two series are close to parallel.**
- The gap moves from −0.65 to −0.51 (France closes ~15% of the odds ratio over eight years): slope +0.021 per year (Newey–West SE 0.005, p = 0.004; permutation p = 0.083). Small but nonzero convergence.
- Residual SD around that trend is 0.083, i.e. yearly noise of about 8% in odds. Year-to-year changes are not correlated (r = −0.10): parallel in trend, not in shocks.
- Combined share: gap slope 0.006 per year (p = 0.86), but noisy (SD 0.35) because of Édilivre's 2013–15 surge and 2017 dip.

**After March 2019: no break in the predicted direction.**
- AP gap relative to its pre-trend: 2019 +0.05 (0.6 pre-SD), 2020 +0.42 (5.1 SD), 2021 +0.05; mean +0.18. Level shift p = 0.08, slope change 0.000 (p = 0.9996). The sign is **France higher relative to Québec**, the opposite of "fee reduces self-publishing".
- The 2020 spike is mostly a Québec COVID dip (Québec AP ISBNs 501 → 380 while France's rose 3,670 → 4,574); 2019 and 2021 are back on the pre-trend.
- Combined share: mean deviation −0.09 (−0.26 SD), nothing.
- France's AP publishers and new entrants kept rising straight through 2019–2021 (entrants 1,479 → 1,744 → 2,175 → 2,352; ISBNs per author-publisher stable, 1.40–1.44) (`frqc_author_publisher_entry.csv`).

**Why this is not the clean "fee" natural experiment.** The only AFNIL schedule I could retrieve (2025 page; the 2019 amount is not documented here) charges a one-off **dossier fee of €37 excl. VAT for a first ISBN request**, with a €28 fee for a further list and optional expedited processing at €87–154. That is a lump sum for a block, not a per-ISBN price. UK Nielsen is £93 for a single ISBN. So France moved from free to a small one-off cost; the fee treatment is weak, and a null is the expected result. **The parallel-trends design is strong, but the treatment is weak, so I cannot say a larger fee would not bite.** What the pre-2019 parallelism does give is a clean baseline for France/Québec in case another treatment is found (for example the 2019 website change that made applications online-only, or Québec policy changes).

### 5. Summary of what holds up

1. **Strongest:** NZ's author-publisher share broke upward in 2007 (p = 0.001), coincident with Amazon/POD self-publishing, and NZ's per-capita rate (~90–110 per million) is about 10× the UK's (~10) and ~100× the US-LoC's. Free local ISBNs plus POD tools fit this. Cataloguing and selection differences could account for part of the level gap.
2. **Strong, but mechanism not tested:** in paid-ISBN countries the Amazon-era boom sits outside national bibliographies (national records show 35–57 Amazon-issued ISBNs a year against ~24,000 on Amazon).
3. **Null with qualification:** France vs Québec are parallel before 2019 on author=publisher, and show no sustained break after the 2019 fee; the fee was small.
4. **Does not hold:** the combined measure's UK vs NZ difference reverses sign (UK services boom). Country-trend-adjusted NZ vs UK AP effect is not significant.

### 6. Ideas not yet done

- Get the 2019 AFNIL tariff and the Québec policy history, then redo §4 with the right dose.
- Use the Amazon data with publisher location (Amazon "Publisher" strings) to build a UK, NZ and Québec marketplace series.
- Find a second, paid-ISBN francophone comparator (Belgium via KBR; Switzerland) for a three-way France comparison.
- Human validation of the blank gold-label CSVs, then correct estimates for misclassification.


# Part C. Tables

## C1. Print ISBNs and self-published shares by year (all sources, full classified range)

Columns: share = (author=publisher OR service)/print ISBNs; ap = author=publisher; svc = service imprint; corp = corporate author=publisher (not counted); window = inside the main window.

### United Kingdom (BNB, May 2018 snapshot; 2015+ incomplete)

| pub_year | print_isbns | self_published | share | wilson_low | wilson_high | author_is_publisher | service_imprint | corporate_self | unidentified_publisher | main_window |
|---|---|---|---|---|---|---|---|---|---|---|
| 1995 | 60454 | 523.0 | 0.0087 | 0.0079 | 0.0094 | 522.0 | 1.0000 | 3,424.0 | 92.0 | True |
| 1996 | 64457 | 490.0 | 0.0076 | 0.0070 | 0.0083 | 486.0 | 4.0000 | 3,480.0 | 88.0 | True |
| 1997 | 69551 | 520.0 | 0.0075 | 0.0069 | 0.0081 | 516.0 | 4.0000 | 3,213.0 | 46.0 | True |
| 1998 | 72672 | 526.0 | 0.0072 | 0.0066 | 0.0079 | 523.0 | 3.0000 | 3,272.0 | 61.0 | True |
| 1999 | 75420 | 580.0 | 0.0077 | 0.0071 | 0.0083 | 573.0 | 7.0000 | 3,171.0 | 89.0 | True |
| 2000 | 80979 | 556.0 | 0.0069 | 0.0063 | 0.0075 | 542.0 | 14.0 | 3,032.0 | 73.0 | True |
| 2001 | 74663 | 393.0 | 0.0053 | 0.0048 | 0.0058 | 375.0 | 18.0 | 2,813.0 | 74.0 | True |
| 2002 | 74689 | 393.0 | 0.0053 | 0.0048 | 0.0058 | 356.0 | 37.0 | 2,940.0 | 77.0 | True |
| 2003 | 66761 | 452.0 | 0.0068 | 0.0062 | 0.0074 | 383.0 | 69.0 | 2,723.0 | 62.0 | True |
| 2004 | 52676 | 470.0 | 0.0089 | 0.0082 | 0.0098 | 378.0 | 92.0 | 2,505.0 | 13.0 | True |
| 2005 | 54073 | 496.0 | 0.0092 | 0.0084 | 0.0100 | 354.0 | 142.0 | 2,722.0 | 15.0 | True |
| 2006 | 55747 | 609.0 | 0.0109 | 0.0101 | 0.0118 | 386.0 | 224.0 | 2,799.0 | 25.0 | True |
| 2007 | 66619 | 1,188.0 | 0.0178 | 0.0169 | 0.0189 | 538.0 | 650.0 | 3,843.0 | 22.0 | True |
| 2008 | 67797 | 1,685.0 | 0.0249 | 0.0237 | 0.0261 | 614.0 | 1,073.0 | 3,778.0 | 30.0 | True |
| 2009 | 70117 | 2,140.0 | 0.0305 | 0.0293 | 0.0318 | 549.0 | 1,593.0 | 3,815.0 | 30.0 | True |
| 2010 | 70979 | 2,334.0 | 0.0329 | 0.0316 | 0.0342 | 619.0 | 1,716.0 | 3,805.0 | 49.0 | True |
| 2011 | 69627 | 2,879.0 | 0.0413 | 0.0399 | 0.0429 | 558.0 | 2,321.0 | 3,202.0 | 30.0 | True |
| 2012 | 68935 | 2,286.0 | 0.0332 | 0.0319 | 0.0345 | 803.0 | 1,485.0 | 2,414.0 | 71.0 | True |
| 2013 | 71317 | 1,664.0 | 0.0233 | 0.0222 | 0.0245 | 748.0 | 916.0 | 2,023.0 | 74.0 | True |
| 2014 | 70636 | 1,571.0 | 0.0222 | 0.0212 | 0.0234 | 783.0 | 788.0 | 1,869.0 | 65.0 | True |
| 2015 | 42750 | 1,272.0 | 0.0298 | 0.0282 | 0.0314 | 538.0 | 735.0 | 1,770.0 | 51.0 | False |
| 2016 | 34052 | 1,152.0 | 0.0338 | 0.0320 | 0.0358 | 498.0 | 655.0 | 1,712.0 | 48.0 | False |
| 2017 | 10761 | 330.0 | 0.0307 | 0.0276 | 0.0341 | 227.0 | 103.0 | 1,033.0 | 22.0 | False |
| 2018 | 906 | 34.0 | 0.0375 | 0.0270 | 0.0520 | 23.0 | 11.0 | 121.0 | 6.0000 | False |

### New Zealand

| pub_year | print_isbns | self_published | share | wilson_low | wilson_high | author_is_publisher | service_imprint | corporate_self | unidentified_publisher | main_window |
|---|---|---|---|---|---|---|---|---|---|---|
| 1995 | 3298 | 107.0 | 0.0324 | 0.0269 | 0.0391 | 107.0 | 0.0000 | 564.0 | 0.0000 | True |
| 1996 | 3347 | 149.0 | 0.0445 | 0.0380 | 0.0520 | 149.0 | 0.0000 | 593.0 | 0.0000 | True |
| 1997 | 3772 | 165.0 | 0.0437 | 0.0377 | 0.0507 | 165.0 | 0.0000 | 592.0 | 1.0000 | True |
| 1998 | 3983 | 222.0 | 0.0557 | 0.0490 | 0.0633 | 222.0 | 0.0000 | 756.0 | 2.0000 | True |
| 1999 | 3772 | 166.0 | 0.0440 | 0.0379 | 0.0510 | 166.0 | 0.0000 | 649.0 | 9.0000 | True |
| 2000 | 3834 | 176.0 | 0.0459 | 0.0397 | 0.0530 | 176.0 | 0.0000 | 693.0 | 6.0000 | True |
| 2001 | 3618 | 177.0 | 0.0489 | 0.0424 | 0.0564 | 176.0 | 1.0000 | 610.0 | 10.0 | True |
| 2002 | 3749 | 173.0 | 0.0461 | 0.0399 | 0.0533 | 173.0 | 0.0000 | 611.0 | 12.0 | True |
| 2003 | 3531 | 160.0 | 0.0453 | 0.0389 | 0.0527 | 160.0 | 0.0000 | 570.0 | 1.0000 | True |
| 2004 | 3897 | 177.0 | 0.0454 | 0.0393 | 0.0524 | 176.0 | 1.0000 | 652.0 | 1.0000 | True |
| 2005 | 3790 | 174.0 | 0.0459 | 0.0397 | 0.0530 | 173.0 | 1.0000 | 632.0 | 3.0000 | True |
| 2006 | 3748 | 199.0 | 0.0531 | 0.0464 | 0.0607 | 196.0 | 3.0000 | 564.0 | 8.0000 | True |
| 2007 | 3778 | 290.0 | 0.0768 | 0.0687 | 0.0857 | 287.0 | 3.0000 | 594.0 | 2.0000 | True |
| 2008 | 4062 | 365.0 | 0.0899 | 0.0814 | 0.0990 | 365.0 | 0.0000 | 665.0 | 0.0000 | True |
| 2009 | 3779 | 437.0 | 0.1156 | 0.1058 | 0.1262 | 436.0 | 1.0000 | 652.0 | 2.0000 | True |
| 2010 | 4010 | 393.0 | 0.0980 | 0.0892 | 0.1076 | 391.0 | 2.0000 | 545.0 | 0.0000 | True |
| 2011 | 3591 | 377.0 | 0.1050 | 0.0954 | 0.1154 | 377.0 | 0.0000 | 540.0 | 2.0000 | True |
| 2012 | 4028 | 450.0 | 0.1117 | 0.1024 | 0.1218 | 441.0 | 9.0000 | 504.0 | 3.0000 | True |
| 2013 | 3687 | 500.0 | 0.1356 | 0.1249 | 0.1470 | 498.0 | 2.0000 | 453.0 | 5.0000 | True |
| 2014 | 3973 | 522.0 | 0.1314 | 0.1212 | 0.1422 | 512.0 | 10.0 | 421.0 | 2.0000 | True |
| 2015 | 3845 | 515.0 | 0.1339 | 0.1235 | 0.1451 | 486.0 | 30.0 | 426.0 | 4.0000 | False |
| 2016 | 3528 | 573.0 | 0.1624 | 0.1506 | 0.1750 | 547.0 | 27.0 | 349.0 | 1.0000 | False |
| 2017 | 3862 | 577.0 | 0.1494 | 0.1385 | 0.1610 | 556.0 | 21.0 | 289.0 | 1.0000 | False |
| 2018 | 3533 | 534.0 | 0.1511 | 0.1397 | 0.1633 | 516.0 | 18.0 | 262.0 | 2.0000 | False |
| 2019 | 3587 | 560.0 | 0.1561 | 0.1446 | 0.1684 | 542.0 | 18.0 | 254.0 | 2.0000 | False |
| 2020 | 2948 | 638.0 | 0.2164 | 0.2019 | 0.2316 | 619.0 | 20.0 | 176.0 | 0.0000 | False |
| 2021 | 2695 | 509.0 | 0.1889 | 0.1745 | 0.2041 | 483.0 | 28.0 | 219.0 | 0.0000 | False |
| 2022 | 2715 | 537.0 | 0.1978 | 0.1832 | 0.2132 | 513.0 | 25.0 | 284.0 | 0.0000 | False |

### France (2022 incomplete)

| pub_year | print_isbns | self_published | share | wilson_low | wilson_high | author_is_publisher | service_imprint | corporate_self | unidentified_publisher | main_window |
|---|---|---|---|---|---|---|---|---|---|---|
| 1995 | 32676 | 399.0 | 0.0122 | 0.0111 | 0.0135 | 328.0 | 71.0 | 658.0 | 6.0000 | False |
| 1996 | 35688 | 540.0 | 0.0151 | 0.0139 | 0.0165 | 442.0 | 98.0 | 735.0 | 6.0000 | False |
| 1997 | 38661 | 586.0 | 0.0152 | 0.0140 | 0.0164 | 509.0 | 77.0 | 767.0 | 9.0000 | False |
| 1998 | 42301 | 625.0 | 0.0148 | 0.0137 | 0.0160 | 548.0 | 77.0 | 758.0 | 14.0 | False |
| 1999 | 43908 | 643.0 | 0.0146 | 0.0136 | 0.0158 | 548.0 | 95.0 | 835.0 | 12.0 | False |
| 2000 | 44038 | 596.0 | 0.0135 | 0.0125 | 0.0147 | 495.0 | 101.0 | 814.0 | 25.0 | False |
| 2001 | 45384 | 598.0 | 0.0132 | 0.0122 | 0.0143 | 488.0 | 110.0 | 745.0 | 25.0 | False |
| 2002 | 46938 | 616.0 | 0.0131 | 0.0121 | 0.0142 | 514.0 | 102.0 | 777.0 | 4.0000 | False |
| 2003 | 47505 | 681.0 | 0.0143 | 0.0133 | 0.0154 | 521.0 | 160.0 | 776.0 | 3.0000 | False |
| 2004 | 50989 | 792.0 | 0.0155 | 0.0145 | 0.0166 | 645.0 | 147.0 | 782.0 | 6.0000 | False |
| 2005 | 53343 | 1,477.0 | 0.0277 | 0.0263 | 0.0291 | 737.0 | 740.0 | 810.0 | 15.0 | False |
| 2006 | 54873 | 1,640.0 | 0.0299 | 0.0285 | 0.0313 | 716.0 | 924.0 | 919.0 | 18.0 | False |
| 2007 | 57657 | 2,335.0 | 0.0405 | 0.0389 | 0.0421 | 817.0 | 1,518.0 | 960.0 | 8.0000 | False |
| 2008 | 59560 | 2,954.0 | 0.0496 | 0.0479 | 0.0514 | 871.0 | 2,088.0 | 925.0 | 18.0 | False |
| 2009 | 59790 | 3,478.0 | 0.0582 | 0.0563 | 0.0601 | 989.0 | 2,491.0 | 879.0 | 5.0000 | False |
| 2010 | 63691 | 3,935.0 | 0.0618 | 0.0599 | 0.0637 | 1,287.0 | 2,652.0 | 854.0 | 6.0000 | True |
| 2011 | 66068 | 4,741.0 | 0.0718 | 0.0698 | 0.0738 | 1,471.0 | 3,272.0 | 880.0 | 4.0000 | True |
| 2012 | 67568 | 5,364.0 | 0.0794 | 0.0774 | 0.0814 | 1,542.0 | 3,822.0 | 866.0 | 8.0000 | True |
| 2013 | 68540 | 6,972.0 | 0.1017 | 0.0995 | 0.1040 | 1,731.0 | 5,241.0 | 864.0 | 16.0 | True |
| 2014 | 69310 | 10,139.0 | 0.1463 | 0.1437 | 0.1489 | 1,898.0 | 8,242.0 | 882.0 | 13.0 | True |
| 2015 | 72342 | 10,786.0 | 0.1491 | 0.1465 | 0.1517 | 2,180.0 | 8,606.0 | 1,046.0 | 22.0 | True |
| 2016 | 72678 | 8,710.0 | 0.1198 | 0.1175 | 0.1222 | 2,436.0 | 6,274.0 | 1,003.0 | 17.0 | True |
| 2017 | 71110 | 6,318.0 | 0.0888 | 0.0868 | 0.0910 | 2,830.0 | 3,488.0 | 1,053.0 | 39.0 | True |
| 2018 | 76072 | 10,225.0 | 0.1344 | 0.1320 | 0.1369 | 3,105.0 | 7,120.0 | 979.0 | 27.0 | True |
| 2019 | 75351 | 10,109.0 | 0.1342 | 0.1317 | 0.1366 | 3,670.0 | 6,439.0 | 936.0 | 19.0 | True |
| 2020 | 68569 | 10,646.0 | 0.1553 | 0.1526 | 0.1580 | 4,579.0 | 6,072.0 | 747.0 | 21.0 | True |
| 2021 | 77214 | 10,844.0 | 0.1404 | 0.1380 | 0.1429 | 5,071.0 | 5,774.0 | 781.0 | 20.0 | True |
| 2022 | 62928 | 4,192.0 | 0.0666 | 0.0647 | 0.0686 | 2,142.0 | 2,053.0 | 853.0 | 20.0 | False |

### Québec (2010+)

| pub_year | print_isbns | self_published | share | wilson_low | wilson_high | author_is_publisher | service_imprint | corporate_self | unidentified_publisher | main_window |
|---|---|---|---|---|---|---|---|---|---|---|
| 2010 | 7958 | 304.0 | 0.0382 | 0.0342 | 0.0426 | 303.0 | 1.0000 | 434.0 | 3.0000 | True |
| 2011 | 7976 | 325.0 | 0.0407 | 0.0366 | 0.0453 | 319.0 | 6.0000 | 464.0 | 0.0000 | True |
| 2012 | 8116 | 415.0 | 0.0511 | 0.0466 | 0.0561 | 412.0 | 3.0000 | 364.0 | 2.0000 | True |
| 2013 | 7025 | 312.0 | 0.0444 | 0.0398 | 0.0495 | 311.0 | 1.0000 | 397.0 | 0.0000 | True |
| 2014 | 7902 | 381.0 | 0.0482 | 0.0437 | 0.0532 | 376.0 | 5.0000 | 349.0 | 0.0000 | True |
| 2015 | 7155 | 376.0 | 0.0526 | 0.0476 | 0.0580 | 355.0 | 21.0 | 412.0 | 0.0000 | True |
| 2016 | 7405 | 481.0 | 0.0650 | 0.0596 | 0.0708 | 447.0 | 34.0 | 438.0 | 0.0000 | True |
| 2017 | 7385 | 537.0 | 0.0727 | 0.0670 | 0.0789 | 492.0 | 45.0 | 487.0 | 0.0000 | True |
| 2018 | 7131 | 504.0 | 0.0707 | 0.0650 | 0.0769 | 472.0 | 32.0 | 509.0 | 0.0000 | True |
| 2019 | 6764 | 501.0 | 0.0741 | 0.0681 | 0.0806 | 501.0 | 0.0000 | 369.0 | 0.0000 | True |
| 2020 | 5394 | 380.0 | 0.0704 | 0.0639 | 0.0776 | 380.0 | 0.0000 | 315.0 | 2.0000 | True |
| 2021 | 6461 | 618.0 | 0.0957 | 0.0887 | 0.1031 | 616.0 | 2.0000 | 251.0 | 8.0000 | True |
| 2022 | 5977 | 464.0 | 0.0776 | 0.0711 | 0.0847 | 463.0 | 1.0000 | 288.0 | 0.0000 | False |

### US, Library of Congress (window 1995–2011; later years truncated)

| pub_year | print_isbns | self_published | author_is_publisher | service_imprint | service_platform | amazon_imprint | i9798 | share |
|---|---|---|---|---|---|---|---|---|
| 1995 | 74559 | 296.0 | 276.0 | 20.0 | 0.0000 | 0.0000 | 0.0000 | 0.0040 |
| 1996 | 78127 | 350.0 | 319.0 | 31.0 | 0.0000 | 0.0000 | 0.0000 | 0.0045 |
| 1997 | 79389 | 339.0 | 306.0 | 33.0 | 0.0000 | 0.0000 | 0.0000 | 0.0043 |
| 1998 | 81041 | 486.0 | 325.0 | 167.0 | 0.0000 | 0.0000 | 0.0000 | 0.0060 |
| 1999 | 82270 | 439.0 | 304.0 | 137.0 | 0.0000 | 0.0000 | 0.0000 | 0.0053 |
| 2000 | 85150 | 598.0 | 291.0 | 309.0 | 0.0000 | 0.0000 | 0.0000 | 0.0070 |
| 2001 | 83989 | 633.0 | 285.0 | 352.0 | 0.0000 | 0.0000 | 0.0000 | 0.0075 |
| 2002 | 88826 | 827.0 | 303.0 | 540.0 | 0.0000 | 1.0000 | 0.0000 | 0.0093 |
| 2003 | 91475 | 1,179.0 | 345.0 | 858.0 | 1.0000 | 8.0000 | 0.0000 | 0.0129 |
| 2004 | 94142 | 1,565.0 | 321.0 | 1,252.0 | 7.0000 | 25.0 | 0.0000 | 0.0166 |
| 2005 | 93459 | 1,641.0 | 337.0 | 1,327.0 | 7.0000 | 15.0 | 0.0000 | 0.0176 |
| 2006 | 94496 | 1,526.0 | 284.0 | 1,260.0 | 18.0 | 32.0 | 0.0000 | 0.0161 |
| 2007 | 91797 | 1,521.0 | 287.0 | 1,261.0 | 23.0 | 32.0 | 0.0000 | 0.0166 |
| 2008 | 92804 | 1,553.0 | 245.0 | 1,315.0 | 43.0 | 32.0 | 0.0000 | 0.0167 |
| 2009 | 92168 | 1,918.0 | 250.0 | 1,679.0 | 26.0 | 52.0 | 0.0000 | 0.0208 |
| 2010 | 91486 | 1,395.0 | 230.0 | 1,177.0 | 42.0 | 29.0 | 0.0000 | 0.0152 |
| 2011 | 88707 | 1,146.0 | 219.0 | 929.0 | 63.0 | 50.0 | 0.0000 | 0.0129 |
| 2012 | 85810 | 813.0 | 186.0 | 627.0 | 64.0 | 57.0 | 0.0000 | 0.0095 |
| 2013 | 77817 | 449.0 | 123.0 | 327.0 | 62.0 | 55.0 | 0.0000 | 0.0058 |
| 2014 | 67607 | 252.0 | 79.0 | 173.0 | 38.0 | 33.0 | 0.0000 | 0.0037 |
| 2015 | 54395 | 37.0 | 21.0 | 17.0 | 4.0000 | 2.0000 | 0.0000 | 0.0007 |
| 2016 | 22731 | 2.0000 | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0001 |
| 2017 | 994 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 2018 | 7 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 2019 | 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

### Amazon marketplace sample (print ISBNs, all countries, US-centred)

| pub_year | print_isbns | self_published | author_is_publisher | service_imprint | service_platform | amazon_imprint | i9798 | share |
|---|---|---|---|---|---|---|---|---|
| 1995 | 28333 | 85.0 | 81.0 | 4.0000 | 3.0000 | 10.0 | 1.0000 | 0.0030 |
| 1996 | 31907 | 90.0 | 88.0 | 2.0000 | 1.0000 | 12.0 | 0.0000 | 0.0028 |
| 1997 | 37957 | 130.0 | 125.0 | 5.0000 | 1.0000 | 21.0 | 0.0000 | 0.0034 |
| 1998 | 42960 | 178.0 | 141.0 | 37.0 | 5.0000 | 23.0 | 0.0000 | 0.0041 |
| 1999 | 48008 | 351.0 | 192.0 | 159.0 | 4.0000 | 35.0 | 3.0000 | 0.0073 |
| 2000 | 54957 | 1,542.0 | 171.0 | 1,371.0 | 6.0000 | 36.0 | 1.0000 | 0.0281 |
| 2001 | 55509 | 1,422.0 | 168.0 | 1,254.0 | 3.0000 | 95.0 | 0.0000 | 0.0256 |
| 2002 | 59325 | 1,419.0 | 225.0 | 1,194.0 | 6.0000 | 129.0 | 3.0000 | 0.0239 |
| 2003 | 64980 | 1,786.0 | 256.0 | 1,530.0 | 26.0 | 154.0 | 4.0000 | 0.0275 |
| 2004 | 69178 | 2,463.0 | 234.0 | 2,229.0 | 110.0 | 184.0 | 2.0000 | 0.0356 |
| 2005 | 75136 | 3,392.0 | 301.0 | 3,091.0 | 361.0 | 403.0 | 9.0000 | 0.0451 |
| 2006 | 81885 | 4,968.0 | 348.0 | 4,620.0 | 691.0 | 753.0 | 7.0000 | 0.0607 |
| 2007 | 86458 | 5,354.0 | 402.0 | 4,952.0 | 1,045.0 | 933.0 | 5.0000 | 0.0619 |
| 2008 | 92343 | 7,445.0 | 472.0 | 6,973.0 | 2,581.0 | 2,722.0 | 11.0 | 0.0806 |
| 2009 | 97501 | 10,934.0 | 596.0 | 10,338.0 | 4,795.0 | 5,417.0 | 14.0 | 0.1121 |
| 2010 | 108895 | 14,091.0 | 642.0 | 13,449.0 | 8,857.0 | 7,782.0 | 12.0 | 0.1294 |
| 2011 | 115802 | 19,855.0 | 1,016.0 | 18,839.0 | 14,292.0 | 12,842.0 | 14.0 | 0.1715 |
| 2012 | 131782 | 31,285.0 | 1,642.0 | 29,643.0 | 25,456.0 | 24,169.0 | 23.0 | 0.2374 |
| 2013 | 143137 | 39,158.0 | 2,284.0 | 36,874.0 | 33,227.0 | 32,019.0 | 35.0 | 0.2736 |
| 2014 | 147444 | 45,457.0 | 2,653.0 | 42,804.0 | 39,843.0 | 38,363.0 | 35.0 | 0.3083 |
| 2015 | 151432 | 49,141.0 | 3,256.0 | 45,885.0 | 43,705.0 | 42,164.0 | 37.0 | 0.3245 |
| 2016 | 151667 | 53,495.0 | 3,484.0 | 50,011.0 | 48,088.0 | 46,644.0 | 51.0 | 0.3527 |
| 2017 | 151790 | 60,536.0 | 4,065.0 | 56,471.0 | 54,936.0 | 53,703.0 | 83.0 | 0.3988 |
| 2018 | 144537 | 56,890.0 | 3,576.0 | 53,320.0 | 52,192.0 | 51,028.0 | 119.0 | 0.3936 |
| 2019 | 137144 | 56,435.0 | 3,591.0 | 52,854.0 | 51,793.0 | 51,877.0 | 207.0 | 0.4115 |
| 2020 | 132521 | 60,440.0 | 4,271.0 | 56,172.0 | 55,340.0 | 55,001.0 | 50,712.0 | 0.4561 |
| 2021 | 148033 | 73,894.0 | 4,914.0 | 68,982.0 | 68,047.0 | 67,592.0 | 68,038.0 | 0.4992 |
| 2022 | 121538 | 59,524.0 | 4,802.0 | 54,727.0 | 54,087.0 | 53,783.0 | 62,643.0 | 0.4898 |

## C2. Trends and early/late changes (all variants)

| source | variant | start_year | end_year | slope_pp_per_year | early_pooled_share | late_pooled_share | change_pp | early_n | late_n |
|---|---|---|---|---|---|---|---|---|---|
| uk | main | 1995 | 2014 | 0.1547 | 0.0079 | 0.0262 | 1.8296 | 194462 | 210888 |
| uk | author_only | 1995 | 2014 | 0.0181 | 0.0078 | 0.0111 | 0.3230 | 194462 | 210888 |
| uk | services_only | 1995 | 2014 | 0.1366 | 0.0000 | 0.0151 | 1.5075 | 194462 | 210888 |
| uk | author_plus_platform | 1995 | 2014 | 0.0241 | 0.0078 | 0.0121 | 0.4255 | 194462 | 210888 |
| uk | exclude_vanity | 1995 | 2014 | 0.1547 | 0.0079 | 0.0262 | 1.8296 | 194462 | 210888 |
| uk | include_mixed_contract_imprints | 1995 | 2014 | 0.1697 | 0.0091 | 0.0302 | 2.1026 | 194462 | 210888 |
| uk | exclude_government_standards | 1995 | 2014 | 0.1552 | 0.0080 | 0.0263 | 1.8247 | 191060 | 210164 |
| uk | exclude_theses | 1995 | 2014 | 0.1547 | 0.0079 | 0.0262 | 1.8316 | 194006 | 210596 |
| uk | exclude_reprints_new_editions | 1995 | 2014 | 0.1540 | 0.0080 | 0.0259 | 1.7953 | 190255 | 207671 |
| uk | exclude_all_four | 1995 | 2014 | 0.1545 | 0.0081 | 0.0260 | 1.7921 | 186531 | 206725 |
| uk | exclude_initials_only_matches | 1995 | 2014 | 0.1770 | 0.0033 | 0.0256 | 2.2348 | 194462 | 210888 |
| uk | include_contributor_matches | 1995 | 2014 | 0.1555 | 0.0087 | 0.0271 | 1.8388 | 194462 | 210888 |
| uk | exclude_unidentified_publishers | 1995 | 2014 | 0.1548 | 0.0079 | 0.0262 | 1.8313 | 194236 | 210678 |
| uk | normalized_title_author_groups | 1995 | 2014 | 0.1888 | 0.0090 | 0.0312 | 2.2203 | 163471 | 153467 |
| nz | main | 1995 | 2014 | 0.5093 | 0.0404 | 0.1259 | 8.5526 | 10417 | 11688 |
| nz | author_only | 1995 | 2014 | 0.5015 | 0.0404 | 0.1241 | 8.3730 | 10417 | 11688 |
| nz | services_only | 1995 | 2014 | 0.0077 | 0.0000 | 0.0018 | 0.1797 | 10417 | 11688 |
| nz | author_plus_platform | 1995 | 2014 | 0.5038 | 0.0404 | 0.1247 | 8.4243 | 10417 | 11688 |
| nz | exclude_vanity | 1995 | 2014 | 0.5093 | 0.0404 | 0.1259 | 8.5526 | 10417 | 11688 |
| nz | include_mixed_contract_imprints | 1995 | 2014 | 0.5093 | 0.0404 | 0.1259 | 8.5526 | 10417 | 11688 |
| nz | exclude_government_standards | 1995 | 2014 | 0.5319 | 0.0470 | 0.1362 | 8.9187 | 8951 | 10806 |
| nz | exclude_theses | 1995 | 2014 | 0.5100 | 0.0403 | 0.1263 | 8.5990 | 10394 | 11623 |
| nz | exclude_reprints_new_editions | 1995 | 2014 | 0.5230 | 0.0416 | 0.1295 | 8.7932 | 9433 | 10750 |
| nz | exclude_all_four | 1995 | 2014 | 0.5439 | 0.0485 | 0.1404 | 9.1900 | 8057 | 9884 |
| nz | exclude_initials_only_matches | 1995 | 2014 | 0.3722 | 0.0084 | 0.0971 | 8.8756 | 10417 | 11688 |
| nz | include_contributor_matches | 1995 | 2014 | 0.5251 | 0.0404 | 0.1295 | 8.9120 | 10417 | 11688 |
| nz | exclude_unidentified_publishers | 1995 | 2014 | 0.5095 | 0.0404 | 0.1260 | 8.5630 | 10416 | 11678 |
| nz | normalized_title_author_groups | 1995 | 2014 | 0.5484 | 0.0424 | 0.1346 | 9.2173 | 9601 | 10233 |
| fr | main | 2010 | 2021 | 0.6860 | 0.0712 | 0.1429 | 7.1744 | 197327 | 221134 |
| fr | author_only | 2010 | 2021 | 0.4197 | 0.0218 | 0.0602 | 3.8444 | 197327 | 221134 |
| fr | services_only | 2010 | 2021 | 0.2662 | 0.0494 | 0.0827 | 3.3297 | 197327 | 221134 |
| fr | author_plus_platform | 2010 | 2021 | 0.7395 | 0.0244 | 0.0936 | 6.9157 | 197327 | 221134 |
| fr | exclude_vanity | 2010 | 2021 | 0.7047 | 0.0572 | 0.1300 | 7.2735 | 197327 | 221134 |
| fr | include_mixed_contract_imprints | 2010 | 2021 | 0.6860 | 0.0712 | 0.1429 | 7.1744 | 197327 | 221134 |
| fr | exclude_government_standards | 2010 | 2021 | 0.6859 | 0.0713 | 0.1431 | 7.1758 | 196878 | 220863 |
| fr | exclude_theses | 2010 | 2021 | 0.6864 | 0.0712 | 0.1430 | 7.1788 | 197242 | 221027 |
| fr | exclude_reprints_new_editions | 2010 | 2021 | 0.6989 | 0.0772 | 0.1508 | 7.3605 | 179448 | 206325 |
| fr | exclude_all_four | 2010 | 2021 | 0.6993 | 0.0774 | 0.1511 | 7.3681 | 179052 | 205997 |
| fr | exclude_initials_only_matches | 2010 | 2021 | 0.9300 | 0.0508 | 0.1425 | 9.1716 | 197327 | 221134 |
| fr | include_contributor_matches | 2010 | 2021 | 0.6968 | 0.0723 | 0.1449 | 7.2656 | 197327 | 221134 |
| fr | exclude_unidentified_publishers | 2010 | 2021 | 0.6864 | 0.0712 | 0.1429 | 7.1777 | 197309 | 221074 |
| fr | normalized_title_author_groups | 2010 | 2021 | 0.7224 | 0.0832 | 0.1594 | 7.6154 | 167327 | 188448 |
| qc | main | 2010 | 2021 | 0.4465 | 0.0434 | 0.0805 | 3.7100 | 24050 | 18619 |
| qc | author_only | 2010 | 2021 | 0.4352 | 0.0430 | 0.0804 | 3.7408 | 24050 | 18619 |
| qc | services_only | 2010 | 2021 | 0.0113 | 0.0004 | 0.0001 | -0.0308 | 24050 | 18619 |
| qc | author_plus_platform | 2010 | 2021 | 0.4331 | 0.0432 | 0.0804 | 3.7200 | 24050 | 18619 |
| qc | exclude_vanity | 2010 | 2021 | 0.4481 | 0.0433 | 0.0805 | 3.7224 | 24050 | 18619 |
| qc | include_mixed_contract_imprints | 2010 | 2021 | 0.5944 | 0.0434 | 0.0942 | 5.0795 | 24050 | 18619 |
| qc | exclude_government_standards | 2010 | 2021 | 0.4358 | 0.0454 | 0.0814 | 3.6049 | 22995 | 18404 |
| qc | exclude_theses | 2010 | 2021 | 0.4465 | 0.0434 | 0.0805 | 3.7101 | 24046 | 18617 |
| qc | exclude_reprints_new_editions | 2010 | 2021 | 0.4466 | 0.0434 | 0.0805 | 3.7098 | 24042 | 18616 |
| qc | exclude_all_four | 2010 | 2021 | 0.4358 | 0.0454 | 0.0815 | 3.6047 | 22983 | 18399 |
| qc | exclude_initials_only_matches | 2010 | 2021 | 0.7635 | 0.0099 | 0.0803 | 7.0357 | 24050 | 18619 |
| qc | include_contributor_matches | 2010 | 2021 | 0.4627 | 0.0464 | 0.0849 | 3.8552 | 24050 | 18619 |
| qc | exclude_unidentified_publishers | 2010 | 2021 | 0.4470 | 0.0434 | 0.0806 | 3.7134 | 24045 | 18609 |
| qc | normalized_title_author_groups | 2010 | 2021 | 0.4262 | 0.0484 | 0.0833 | 3.4865 | 19103 | 14288 |
| uk | UK_NZ_extension | 1995 | 2017 | 0.1477 | 0.0087 | 0.0307 | 2.2015 | 60454 | 10761 |
| nz | UK_NZ_extension | 1995 | 2017 | 0.5669 | 0.0324 | 0.1494 | 11.7 | 3298 | 3862 |
| uk | common_2010_2013 | 2010 | 2013 | -0.3684 | 0.0329 | 0.0233 | -0.9551 | 70979 | 71317 |
| nz | common_2010_2013 | 2010 | 2013 | 1.1955 | 0.0980 | 0.1356 | 3.7607 | 4010 | 3687 |
| fr | common_2010_2013 | 2010 | 2013 | 1.2744 | 0.0618 | 0.1017 | 3.9939 | 63691 | 68540 |
| qc | common_2010_2013 | 2010 | 2013 | 0.2902 | 0.0382 | 0.0444 | 0.6212 | 7958 | 7025 |
| fr | fr_qc_both_free_2010_2018 | 2010 | 2018 | 0.7835 | 0.0618 | 0.1344 | 7.2629 | 63691 | 76072 |
| qc | fr_qc_both_free_2010_2018 | 2010 | 2018 | 0.4360 | 0.0382 | 0.0707 | 3.2477 | 7958 | 7131 |
| fr | fr_fee_era_2018_2021 | 2018 | 2021 | 0.3919 | 0.1344 | 0.1404 | 0.6029 | 76072 | 77214 |
| qc | fr_fee_era_2018_2021 | 2018 | 2021 | 0.7130 | 0.0707 | 0.0957 | 2.4974 | 7131 | 6461 |
| uk | uk_nz_2005_2011 | 2005 | 2011 | 0.5469 | 0.0092 | 0.0413 | 3.2176 | 54073 | 69627 |
| nz | uk_nz_2005_2011 | 2005 | 2011 | 1.0926 | 0.0459 | 0.1050 | 5.9074 | 3790 | 3591 |

## C3. Sensitivity checks, pooled over each main window

Windows: UK/NZ 1995–2014; FR/QC 2010–2021.

| variant | fr | nz | qc | uk |
|---|---|---|---|---|
| author_only | 0.0375 | 0.0710 | 0.0575 | 0.0078 |
| author_plus_platform | 0.0562 | 0.0712 | 0.0576 | 0.0081 |
| exclude_all_four | 0.1247 | 0.0840 | 0.0607 | 0.0162 |
| exclude_government_standards | 0.1166 | 0.0811 | 0.0606 | 0.0162 |
| exclude_initials_only_matches | 0.1082 | 0.0276 | 0.0493 | 0.0133 |
| exclude_reprints_new_editions | 0.1245 | 0.0737 | 0.0592 | 0.0161 |
| exclude_theses | 0.1165 | 0.0715 | 0.0592 | 0.0160 |
| exclude_unidentified_publishers | 0.1165 | 0.0716 | 0.0592 | 0.0160 |
| exclude_vanity | 0.1033 | 0.0715 | 0.0592 | 0.0160 |
| include_contributor_matches | 0.1181 | 0.0721 | 0.0633 | 0.0170 |
| include_mixed_contract_imprints | 0.1164 | 0.0715 | 0.0657 | 0.0180 |
| main | 0.1164 | 0.0715 | 0.0592 | 0.0160 |
| normalized_title_author_groups | 0.1330 | 0.0772 | 0.0651 | 0.0191 |
| services_only | 0.0790 | 0.0004 | 0.0017 | 0.0082 |

Full year-by-year sensitivity series: `output/selfpub/sensitivity_by_year.csv`.

## C4. Coverage and quality (selected columns)

| source | pub_year | total_records | country_print_records | valid_isbn_share_country_print | publisher_share_country_print | personal_author_share_country_print | raw_isbn_occurrences | duplicate_isbn_occurrences | completeness_status |
|---|---|---|---|---|---|---|---|---|---|
| uk | 1995 | 64285 | 60,489.0 | 0.9158 | 0.9972 | 0.7391 | 65924 | 1956 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 1996 | 66687 | 62,988.0 | 0.9224 | 0.9975 | 0.7403 | 69591 | 1497 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 1997 | 73971 | 68,114.0 | 0.9347 | 0.9987 | 0.7472 | 77827 | 2312 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 1998 | 79924 | 71,562.0 | 0.9341 | 0.9984 | 0.7423 | 83430 | 2464 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 1999 | 86951 | 74,193.0 | 0.9312 | 0.9982 | 0.7460 | 90755 | 3327 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2000 | 91790 | 79,161.0 | 0.9332 | 0.9981 | 0.7446 | 97330 | 4621 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2001 | 91624 | 76,449.0 | 0.9390 | 0.9985 | 0.7492 | 96396 | 7697 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2002 | 89346 | 73,839.0 | 0.9405 | 0.9985 | 0.7464 | 94390 | 3694 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2003 | 92708 | 65,178.0 | 0.9315 | 0.9983 | 0.7419 | 96547 | 1842 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2004 | 86726 | 51,952.0 | 0.9159 | 0.9988 | 0.7495 | 91917 | 963 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2005 | 90485 | 53,279.0 | 0.9258 | 0.9989 | 0.7682 | 96376 | 765 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2006 | 94187 | 54,508.0 | 0.9258 | 0.9987 | 0.7682 | 100144 | 833 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2007 | 107563 | 65,364.0 | 0.9205 | 0.9988 | 0.7597 | 112415 | 861 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2008 | 116366 | 67,248.0 | 0.9223 | 0.9991 | 0.7623 | 121003 | 1082 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2009 | 123277 | 68,770.0 | 0.9270 | 0.9992 | 0.7554 | 127981 | 1264 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2010 | 124426 | 68,192.0 | 0.9333 | 0.9990 | 0.7692 | 129806 | 1304 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2011 | 132764 | 66,839.0 | 0.9417 | 0.9992 | 0.7801 | 137681 | 1336 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2012 | 122496 | 65,041.0 | 0.9518 | 0.9979 | 0.7729 | 129350 | 824 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2013 | 127774 | 67,512.0 | 0.9588 | 0.9982 | 0.7842 | 137157 | 1188 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2014 | 134026 | 68,739.0 | 0.9630 | 0.9983 | 0.7930 | 143520 | 1106 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2015 | 88029 | 41,449.0 | 0.9524 | 0.9985 | 0.7840 | 100726 | 1051 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2016 | 83778 | 33,416.0 | 0.9468 | 0.9978 | 0.7783 | 99587 | 1040 | Not identifiable from one catalogue snapshot; descriptive counts only |
| uk | 2017 | 38425 | 10,901.0 | 0.9171 | 0.9968 | 0.7105 | 50200 | 397 | May 2018 snapshot: 2017–18 vulnerable to lag; later years not usable |
| uk | 2018 | 8194 | 1,001.0 | 0.8731 | 0.9920 | 0.6464 | 11966 | 100 | May 2018 snapshot: 2017–18 vulnerable to lag; later years not usable |
| uk | 2019 | 25 | 0.0000 |  |  |  | 33 | 0 | May 2018 snapshot: 2017–18 vulnerable to lag; later years not usable |
| uk | 2021 | 5 | 0.0000 |  |  |  | 5 | 1 | May 2018 snapshot: 2017–18 vulnerable to lag; later years not usable |
| nz | 1995 | 9031 | 5,658.0 | 0.5716 | 0.9984 | 0.7036 | 4836 | 346 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 1996 | 9272 | 5,830.0 | 0.5600 | 0.9981 | 0.6847 | 4727 | 270 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 1997 | 9176 | 6,006.0 | 0.5986 | 0.9992 | 0.7070 | 4999 | 182 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 1998 | 9586 | 6,134.0 | 0.6146 | 0.9977 | 0.7178 | 5206 | 87 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 1999 | 9334 | 5,951.0 | 0.6071 | 0.9971 | 0.7079 | 4944 | 65 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2000 | 9350 | 5,548.0 | 0.6610 | 0.9948 | 0.7541 | 5179 | 144 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2001 | 9072 | 5,200.0 | 0.6515 | 0.9962 | 0.7329 | 5007 | 160 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2002 | 9426 | 5,290.0 | 0.6698 | 0.9970 | 0.7374 | 5173 | 108 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2003 | 9484 | 5,385.0 | 0.6266 | 0.9991 | 0.7543 | 4903 | 101 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2004 | 10280 | 5,807.0 | 0.6348 | 0.9981 | 0.7667 | 5393 | 38 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2005 | 9904 | 5,709.0 | 0.6234 | 0.9996 | 0.7376 | 5047 | 39 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2006 | 10400 | 5,287.0 | 0.6730 | 0.9987 | 0.7254 | 5304 | 42 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2007 | 11515 | 5,185.0 | 0.6937 | 0.9996 | 0.7161 | 5487 | 55 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2008 | 12448 | 5,277.0 | 0.7169 | 0.9992 | 0.7387 | 6112 | 20 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2009 | 13249 | 4,932.0 | 0.7315 | 0.9994 | 0.7863 | 6160 | 18 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2010 | 13830 | 4,960.0 | 0.7681 | 1.0000 | 0.8042 | 7005 | 28 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2011 | 13179 | 4,388.0 | 0.7464 | 0.9995 | 0.7965 | 6394 | 21 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2012 | 13771 | 4,717.0 | 0.7941 | 0.9992 | 0.8109 | 7876 | 36 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2013 | 12803 | 4,455.0 | 0.7818 | 0.9984 | 0.7957 | 7527 | 86 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2014 | 12786 | 4,767.0 | 0.8062 | 0.9994 | 0.8146 | 7619 | 85 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2015 | 12951 | 4,446.0 | 0.8318 | 0.9987 | 0.8041 | 8084 | 46 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2016 | 11879 | 4,041.0 | 0.8391 | 0.9998 | 0.8203 | 7073 | 97 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2017 | 12314 | 4,308.0 | 0.8763 | 0.9995 | 0.8312 | 7377 | 72 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2018 | 11880 | 3,919.0 | 0.8681 | 0.9997 | 0.8311 | 7108 | 56 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2019 | 11902 | 3,901.0 | 0.8867 | 0.9995 | 0.8441 | 6775 | 69 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2020 | 13225 | 3,147.0 | 0.8990 | 1.0000 | 0.8764 | 6804 | 68 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2021 | 10520 | 2,809.0 | 0.9025 | 0.9996 | 0.8644 | 5896 | 51 | Not identifiable from one catalogue snapshot; descriptive counts only |
| nz | 2022 | 9784 | 2,761.0 | 0.8892 | 1.0000 | 0.8508 | 5855 | 54 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 1995 | 42514 | 40,032.0 | 0.8109 | 0.9998 | 0.7327 | 35777 | 287 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 1996 | 45875 | 43,065.0 | 0.8243 | 0.9998 | 0.7377 | 38977 | 288 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 1997 | 47484 | 44,974.0 | 0.8527 | 0.9999 | 0.7480 | 41651 | 291 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 1998 | 50287 | 47,505.0 | 0.8826 | 0.9998 | 0.7524 | 45536 | 290 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 1999 | 51243 | 48,525.0 | 0.8955 | 0.9998 | 0.7546 | 47103 | 301 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2000 | 52054 | 48,133.0 | 0.9040 | 0.9995 | 0.7570 | 46920 | 264 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2001 | 52529 | 49,715.0 | 0.9015 | 0.9996 | 0.7570 | 48489 | 213 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2002 | 53372 | 50,333.0 | 0.9186 | 0.9999 | 0.7752 | 50144 | 202 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2003 | 53969 | 50,928.0 | 0.9181 | 0.9999 | 0.7843 | 50647 | 172 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2004 | 57516 | 54,298.0 | 0.9246 | 1.0000 | 0.7887 | 54408 | 199 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2005 | 59930 | 56,604.0 | 0.9300 | 0.9997 | 0.7997 | 56965 | 236 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2006 | 61903 | 58,009.0 | 0.9323 | 0.9998 | 0.8025 | 59172 | 268 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2007 | 64573 | 60,605.0 | 0.9386 | 0.9999 | 0.8098 | 61982 | 218 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2008 | 66530 | 62,258.0 | 0.9443 | 0.9998 | 0.8127 | 64256 | 229 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2009 | 66159 | 62,250.0 | 0.9471 | 0.9999 | 0.8184 | 64065 | 238 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2010 | 69350 | 65,794.0 | 0.9555 | 0.9999 | 0.8208 | 67611 | 175 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2011 | 71595 | 68,025.0 | 0.9583 | 1.0000 | 0.8289 | 70074 | 204 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2012 | 73181 | 69,829.0 | 0.9557 | 0.9999 | 0.8238 | 73196 | 163 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2013 | 73322 | 70,412.0 | 0.9598 | 0.9999 | 0.8295 | 75389 | 224 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2014 | 74315 | 71,338.0 | 0.9633 | 1.0000 | 0.8370 | 72736 | 222 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2015 | 77304 | 74,034.0 | 0.9678 | 0.9999 | 0.8394 | 75909 | 135 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2016 | 77315 | 73,845.0 | 0.9761 | 0.9999 | 0.8458 | 76450 | 164 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2017 | 75992 | 72,275.0 | 0.9758 | 0.9997 | 0.8411 | 75120 | 148 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2018 | 80945 | 77,091.0 | 0.9771 | 0.9999 | 0.8531 | 80111 | 105 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2019 | 80382 | 76,838.0 | 0.9706 | 0.9999 | 0.8506 | 79097 | 98 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2020 | 72758 | 69,721.0 | 0.9763 | 1.0000 | 0.8660 | 71784 | 91 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2021 | 82333 | 78,709.0 | 0.9764 | 1.0000 | 0.8679 | 81082 | 83 | Not identifiable from one catalogue snapshot; descriptive counts only |
| fr | 2022 | 67296 | 63,966.0 | 0.9788 | 1.0000 | 0.8502 | 66336 | 51 | Not identifiable from one catalogue snapshot; descriptive counts only |
| qc | 2010 | 15088 | 8,054.0 | 0.9998 | 1.0000 | 0.7636 | 15052 | 205 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2011 | 15709 | 8,089.0 | 1.0000 | 1.0000 | 0.7809 | 15672 | 172 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2012 | 16887 | 8,186.0 | 0.9995 | 1.0000 | 0.8091 | 16843 | 160 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2013 | 16180 | 7,087.0 | 0.9996 | 1.0000 | 0.8139 | 16130 | 91 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2014 | 17955 | 7,975.0 | 0.9991 | 1.0000 | 0.8317 | 17833 | 83 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2015 | 17208 | 7,230.0 | 0.9997 | 1.0000 | 0.8491 | 17129 | 102 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2016 | 17038 | 7,476.0 | 0.9996 | 1.0000 | 0.8567 | 16985 | 108 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2017 | 17830 | 7,462.0 | 0.9997 | 1.0000 | 0.8558 | 17779 | 154 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2018 | 18231 | 7,200.0 | 1.0000 | 1.0000 | 0.8561 | 18189 | 131 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2019 | 19452 | 8,287.0 | 0.9993 | 1.0000 | 0.8755 | 19398 | 1883 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2020 | 17496 | 7,111.0 | 0.9997 | 0.9997 | 0.8785 | 17443 | 2053 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2021 | 18984 | 8,454.0 | 0.9985 | 0.9991 | 0.9132 | 18928 | 2167 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |
| qc | 2022 | 18500 | 7,753.0 | 0.9997 | 1.0000 | 0.9052 | 18462 | 2035 | ISBN-only CSV; strict subset with matched 2010–24 bibliography and identifiable Québec place |

## C5. Amazon-issued ISBNs, 979-8 and NZ pool context

| source | pub_year | print_isbns | amazon_imprint | us_9798_not_amazon_proof | both_amazon_and_9798 | nz_pool | nz_pool_flagged | other_prefix_flagged |
|---|---|---|---|---|---|---|---|---|
| uk | 1995 | 60454 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 523.0 |
| uk | 1996 | 64457 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 489.0 |
| uk | 1997 | 69551 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 519.0 |
| uk | 1998 | 72672 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 526.0 |
| uk | 1999 | 75420 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 580.0 |
| uk | 2000 | 80979 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 556.0 |
| uk | 2001 | 74663 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 393.0 |
| uk | 2002 | 74689 | 1.0000 | 0.0000 | 0.0000 | 2.0000 | 0.0000 | 393.0 |
| uk | 2003 | 66761 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 452.0 |
| uk | 2004 | 52676 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 470.0 |
| uk | 2005 | 54073 | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 496.0 |
| uk | 2006 | 55747 | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 609.0 |
| uk | 2007 | 66619 | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,188.0 |
| uk | 2008 | 67797 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,685.0 |
| uk | 2009 | 70117 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 2,140.0 |
| uk | 2010 | 70979 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 2,333.0 |
| uk | 2011 | 69627 | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2,879.0 |
| uk | 2012 | 68935 | 35.0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2,286.0 |
| uk | 2013 | 71317 | 7.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,664.0 |
| uk | 2014 | 70636 | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,571.0 |
| uk | 2015 | 42750 | 11.0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,272.0 |
| uk | 2016 | 34052 | 8.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,152.0 |
| uk | 2017 | 10761 | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 330.0 |
| uk | 2018 | 906 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 34.0 |
| nz | 1995 | 3298 | 0.0000 | 0.0000 | 0.0000 | 481.0 | 92.0 | 15.0 |
| nz | 1996 | 3347 | 0.0000 | 0.0000 | 0.0000 | 538.0 | 113.0 | 36.0 |
| nz | 1997 | 3772 | 0.0000 | 0.0000 | 0.0000 | 602.0 | 126.0 | 39.0 |
| nz | 1998 | 3983 | 0.0000 | 0.0000 | 0.0000 | 589.0 | 105.0 | 117.0 |
| nz | 1999 | 3772 | 0.0000 | 0.0000 | 0.0000 | 630.0 | 132.0 | 34.0 |
| nz | 2000 | 3834 | 0.0000 | 0.0000 | 0.0000 | 639.0 | 132.0 | 44.0 |
| nz | 2001 | 3618 | 0.0000 | 0.0000 | 0.0000 | 667.0 | 151.0 | 26.0 |
| nz | 2002 | 3749 | 0.0000 | 0.0000 | 0.0000 | 708.0 | 144.0 | 29.0 |
| nz | 2003 | 3531 | 0.0000 | 0.0000 | 0.0000 | 554.0 | 113.0 | 47.0 |
| nz | 2004 | 3897 | 0.0000 | 0.0000 | 0.0000 | 64.0 | 11.0 | 166.0 |
| nz | 2005 | 3790 | 0.0000 | 0.0000 | 0.0000 | 480.0 | 90.0 | 84.0 |
| nz | 2006 | 3748 | 0.0000 | 0.0000 | 0.0000 | 760.0 | 173.0 | 26.0 |
| nz | 2007 | 3778 | 0.0000 | 0.0000 | 0.0000 | 836.0 | 207.0 | 83.0 |
| nz | 2008 | 4062 | 0.0000 | 0.0000 | 0.0000 | 989.0 | 266.0 | 99.0 |
| nz | 2009 | 3779 | 0.0000 | 0.0000 | 0.0000 | 1,092.0 | 357.0 | 80.0 |
| nz | 2010 | 4010 | 0.0000 | 0.0000 | 0.0000 | 1,198.0 | 329.0 | 64.0 |
| nz | 2011 | 3591 | 0.0000 | 0.0000 | 0.0000 | 1,192.0 | 326.0 | 51.0 |
| nz | 2012 | 4028 | 2.0000 | 0.0000 | 0.0000 | 1,231.0 | 377.0 | 73.0 |
| nz | 2013 | 3687 | 0.0000 | 0.0000 | 0.0000 | 1,283.0 | 382.0 | 118.0 |
| nz | 2014 | 3973 | 0.0000 | 0.0000 | 0.0000 | 1,406.0 | 391.0 | 131.0 |
| nz | 2015 | 3845 | 1.0000 | 0.0000 | 0.0000 | 1,433.0 | 395.0 | 120.0 |
| nz | 2016 | 3528 | 3.0000 | 0.0000 | 0.0000 | 1,421.0 | 431.0 | 142.0 |
| nz | 2017 | 3862 | 0.0000 | 0.0000 | 0.0000 | 1,702.0 | 471.0 | 106.0 |
| nz | 2018 | 3533 | 0.0000 | 1.0000 | 0.0000 | 1,621.0 | 438.0 | 96.0 |
| nz | 2019 | 3587 | 0.0000 | 1.0000 | 0.0000 | 1,641.0 | 488.0 | 72.0 |
| nz | 2020 | 2948 | 0.0000 | 37.0 | 0.0000 | 1,682.0 | 590.0 | 48.0 |
| nz | 2021 | 2695 | 0.0000 | 24.0 | 0.0000 | 1,360.0 | 463.0 | 46.0 |
| nz | 2022 | 2715 | 0.0000 | 33.0 | 0.0000 | 1,287.0 | 489.0 | 48.0 |
| fr | 1995 | 32676 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 399.0 |
| fr | 1996 | 35688 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 540.0 |
| fr | 1997 | 38661 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 586.0 |
| fr | 1998 | 42301 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 625.0 |
| fr | 1999 | 43908 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 643.0 |
| fr | 2000 | 44038 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 596.0 |
| fr | 2001 | 45384 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 598.0 |
| fr | 2002 | 46938 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 616.0 |
| fr | 2003 | 47505 | 0.0000 | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 681.0 |
| fr | 2004 | 50989 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 792.0 |
| fr | 2005 | 53343 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,477.0 |
| fr | 2006 | 54873 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1,640.0 |
| fr | 2007 | 57657 | 0.0000 | 0.0000 | 0.0000 | 2.0000 | 0.0000 | 2,335.0 |
| fr | 2008 | 59560 | 1.0000 | 0.0000 | 0.0000 | 2.0000 | 0.0000 | 2,954.0 |
| fr | 2009 | 59790 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3,478.0 |
| fr | 2010 | 63691 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3,935.0 |
| fr | 2011 | 66068 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 4,741.0 |
| fr | 2012 | 67568 | 0.0000 | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 5,364.0 |
| fr | 2013 | 68540 | 2.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 6,972.0 |
| fr | 2014 | 69310 | 2.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 10,139.0 |
| fr | 2015 | 72342 | 2.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 10,786.0 |
| fr | 2016 | 72678 | 5.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 8,710.0 |
| fr | 2017 | 71110 | 5.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 6,318.0 |
| fr | 2018 | 76072 | 2.0000 | 5.0000 | 0.0000 | 0.0000 | 0.0000 | 10,225.0 |
| fr | 2019 | 75351 | 1.0000 | 13.0 | 0.0000 | 0.0000 | 0.0000 | 10,109.0 |
| fr | 2020 | 68569 | 7.0000 | 1,229.0 | 2.0000 | 0.0000 | 0.0000 | 10,646.0 |
| fr | 2021 | 77214 | 1.0000 | 1,668.0 | 1.0000 | 0.0000 | 0.0000 | 10,844.0 |
| fr | 2022 | 62928 | 1.0000 | 754.0 | 1.0000 | 0.0000 | 0.0000 | 4,192.0 |
| qc | 2010 | 7958 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 304.0 |
| qc | 2011 | 7976 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 325.0 |
| qc | 2012 | 8116 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 415.0 |
| qc | 2013 | 7025 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 312.0 |
| qc | 2014 | 7902 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 381.0 |
| qc | 2015 | 7155 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 376.0 |
| qc | 2016 | 7405 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 481.0 |
| qc | 2017 | 7385 | 0.0000 | 9.0000 | 0.0000 | 0.0000 | 0.0000 | 537.0 |
| qc | 2018 | 7131 | 0.0000 | 5.0000 | 0.0000 | 0.0000 | 0.0000 | 504.0 |
| qc | 2019 | 6764 | 0.0000 | 19.0 | 0.0000 | 0.0000 | 0.0000 | 501.0 |
| qc | 2020 | 5394 | 0.0000 | 59.0 | 0.0000 | 0.0000 | 0.0000 | 380.0 |
| qc | 2021 | 6461 | 0.0000 | 59.0 | 0.0000 | 0.0000 | 0.0000 | 618.0 |
| qc | 2022 | 5977 | 1.0000 | 60.0 | 1.0000 | 0.0000 | 0.0000 | 464.0 |

## C6. Amazon-issued ISBNs: Amazon sample vs national bibliographies

| pub_year | amazon_sample_createspace_or_indep | nb_uk | nb_us | nb_nz | nb_fr | nb_qc |
|---|---|---|---|---|---|---|
| 2008 | 2,722.0 | 0.0000 | 32.0 | 0.0000 | 1.0000 |  |
| 2009 | 5,417.0 | 0.0000 | 52.0 | 0.0000 | 0.0000 |  |
| 2010 | 7,782.0 | 0.0000 | 29.0 | 0.0000 | 0.0000 | 0.0000 |
| 2011 | 12,842.0 | 2.0000 | 50.0 | 0.0000 | 0.0000 | 0.0000 |
| 2012 | 24,169.0 | 35.0 | 57.0 | 2.0000 | 0.0000 | 0.0000 |
| 2013 | 32,019.0 | 7.0000 | 55.0 | 0.0000 | 2.0000 | 0.0000 |
| 2014 | 38,363.0 | 3.0000 | 33.0 | 0.0000 | 2.0000 | 1.0000 |
| 2015 | 42,164.0 | 11.0 | 2.0000 | 1.0000 | 2.0000 | 0.0000 |
| 2016 | 46,644.0 | 8.0000 | 0.0000 | 3.0000 | 5.0000 | 0.0000 |
| 2017 | 53,703.0 | 2.0000 | 0.0000 | 0.0000 | 5.0000 | 0.0000 |
| 2018 | 51,028.0 | 0.0000 | 0.0000 | 0.0000 | 2.0000 | 0.0000 |

## C7. Unknown-breakpoint tests (sup-F, bootstrap p)

| country | outcome | window | break_year | supF | boot_p |
|---|---|---|---|---|---|
| NZ | ap | 1995-2019 | 2007 | 22.8 | 0.0010 |
| NZ | sp | 1995-2019 | 2007 | 23.0 | 0.0010 |
| UK | ap | 1995-2014 | 2001 | 34.3 | 0.0010 |
| UK | sp | 1995-2014 | 2007 | 14.4 | 0.0040 |
| US (LoC) | ap | 1995-2011 | 2003 | 9.4868 | 0.0350 |
| US (LoC) | sp | 1995-2011 | 2004 | 23.0 | 0.0010 |
| France | ap | 2005-2018 | 2009 | 6.6839 | 0.1119 |
| France | sp | 2005-2018 | 2014 | 12.7 | 0.0250 |
| Québec | ap | 2010-2018 | 2013 | 3.9503 | 0.3467 |
| Québec | sp | 2010-2018 | 2013 | 3.7939 | 0.3247 |

## C8. NZ minus UK interrupted time series on the log-odds gap

| outcome | break_year | pre_gap_slope | level_shift | slope_change | slope_change_se_NW | slope_change_p_NW | rank_among_placebos |
|---|---|---|---|---|---|---|---|
| ap | 2007 | 0.0415 | 0.2171 | -0.0152 | 0.0270 | 0.5747 | 4 |
| ap | 2008 | 0.0443 | 0.2516 | -0.0369 | 0.0220 | 0.0944 | 11 |
| ap | 2009 | 0.0467 | 0.3019 | -0.0727 | 0.0234 | 0.0019 | 11 |
| sp | 2007 | 0.0054 | -0.6341 | 0.0507 | 0.0411 | 0.2176 | 3 |
| sp | 2008 | -0.0064 | -0.6307 | 0.1019 | 0.0434 | 0.0188 | 1 |
| sp | 2009 | -0.0184 | -0.5485 | 0.1559 | 0.0495 | 0.0016 | 0 |

## C9. Pooled difference-in-differences around 2007/08

| comparison | window | outcome | break_year | country_trends | log_odds_ratio | odds_ratio | se_cluster_year | p_cluster | boot_ci_low_or | boot_ci_high_or |
|---|---|---|---|---|---|---|---|---|---|---|
| NZ vs UK | 1995-2014 | ap | 2007 | False | 0.5823 | 1.7902 | 0.1326 | 0.0000 | 1.5413 | 2.1001 |
| NZ vs UK | 1995-2014 | ap | 2007 | True | 0.2510 | 1.2853 | 0.2252 | 0.2649 |  |  |
| NZ vs UK | 1995-2014 | ap | 2008 | False | 0.5697 | 1.7678 | 0.1360 | 0.0000 | 1.5264 | 2.1341 |
| NZ vs UK | 1995-2014 | ap | 2008 | True | 0.2262 | 1.2538 | 0.2256 | 0.3162 |  |  |
| NZ vs UK | 1995-2014 | sp | 2007 | False | -0.4107 | 0.6632 | 0.1949 | 0.0351 | 0.5204 | 0.8411 |
| NZ vs UK | 1995-2014 | sp | 2007 | True | -0.6513 | 0.5214 | 0.3488 | 0.0618 |  |  |
| NZ vs UK | 1995-2014 | sp | 2008 | False | -0.3749 | 0.6874 | 0.2094 | 0.0735 | 0.5142 | 0.9462 |
| NZ vs UK | 1995-2014 | sp | 2008 | True | -0.4785 | 0.6197 | 0.3302 | 0.1473 |  |  |
| NZ vs US(LoC) | 1995-2011 | ap | 2007 | False | 1.0904 | 2.9754 | 0.1638 | 0.0000 | 2.3175 | 3.6109 |
| NZ vs US(LoC) | 1995-2011 | ap | 2007 | True | 0.7530 | 2.1234 | 0.2386 | 0.0016 |  |  |
| NZ vs US(LoC) | 1995-2011 | ap | 2008 | False | 1.1249 | 3.0798 | 0.1337 | 0.0000 | 2.4050 | 3.6202 |
| NZ vs US(LoC) | 1995-2011 | ap | 2008 | True | 0.7059 | 2.0258 | 0.2574 | 0.0061 |  |  |
| NZ vs US(LoC) | 1995-2011 | sp | 2007 | False | 0.2223 | 1.2489 | 0.2596 | 0.3919 | 0.8643 | 1.7173 |
| NZ vs US(LoC) | 1995-2011 | sp | 2007 | True | 0.9920 | 2.6966 | 0.3694 | 0.0072 |  |  |
| NZ vs US(LoC) | 1995-2011 | sp | 2008 | False | 0.2844 | 1.3289 | 0.2319 | 0.2201 | 0.9780 | 1.7643 |
| NZ vs US(LoC) | 1995-2011 | sp | 2008 | True | 0.9659 | 2.6271 | 0.4068 | 0.0176 |  |  |
| NZ vs UK+US(LoC) | 1995-2011 | ap | 2007 | False | 0.7674 | 2.1542 | 0.1255 | 0.0000 | 1.7441 | 2.6592 |
| NZ vs UK+US(LoC) | 1995-2011 | ap | 2007 | True | 0.3671 | 1.4436 | 0.1580 | 0.0202 |  |  |
| NZ vs UK+US(LoC) | 1995-2011 | ap | 2008 | False | 0.7790 | 2.1793 | 0.1252 | 0.0000 | 1.6696 | 2.6851 |
| NZ vs UK+US(LoC) | 1995-2011 | ap | 2008 | True | 0.3548 | 1.4259 | 0.1584 | 0.0251 |  |  |
| NZ vs UK+US(LoC) | 1995-2011 | sp | 2007 | False | -0.1443 | 0.8656 | 0.1444 | 0.3176 | 0.6954 | 1.0563 |
| NZ vs UK+US(LoC) | 1995-2011 | sp | 2007 | True | 0.4340 | 1.5434 | 0.1962 | 0.0270 |  |  |
| NZ vs UK+US(LoC) | 1995-2011 | sp | 2008 | False | -0.1271 | 0.8807 | 0.1284 | 0.3225 | 0.7034 | 1.0553 |
| NZ vs UK+US(LoC) | 1995-2011 | sp | 2008 | True | 0.3667 | 1.4429 | 0.2003 | 0.0672 |  |  |

## C10. France vs Québec: parallel trends and post-2019 tests

| outcome | label | gap_2010 | gap_2018 | pre_slope_gap_per_year | pre_slope_se_NW | pre_slope_p_NW | pre_slope_p_perm | pre_resid_sd | comovement_r_pre | post_dev_2019 | post_dev_2020 | post_dev_2021 | post_dev_mean | post_dev_in_pre_sd | level_shift_2019 | level_shift_p_NW | slope_change | slope_change_p_NW |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ap | author=publisher only | -0.6519 | -0.5102 | 0.0206 | 0.0049 | 0.0041 | 0.0833 | 0.0833 | -0.1020 | 0.0541 | 0.4223 | 0.0541 | 0.1768 | 2.1221 | 0.1768 | 0.0823 | 0.0000 | 0.9996 |
| sp | combined (main) | 0.5056 | 0.7138 | 0.0059 | 0.0331 | 0.8627 | 0.8953 | 0.3460 | -0.5744 | -0.0839 | 0.1349 | -0.3220 | -0.0904 | -0.2612 | 0.0287 | 0.8942 | -0.1191 | 0.1755 |
| svc_only | services only | 5.8440 | 3.1315 | -0.3975 | 0.0841 | 0.0021 | 0.0217 | 0.9896 | -0.0894 | inf | inf | 4.0130 | inf | inf | inf |  |  |  |

### Yearly France−Québec log-odds gap

| pub_year | gap_logodds_ap | gap_logodds_sp | gap_logodds_svc_only |
|---|---|---|---|
| 2010 | -0.6519 | 0.5056 | 5.8440 |
| 2011 | -0.6040 | 0.5988 | 4.2365 |
| 2012 | -0.8285 | 0.4701 | 5.0885 |
| 2013 | -0.5810 | 0.8906 | 6.3657 |
| 2014 | -0.5735 | 1.2186 | 5.3619 |
| 2015 | -0.5189 | 1.1503 | 3.8258 |
| 2016 | -0.6165 | 0.6730 | 3.0196 |
| 2017 | -0.5436 | 0.2179 | 2.1298 |
| 2018 | -0.5102 | 0.7138 | 3.1315 |
| 2019 | -0.4462 | 0.6611 |  |
| 2020 | -0.0574 | 0.8859 |  |
| 2021 | -0.4050 | 0.4349 | 5.5644 |

### Author=publisher entry in France and Québec

| source | pub_year | isbns | pubs | titles | entrants | isbn_per_pub | isbn_per_title |
|---|---|---|---|---|---|---|---|
| fr | 2010 | 1283 | 1003 | 1244 | 745 | 1.2792 | 1.0314 |
| fr | 2011 | 1469 | 1153 | 1443 | 824 | 1.2741 | 1.0180 |
| fr | 2012 | 1542 | 1195 | 1529 | 815 | 1.2904 | 1.0085 |
| fr | 2013 | 1731 | 1360 | 1703 | 916 | 1.2728 | 1.0164 |
| fr | 2014 | 1897 | 1481 | 1858 | 1097 | 1.2809 | 1.0210 |
| fr | 2015 | 2180 | 1570 | 2109 | 1389 | 1.3885 | 1.0337 |
| fr | 2016 | 2436 | 1874 | 2382 | 1443 | 1.2999 | 1.0227 |
| fr | 2017 | 2830 | 2051 | 2764 | 1444 | 1.3798 | 1.0239 |
| fr | 2018 | 3105 | 2232 | 3027 | 1479 | 1.3911 | 1.0258 |
| fr | 2019 | 3670 | 2624 | 3577 | 1744 | 1.3986 | 1.0260 |
| fr | 2020 | 4574 | 3172 | 4463 | 2175 | 1.4420 | 1.0249 |
| fr | 2021 | 5070 | 3535 | 4902 | 2352 | 1.4342 | 1.0343 |
| qc | 2010 | 303 | 228 | 274 | 228 | 1.3289 | 1.1058 |
| qc | 2011 | 319 | 242 | 292 | 209 | 1.3182 | 1.0925 |
| qc | 2012 | 412 | 305 | 354 | 262 | 1.3508 | 1.1638 |
| qc | 2013 | 311 | 246 | 287 | 233 | 1.2642 | 1.0836 |
| qc | 2014 | 376 | 263 | 340 | 235 | 1.4297 | 1.1059 |
| qc | 2015 | 355 | 266 | 313 | 215 | 1.3346 | 1.1342 |
| qc | 2016 | 447 | 331 | 402 | 279 | 1.3505 | 1.1119 |
| qc | 2017 | 492 | 373 | 435 | 291 | 1.3190 | 1.1310 |
| qc | 2018 | 472 | 336 | 420 | 252 | 1.4048 | 1.1238 |
| qc | 2019 | 501 | 330 | 436 | 257 | 1.5182 | 1.1491 |
| qc | 2020 | 380 | 257 | 292 | 198 | 1.4786 | 1.3014 |
| qc | 2021 | 616 | 442 | 500 | 340 | 1.3937 | 1.2320 |

## C11. Per-capita author=publisher rates

| pub_year | fr | nz | qc | uk | us |
|---|---|---|---|---|---|
| 1995 | 5.6552 | 29.2 |  | 9.0000 | 1.0364 |
| 1996 | 7.5556 | 40.2 |  | 8.3534 | 1.1838 |
| 1997 | 8.6271 | 44.0 |  | 8.8417 | 1.1223 |
| 1998 | 9.2101 | 58.7 |  | 8.9341 | 1.1782 |
| 1999 | 9.1333 | 43.4 |  | 9.7582 | 1.0895 |
| 2000 | 8.1818 | 45.6 |  | 9.2020 | 1.0312 |
| 2001 | 7.9948 | 45.0 |  | 6.3345 | 1.0005 |
| 2002 | 8.3469 | 43.6 |  | 5.9832 | 1.0538 |
| 2003 | 8.3870 | 39.8 |  | 6.4047 | 1.1889 |
| 2004 | 10.3 | 43.2 |  | 6.2895 | 1.0962 |
| 2005 | 11.7 | 41.9 |  | 5.8609 | 1.1404 |
| 2006 | 11.3 | 46.9 |  | 6.3403 | 0.9522 |
| 2007 | 12.8 | 67.9 |  | 8.7679 | 0.9534 |
| 2008 | 13.6 | 85.4 |  | 9.9288 | 0.8065 |
| 2009 | 15.4 | 100.9 |  | 8.8094 | 0.8156 |
| 2010 | 19.9 | 89.5 | 38.4 | 9.8567 | 0.7436 |
| 2011 | 22.6 | 85.4 | 40.1 | 8.8207 | 0.7029 |
| 2012 | 23.6 | 98.8 | 51.4 | 12.6 | 0.5926 |
| 2013 | 26.4 | 110.5 | 38.5 | 11.7 | 0.3891 |
| 2014 | 28.7 | 112.4 | 46.2 | 12.1 | 0.2481 |
| 2015 | 32.8 | 105.7 | 43.3 | 8.2642 | 0.0655 |
| 2016 | 36.6 | 116.4 | 54.0 | 7.6031 | 0.0062 |
| 2017 | 42.4 | 115.9 | 58.9 | 3.4446 | 0.0000 |
| 2018 | 46.3 | 105.4 | 55.9 | 0.3469 | 0.0000 |
| 2019 | 54.6 | 108.6 | 58.8 |  | 0.0000 |
| 2020 | 67.9 | 121.6 | 44.2 |  |  |
| 2021 | 75.2 | 94.9 | 71.6 |  |  |
| 2022 | 31.8 | 100.8 | 53.8 |  |  |

## C12. Author=publisher entry, NZ/UK/US(LoC)

| source | pub_year | pubs | titles | isbns | entrants | titles_per_pub |
|---|---|---|---|---|---|---|
| nz | 2000 | 152 | 166 | 176 | 118 | 1.0921 |
| nz | 2001 | 158 | 172 | 176 | 129 | 1.0886 |
| nz | 2002 | 152 | 169 | 173 | 122 | 1.1118 |
| nz | 2003 | 142 | 157 | 160 | 111 | 1.1056 |
| nz | 2004 | 161 | 172 | 176 | 126 | 1.0683 |
| nz | 2005 | 165 | 171 | 173 | 131 | 1.0364 |
| nz | 2006 | 174 | 189 | 196 | 139 | 1.0862 |
| nz | 2007 | 251 | 276 | 287 | 197 | 1.0996 |
| nz | 2008 | 303 | 351 | 365 | 241 | 1.1584 |
| nz | 2009 | 362 | 429 | 436 | 273 | 1.1851 |
| nz | 2010 | 316 | 377 | 391 | 258 | 1.1930 |
| nz | 2011 | 323 | 361 | 377 | 248 | 1.1176 |
| nz | 2012 | 364 | 421 | 441 | 279 | 1.1566 |
| nz | 2013 | 380 | 475 | 498 | 344 | 1.2500 |
| nz | 2014 | 403 | 487 | 512 | 330 | 1.2084 |
| nz | 2015 | 398 | 462 | 486 | 326 | 1.1608 |
| nz | 2016 | 428 | 524 | 547 | 322 | 1.2243 |
| nz | 2017 | 464 | 541 | 556 | 347 | 1.1659 |
| nz | 2018 | 414 | 494 | 516 | 307 | 1.1932 |
| nz | 2019 | 425 | 498 | 542 | 317 | 1.1718 |
| nz | 2020 | 501 | 588 | 619 | 379 | 1.1737 |
| nz | 2021 | 398 | 446 | 483 | 285 | 1.1206 |
| nz | 2022 | 420 | 476 | 513 | 291 | 1.1333 |
| uk | 2000 | 401 | 523 | 542 | 310 | 1.3042 |
| uk | 2001 | 306 | 366 | 375 | 214 | 1.1961 |
| uk | 2002 | 308 | 349 | 356 | 204 | 1.1331 |
| uk | 2003 | 331 | 373 | 383 | 235 | 1.1269 |
| uk | 2004 | 302 | 367 | 378 | 231 | 1.2152 |
| uk | 2005 | 304 | 342 | 354 | 224 | 1.1250 |
| uk | 2006 | 308 | 370 | 386 | 212 | 1.2013 |
| uk | 2007 | 462 | 530 | 538 | 342 | 1.1472 |
| uk | 2008 | 467 | 579 | 614 | 341 | 1.2398 |
| uk | 2009 | 455 | 533 | 549 | 351 | 1.1714 |
| uk | 2010 | 484 | 604 | 619 | 369 | 1.2479 |
| uk | 2011 | 471 | 545 | 558 | 348 | 1.1571 |
| uk | 2012 | 528 | 713 | 803 | 405 | 1.3504 |
| uk | 2013 | 592 | 729 | 748 | 450 | 1.2314 |
| uk | 2014 | 602 | 748 | 783 | 455 | 1.2425 |
| uk | 2015 | 439 | 525 | 538 | 311 | 1.1959 |
| uk | 2016 | 422 | 488 | 498 | 310 | 1.1564 |
| uk | 2017 | 192 | 219 | 227 | 142 | 1.1406 |
| uk | 2018 | 20 | 21 | 23 | 12 | 1.0500 |
| us | 2000 | 264 | 274 | 291 | 231 | 1.0379 |
| us | 2001 | 240 | 252 | 285 | 209 | 1.0500 |
| us | 2002 | 267 | 282 | 303 | 231 | 1.0562 |
| us | 2003 | 302 | 315 | 345 | 268 | 1.0430 |
| us | 2004 | 280 | 287 | 321 | 248 | 1.0250 |
| us | 2005 | 307 | 319 | 337 | 266 | 1.0391 |
| us | 2006 | 245 | 263 | 284 | 211 | 1.0735 |
| us | 2007 | 257 | 265 | 287 | 231 | 1.0311 |
| us | 2008 | 216 | 230 | 245 | 191 | 1.0648 |
| us | 2009 | 220 | 238 | 250 | 194 | 1.0818 |
| us | 2010 | 208 | 215 | 230 | 190 | 1.0337 |
| us | 2011 | 187 | 193 | 219 | 167 | 1.0321 |
| us | 2012 | 168 | 174 | 186 | 151 | 1.0357 |
| us | 2013 | 115 | 118 | 123 | 98 | 1.0261 |
| us | 2014 | 74 | 75 | 79 | 61 | 1.0135 |
| us | 2015 | 18 | 19 | 21 | 16 | 1.0556 |
| us | 2016 | 2 | 2 | 2 | 2 | 1.0000 |

## C13. BnF official benchmark vs our France series

| pub_year | bnf_author_depositor_share | our_ap_share | our_combined_share |
|---|---|---|---|
| 2009 | 0.0316 | 0.0165 | 0.0582 |
| 2010 | 0.0456 | 0.0202 | 0.0618 |
| 2011 | 0.0419 | 0.0223 | 0.0718 |
| 2012 | 0.0440 | 0.0228 | 0.0794 |
| 2013 | 0.0474 | 0.0253 | 0.1017 |
| 2014 | 0.0471 | 0.0274 | 0.1463 |
| 2015 | 0.0505 | 0.0301 | 0.1491 |
| 2016 | 0.0556 | 0.0335 | 0.1198 |
| 2017 | 0.0550 | 0.0398 | 0.0888 |
| 2018 | 0.0579 | 0.0408 | 0.1344 |
| 2019 | 0.0702 | 0.0487 | 0.1342 |
| 2020 | 0.1095 | 0.0668 | 0.1553 |

Correlation 2009–2020: AP vs BnF 0.96; combined vs BnF 0.65.

## C14. Validation

Record-only read of 25 flagged and 25 unflagged ISBNs per source (not independent, no web lookups): flagged — no clear false positives, about 5 borderline sole-trader/company imprints; unflagged — UK/FR almost all real publishers, NZ/QC a few likely misses (pseudonyms, small imprints). Full 200+200 samples with blank gold-label columns: `output/selfpub/validation_{uk,nz,fr,qc}.csv`. NZ pool check: flag rate inside the 978-0-473/978-1-06 pool is 27–38%, outside 2–7%.

## C15. Source totals

| source | raw_records | classified_isbns |
|---|---|---|
| uk | 3661618 | 1446638 |
| nz | 613748 | 101960 |
| fr | 2780793 | 1624752 |
| qc | 291392 | 92649 |

## C16. File index

All under `output/selfpub/`: all_by_year, uk_nz_by_year, fr_qc_by_year, sensitivity_by_year, trends_and_early_late, coverage, amazon_and_nz_prefix_context, amazon_issued_capture, break_tests, nz_uk_its, did_amazon_era, frqc_parallel_trends_did, frqc_gap_series, frqc_author_publisher_entry, per_capita, panel, ap_entry_nz_uk_us, uk_service_place_sensitivity, bnf_official_benchmarks, publisher_candidates_*, duplicates_*, validation_*, figures/*.
