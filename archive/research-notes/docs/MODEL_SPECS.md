# MODEL_SPECS: definitions, models and the causal claims they can carry

## Definitions that the figures depend on

- **AP = "author = publisher".** NOT Amazon Publishing. A print ISBN is AP when a personal author's normalised name equals, or is contained in, the publisher string (initials and surname+family/trust variants included), or the publisher field says "the author / à compte d'auteur / auto-édition". Corporate author = publisher is excluded (`corporate_self`).
- **Combined / "self-published" (sp)** = AP OR service imprint (a publisher string matching `config/selfpub_services.csv`, e.g. AuthorHouse, Xlibris, CreateSpace, "Independently published", Lulu, BoD, Édilivre).
- **Denominator** = distinct valid ISBN-13s of print books, one row per ISBN, in the national catalogue for the stated country and year: not "all ISBNs issued" and not new titles. Excludes ebooks, audio, music, maps, serials, microforms. Includes reprints, new editions, government publications and standards unless a sensitivity variant says otherwise. So every share is "share of catalogued print ISBNs", not a share of ISBNs issued by an agency.
- **Country attribution:** NZ 008 country = nz; UK publication-country link, Ireland and imports dropped (note AuthorHouse etc. fall out once their stated place becomes the US); France 102/place; Québec place-name match; US (LoC) 008/15-17 ends in "u". Amazon has no country field.
- **Year** = publication year from the record (not cataloguing year).
- **Amazon sample** = Amazon Reviews 2023 Books metadata, print-format products with an ISBN-13 (2.71M). Marketplace, reviews-biased, global; a US-centred series only by assumption. "Amazon-issued" = publisher string matches CreateSpace / Independently published (a marker of Amazon's free ISBN), "979-8" = ISBN prefix.
- **Bowker.** I do not have Bowker's data. The only Bowker values used are two published figures (self-published = 11% of US ISBNs in 2007, 40% in 2012; press-release summaries), plotted as two points. **No correlation or lag can be computed from two points; "Amazon vs Bowker" is a plausibility check on shape and level, not a validation.** Bowker counts ISBNs registered, ours counts ISBNs of listed products.
- **Windows:** UK/NZ 1995–2014; France/Québec 2010–2021; US LoC 1995–2011; NZ to 2019 in break tests.

## Models (all in `econ_*.py`)

### M1. NZ vs paid-ISBN comparators, binomial DiD (`econ_did.py` → `did_amazon_era.csv`)
- Unit: country-year. Outcome: share p_ct = k_ct / n_ct (AP or sp), with n_ct frequency weights.
- Model: logit p_ct = α_year(C(yr)) + β·NZ_c + δ·(NZ_c × 1[year ≥ B]) [+ γ·NZ_c × (year − B) in the "country trends" version]. B = 2007 or 2008. Quasi-binomial (Pearson χ² scale), SEs clustered by year.
- Comparisons: NZ vs UK (1995–2014: 40 country-years, 20 year clusters); NZ vs US-LoC (1995–2011: 34, 17); NZ vs UK+US-LoC (1995–2011: 51, 17).
- Treatment: "NZ (free national ISBN) × post-Amazon/POD shock". The shock is a calendar year, not an ISBN price change; the variation identified is NZ's differential change relative to paid-ISBN countries.
- CI: percentile year-block bootstrap (300 resamples of years with replacement, year FE relabelled); given for the no-trend version only.
- Results (odds ratios, δ): AP, NZ vs UK, B=2007: 1.79 [1.54, 2.10], with trends 1.29 (p = 0.27); NZ vs US-LoC AP: 2.98 [2.32, 3.61], with trends 2.12 (p = 0.002); NZ vs UK combined: 0.66 [0.52, 0.84]. Full rows in C9.
- Weaknesses: one or two control units; statsmodels warns that cluster covariance is not fully supported with freq_weights (SEs may be mis-scaled; treat p-values as approximate); no pre-trend test passes cleanly (the effect shrinks or vanishes once pre-trends are allowed); US-LoC outcome is a selected catalogue.

### M2. Unknown-breakpoint test (`econ_amazon.py` → `break_tests.csv`)
- Outcome: logit share (AP or sp), one country at a time. Null: linear trend. Alternative: linear trend with a level shift and slope change at an unknown year (trim 15%). Statistic: sup-F over candidate years. P-value: residual bootstrap (1,000 resamples, iid residuals).
- Results: NZ AP break 2007 (F = 22.8, p = 0.001), NZ combined 2007 (F = 23.0, p = 0.001); UK AP 2001, combined 2007 (p = 0.004); US-LoC AP 2003, combined 2004; France AP 2009 (p = 0.11), combined 2014 (p = 0.025); Québec none (p > 0.3).
- Weaknesses: iid residual bootstrap ignores serial correlation, so p-values are likely too small; 19–25 annual points; a break year coinciding with the Amazon timeline is suggestive, not shown to be caused by it.

### M3. NZ − UK interrupted time series (`nz_uk_its.csv`)
- Gap_t = logit(p_NZ,t) − logit(p_UK,t), 1995–2014, regressed on (t − B), post, post × (t − B), Newey–West (3 lags). Placebo breaks 2000–2010 for the slope-change t-statistic.
- Results: for AP the slope change is −0.015 (p = 0.57) at B = 2007, −0.037 (p = 0.09) at 2008, −0.073 (p = 0.002) at 2009; combined shows the opposite sign pattern. Not a clean break in the gap; the NZ jump is a level change that the UK partly shares.

### M4. France vs Québec parallel trends and post-2019 (`econ_frqc.py` → `frqc_parallel_trends_did.csv`)
- Unit: year-level log-odds gap d_t = logit(p_FR,t) − logit(p_QC,t) (binomial variance), 2010–2021 (12 years; 9 pre-2019).
- Pre-trend: OLS of d_t on t over 2010–2018, Newey–West (2 lags) and permutation (20,000 shuffles). AP: slope +0.021/yr (SE 0.005, p_NW = 0.004, p_perm = 0.083); residual SD 0.083; year-to-year change correlation −0.10. Combined: slope 0.006 (p = 0.86).
- Post-2019: deviations of d_t from the extrapolated pre-trend: AP 2019 +0.054, 2020 +0.422, 2021 +0.054 (mean +0.177 = 2.1 pre-residual SDs); piecewise regression level shift p = 0.08, slope change p = 0.9996.
- Treatment: France's 2019 ISBN fee, a one-off €37 (excl. VAT, 2025 schedule) dossier fee; the 2019 amount is unverified. Weak dose.
- Weaknesses: two units, so no cross-sectional inference; 9 pre-period points give low power to detect small pre-trend differences; 2020 is a COVID year; combined series is dominated by one publisher (Édilivre).

## Causal claims Part B can and cannot make

- **Can say:** (i) NZ author=publisher shares change structurally around 2007; (ii) NZ's rise exceeds that in UK and US-LoC under simple DiD specifications; (iii) Amazon-issued ISBNs are almost absent from the UK/US national bibliographies; (iv) France and Québec AP shares move in near-parallel before 2019 and do not visibly diverge after the small 2019 fee.
- **Cannot say:** that free ISBNs caused NZ's rise (no price variation within NZ; the NZ–UK effect is not robust to country trends; cataloguing and selection differ across countries); that Amazon caused the 2007 break (timing only); that the French fee has no effect (weak treatment, low power); anything about total self-publishing (national bibliographies measure how self-publishers use the national agency).
- Nothing in Part B is a randomized or instrumented design; it is descriptive evidence with a DiD/break-test structure.

## Not available / not done
- Bowker underlying series; Amazon-vs-Bowker correlation or lag.
- Official population series (per-capita table uses rounded approximations).
- Independent hand validation (gold-label columns are blank).
