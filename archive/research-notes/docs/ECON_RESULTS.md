# Econometric results: ISBN cost, Amazon, and self-publishing

Descriptive and quasi-experimental; none of this is a randomized design. Read METHODS.md §7–8 for data limits. All tables are in `output/selfpub/`, figures in `output/selfpub/figures/`. Code: `econ_frqc.py`, `econ_amazon.py`, `econ_did.py`, `econ_figures.py`.

**Outcome used for tests:** *author = publisher* share (AP), because it needs no list of services and the services lists are the least reliable part. The combined share (AP OR service) is reported as a check.

## 0. New data

| Source | What | Caveat |
|---|---|---|
| US, Library of Congress | MDSConnect BooksAll 2016 (MARC21), 10.7M records; 1.79M print ISBNs 1995–2016 after filters | LoC catalogues what it selects, not all US publishing. Counts fall from 2012 (cataloguing lag in a 2016 snapshot), so the **US window is 1995–2011**. |
| Amazon | Amazon Reviews 2023 "Books" product metadata (McAuley Lab), 4.45M products, 2.71M print ISBNs 1995–2022 | A marketplace catalogue, not a national one. No country field. Skews to products with reviews. Treat as a **US-centred marketplace series**. |
| Harvard bibliographic dataset | not used | LoC covers the same ground more fully; Harvard's release is a research-library selection. |

Sanity check on Amazon: Bowker reports self-published = **11% of US ISBNs in 2007 and 40% in 2012** (infodocket/ProQuest summaries of Bowker releases); the Amazon sample gives 6.2% and 23.7% for the combined measure. Same shape, lower level, as expected for a reviews-biased sample (`figures/amazon_vs_bowker.png`).

## 1. US vs New Zealand (general)

| | 1995–2011 level of AP share | Per million people, 2010 |
|---|---|---|
| NZ (free ISBN) | 3.2% → 10.5% | 89.5 |
| US, LoC (paid ISBN) | 0.37% → 0.25% (flat/falling) | 0.7 |
| Québec (free) | – | 38.4 |
| France | – | 19.9 |
| UK (paid) | 0.9% → 0.8% | 9.9 |

Regression (binomial GLM, year fixed effects, year-clustered SEs, 1995–2011, break 2007; `did_amazon_era.csv`): relative to the US-LoC series, NZ's AP share rose by an **odds ratio of 2.98 (bootstrap CI 2.32–3.61)** after 2007, and **2.12 (p = 0.002)** with country-specific linear trends. But the US LoC is a selected catalogue that did not absorb the Amazon boom (see §3), so this contrast mostly shows that **a national legal-deposit catalogue in a paid-ISBN country did not record the self-publishing rise at all**.

## 2. New Zealand after Amazon

- **Unknown-break test (sup-F, residual bootstrap):** NZ's AP log-odds has a structural break in **2007** (F = 22.8, p = 0.001); the combined share has the same break year (F = 23.0, p = 0.001). The Amazon sample's CreateSpace/Independently-published print records go from 933 (2007) to 2,722 (2008) to 5,417 (2009), the same window (`figures/amazon_timeline.png`). 2007 is also the year of the Kindle launch, but that is a coincidence of timing, not tested.
- **NZ authors stayed in the national system.** NZ records carrying US 979-8 ISBNs are only 24–37 a year in 2020–22 (about 1% of NZ print ISBNs). Only 3–6.5% (2013–22) of NZ's 978-0-473 / 978-1-06 pool ISBNs show up in the Amazon sample at all. Free local ISBNs absorbed the Amazon-era surge instead of Amazon's.
- **Mechanism, entry:** NZ's AP publishers per year rise from 174 (2006) to 362 (2009) and 428 (2016), mostly new names (entrants 139 → 273). The UK shows a similar jump in 2007 (212 → 342 entrants), so the 2007 surge is a shared technology shock; NZ's response is larger in share terms.
- **Mechanism, the agency's small-publisher pool:** inside NZ's 978-0-473 / 978-1-06 pool, AP ISBNs go from 170 (2006) to 357 (2009) and 371 (2012), while AP ISBNs outside the pool stay roughly flat at 50–100. The pool itself grows from 760 to 1,231 ISBNs a year. The NZ surge ran through the National Library's free pool, not through established publishers (a descriptive count, not a causal test).
- **Honest caveat:** UK AP also rose in 2007 (0.69% → 0.91% by 2008, +31%; NZ +70%), and the NZ–UK difference shrinks with country trends (OR 1.29, p = 0.27). **The NZ-vs-UK comparison supports "bigger rise where ISBNs are free" without country trends (OR 1.79, CI 1.54–2.10) but is not significant once pre-existing trends are allowed.** Using the combined measure the sign reverses (OR 0.66) because the UK's author-services boom (AuthorHouse etc.) lifts the UK numerator.

## 3. UK and US after Amazon: leakage out of the national bibliography

- Amazon sample, CreateSpace/"Independently published" print records in 2012: **24,169**. The same imprints in national bibliographies in 2012: **UK 35, US (LoC) 57, NZ 2, France 0, Québec 0** (`amazon_issued_capture.csv`). National bibliographies in the UK and US essentially do not see Amazon-issued ISBNs; the LoC does not catalogue them and BNB hardly does.
- The AP share in those bibliographies is flat (~1% UK, ~0.3% US-LoC; AP only) through the boom, while marketplace-level self-publishing went from 6% (2007) to 24% (2012) to 49% (2021) in the Amazon sample, and 11% → 40% (2007 → 2012) in Bowker's published figures.
- Reading: in paid-ISBN countries, the 2008–2015 self-publishing boom happened largely **outside the national ISBN agency and legal-deposit record**, via Amazon's free ISBNs (CreateSpace, then KDP "Independently published", then 979-8 from 2020: ~50,000 records a year by 2020). In free-ISBN countries (NZ, Québec) it stayed inside. This is the mechanism that makes national-bibliography shares a measure of *how self-publishers use the national agency*, not of total self-publishing, and it is the main reason cross-country levels must not be compared as if they measured the same thing.
- UK break tests: AP break 2001 (artefact of a drop in 2001–02, not an Amazon effect); combined break 2007 (F = 14.4, p = 0.004), driven by AuthorHouse/Xlibris.

## 4. France vs Québec before and after March 2019

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

## 5. Summary of what holds up

1. **Strongest:** NZ's author-publisher share broke upward in 2007 (p = 0.001), coincident with Amazon/POD self-publishing, and NZ's per-capita rate (~90–110 per million) is about 10× the UK's (~10) and ~100× the US-LoC's. Free local ISBNs plus POD tools fit this. Cataloguing and selection differences could account for part of the level gap.
2. **Strong, but mechanism not tested:** in paid-ISBN countries the Amazon-era boom sits outside national bibliographies (national records show 35–57 Amazon-issued ISBNs a year against ~24,000 on Amazon).
3. **Null with qualification:** France vs Québec are parallel before 2019 on author=publisher, and show no sustained break after the 2019 fee; the fee was small.
4. **Does not hold:** the combined measure's UK vs NZ difference reverses sign (UK services boom). Country-trend-adjusted NZ vs UK AP effect is not significant.

## 6. Ideas not yet done

- Get the 2019 AFNIL tariff and the Québec policy history, then redo §4 with the right dose.
- Use the Amazon data with publisher location (Amazon "Publisher" strings) to build a UK, NZ and Québec marketplace series.
- Find a second, paid-ISBN francophone comparator (Belgium via KBR; Switzerland) for a three-way France comparison.
- Human validation of the blank gold-label CSVs, then correct estimates for misclassification.
