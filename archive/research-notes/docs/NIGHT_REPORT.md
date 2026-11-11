# READ THIS FIRST (updated 08:00)
What the overnight work shows, in order of strength. No causal claims anywhere.
1. **Portugal 2015 (fee start):** author=publisher share falls 42-55% vs controls, placebo p<0.03, robust to dropping any control, to classifier fixes (§ night_fixed), and to the 2014 cataloguing change. Weakness: sup-F break test p 0.07-0.45 and the fall is from a 2014 peak.
2. **Mechanism hint, Portugal only:** self-publishers shift off individually bought ISBNs (smaller-prefix share, ISBN share of AP records fall; 2015 ranks 1st of 13 placebo years) while total AP is not distinguishably lower. Does not replicate in Spain.
3. **Spain 2012:** same sign (-27%) but indistinguishable from noise. **France 2019:** null on the raw series; but 21-25% of French AP books in 2020-21 use free Amazon 979-8 ISBNs (0 in 2017); excluding them French AP flattens against trend, with a one-year -0.21 logit gap in 2021 (suggestive).
4. **Data quality:** classifier precision 96-100% across 6 sources (LLM-read labels, not human); UK catalogue collapses after 2014 so UK is unusable as a late donor.
5. **Cross-country levels do not follow fee regime:** free-ISBN Poland/Estonia/Latvia ~3% = paid UK 3.15%; NZ 15%, France 12.6%. So only within-country event designs are informative.
6. **No other free-to-paid event with open data found** (see docs/FEE_HISTORY.md); the test set stays ES/PT/FR (three events).
Still pending at 08:00: Germany and Nordic builds (agents running). Not done: human labels, archived fee pages (Wayback agent launch was blocked by the permission classifier), Czechia download (timeout).

# Overnight report (2026-11-09): fee-introduction event study, validation, fee facts

Descriptive. **No causal claim.** Code: `src/night_events.py`, `night_placebo.py`, `night_fig.py`, `night_percap.py`. Outputs: `output/night/`. Labels: `output/validation_labelled/`. Facts: `docs/FEE_HISTORY.md`.

## 1. Stacked event study over three ISBN-fee introductions
Outcome: logit of the author=publisher (AP) share, normalised to each unit's own pre-period mean (so cross-country rule differences drop out). Treated: Spain 2012, Portugal 2015, France 2019. Donors: NZ, UK, France (France is a free-ISBN donor only for ES/PT, before 2019), Québec (FR event only; UK series ends 2018). Effect = mean gap over event years 0–3. Figure: `output/night/event_study.png`.

| Event | DiD (logit, %) | DiD + own linear pre-trend | Placebo p (two-sided, space×time pool) |
|---|---|---|---|
| Portugal 2015 | −0.54 (−42%) | −0.80 (−55%) | <0.03 (0 of 42 placebos as large) |
| Spain 2012 | −0.31 (−27%) | −0.33 (−28%) | 0.14 / 0.29 |
| France 2019 | +0.17 | −0.08 | 0.41 / 0.79 |

- **Portugal is distinguishable from noise; Spain is the same sign but not distinguishable; France is null.** Leave-one-donor-out leaves signs unchanged (`leave_one_donor_out.csv`: PT −0.47 to −0.64 DiD; ES −0.27 to −0.34).
- Synthetic control (`event_summary.csv`, `sc_weights.json`) agrees in sign and size for ES and PT (−0.34, −0.63); the FR synthetic control is undefined (UK ends 2018).
- The ordering PT > ES > FR is the order of how large/acute the charge is for a self-publisher (PT €100–150 per 10 titles with 2015 start; ES €45 per ISBN; FR a €25–37 dossier fee). That is **three points, and the fee amounts for the self-publisher are secondary-sourced**, so it is suggestive only.
- **Warnings:** (i) placebo years are strongly overlapping, so the p-values are rough; (ii) the UK series is unreliable after ~2016 (AP per million falls 12 → 8 → 3 → 0 in 2014–18, a BNB coverage change, not behaviour), so UK-donor post-years are suspect — the nz+fr-only donor sets still give PT −0.47/−0.68; (iii) Portugal's 2014 spike and the 2014 cataloguing change (RESULTS_PT) still apply; (iv) ES AP flags include organisations named after authors (below); (v) the PT fall may be a return to the long-run mean, which an event study over 7 pre-years only partly addresses.

## 2. Classifier validation (LLM annotator reading the record only; not human gold)
200 rows per source (first 100 flagged, first 100 unflagged); "unclear" excluded and counted. Files: `output/validation_labelled/SUMMARY_*.md`.

| Source | Precision of flags | False-negative rate, unflagged | Notes |
|---|---|---|---|
| UK | 96/98 = 98% | 1/97 = 1% | FPs: ministry/publisher named after author |
| NZ | 95/96 = 99% | 6/87 = 7% | misses: author-named business imprints |
| FR | 98/99 = 99% | 4/93 = 4% | misses: nicknames, Atramenta, l'Édition à façon |
| QC | 100/100 | 2/89 = 2% | misses: pseudonyms |
| ES | 93/97 = 96% | 0/94 | name-rule flags only 3/7 correct: Instituto Paulo Freire, Ediciones Joaquín Rodrigo, etc. |
| PT | 99/99 | 0/93 | **no pre/post-2015 precision difference (29/29 vs 70/70)** |

- The Portugal check matters: the 2015 fall is not a precision artefact of the classifier across the fee date.
- Recall is fragile (UK ≈61%, NZ ≈52%, FR ≈75%, QC ≈74%) because the unflagged stratum is large and many rows are "unclear"; stratum sizes for ES/PT are approximate. Treat recall as a rough lower-bound-ish figure.
- Caveat: the annotator saw the flag and rule columns, which biases toward confirming; no web lookups were made. A human spot check of the 30 false positives/negatives is the cheap next step.
- Suggested rule fixes (not yet applied): organisation guard (Instituto/Fundación/Ministries/Ltd) on name-containment rules; corporate-author match → `corporate_self`; add Minerva Press, Atramenta, l'Édition à façon to the service list; author-death-before-pub-year skip.

## 3. Per capita with official population
`ap_per_million_official_pop.csv`, `ap_per_million.png`. 2018 AP per million: NZ 105, Québec 56, France 46, Spain 22, Portugal 16, UK ~0 (coverage breakdown). France rises 20 (2010) → 75 (2021) with no visible kink at 2019. Québec's level is ≈2× France's pre-2019 only in the free-vs-free comparison, and rules/selection differ across countries, so levels are not comparable.

## 4. Facts (`docs/FEE_HISTORY.md`)
- No further country with a documented free→paid change in 2005–2022 and open bulk bibliography was found beyond ES, PT, FR. So the realistic design remains these three events; extra countries (Germany paid, CC0 DNB dumps; Sweden/Norway/Finland free) would add paid-vs-free **level** comparisons only.
- UK single-ISBN price: £99 (2016) → £89–93 since, nominally flat; Nielsen's online store launched Jul 2016. Ireland buys ISBNs from Nielsen, so Ireland is a paid, not a free, control; no open NLI dump found.
- France: charging began 8 Mar 2019 with online-only applications; 2019 amount unverified (secondary: €25 ex-VAT).
- Québec: free via BAnQ since 1979; self-publishing authors qualify.
- BNB has no published policy on self-published/POD books — a standing threat to UK numbers.
- Official population saved (`config/population_official.csv`, Québec as `CAN_QC`).

## 5. Bottom line
The fee story is a **dose-ordered, partly consistent pattern**: a sizeable, placebo-distinguishable fall in AP share after Portugal's 2015 fee, a smaller indistinguishable one after Spain's, nothing after France's. The classifier looks accurate (≈96–100% precision) and equally so around the fee date in Portugal. It does **not** establish causation: three events, overlapping placebos, a 2014 PT peak, unreliable UK donor years, and unverified fee amounts.

## 6. Still open
Hand/human labels; applying the rule fixes and re-running ES; Wayback pricing for Nielsen/AFNIL; BNP note on the 2014 change; a Nordic or German level comparison; `RESULTS.md` not yet regenerated with these results.

---
# Round 2 additions (in progress; agents still running for DE, Nordics, extra countries, classifier-fix rerun)

## 7. Extensive vs intensive margin (`src/night_margin.py`, `output/night/ap_margin_by_year.csv`, `ap_margin.png`)
- Portugal 2014→2015: distinct AP authors 187→147 (−21%), first-time AP authors (first appearance in the data, left-censored) 131→100, AP books per author 1.29→1.14. The fall is fewer authors, not fewer books per author.
- Spain 2011→2012: distinct AP authors 876→743 (−15%); recovers by 2014.
- France keeps adding authors through 2019–21 (2,586 → 3,476).

## 8. France 2019 hidden by Amazon ISBNs (`src/night_fr_noamz.py`)
- 979-8 (Amazon-issued) ISBNs jump in the French catalogue from 13 (2019) to 1,229 (2020) and 1,668 (2021); they make up 21–25% of French AP books in 2020–21. A catalogue/deposit change or genuine substitution; this report cannot tell which.
- With Amazon ISBNs removed from numerator and denominator, French AP share is 4.86% (2019), 5.27% (2020), 4.95% (2021): a flattening against a +0.4 pp/yr pre-trend. Trend-adjusted gap vs NZ+QC: +0.06 (2019), −0.04 (2020), **−0.21 (2021)**, against a pre-period residual SD of about 0.05. One late year with noisy donors; suggestive of a lagged effect, not established. This revises the earlier "no break" statement, which used AP including Amazon ISBNs.

## 9. UK donor warning
UK catalogue size: 70.6k (2014) → 42.7k (2015) → 34.1k → 10.8k → 0.9k (2018). UK is unusable after 2014 as a donor or as a paid-ISBN series; PT 2015 results should rely on the NZ+FR donor set (−0.47 DiD, −0.68 trend-adjusted).

## 10. New hypotheses tested (`output/night_h/RESULTS_H.md`)
- **Composition (H-A):** no fee-shaped shift; short books, poetry and memoirs did not leave first at any fee date. Many apparent shifts coincide with cataloguing breaks (PT 2014, ES 2016). ~24 tests, so a few nominal hits are expected by chance.
- **ISBN prefixes (H-B), Portugal:** AP books on small-registrant prefixes (≤10 numbers) fell from 45% to 32% (DiD −0.33 log-odds, CI excludes 0); first use of a prefix fell 25% → 10%; the share on multi-author prefixes (service pools) rose 68% → 80%. Singleton prefixes 6.3% → 3.6% (CI includes 0). Spain has too few singletons to test; France goes the other way.
- **ISBN-less records (H-C):** Portugal AP records with no ISBN rose 47% → 58% against flat non-AP (DiD +0.53, CI 0.36–0.70), matching the earlier ISBN-visibility finding. Spain weak; no controls for FR/NZ/QC (their files have no ISBN-less records).
- **Elasticity (H-D):** illustrative only; ≈ −0.7 (ES) and −0.4 (PT) per €100, +0.6 for FR with CI spanning 0; three points.
- Reading: the Portuguese response looks like a shift of self-publishers off individually bought ISBNs (toward service pools or no ISBN) rather than a disappearance of the books — a hypothesis for the ISBN-visibility mechanism, not a causal result.

## 11. Portugal ISBN-visibility with placebos (`output/night_vis/RESULTS_VIS.md`)
- ITS level shifts at 2015 (Newey-West, Holm-adjusted): ISBN share of AP records −0.58 logit [−0.81, −0.36] (p<0.001); share on small-registrant prefixes −0.83 (p=0.005); share on first-use prefixes −1.30 (p=0.001). 2015 ranks first of 13 placebo break years on these. PT non-AP is null; the same outcomes for Spain at 2015 are null; a placebo 2012 break in PT is null.
- **Weak point:** unknown-break sup-F with block bootstrap gives p = 0.07–0.45; none survives Holm. The multi-author-prefix outcome also breaks for non-AP, so it is dropped as AP-specific evidence.
- **Spain 2012 does not replicate** the prefix pattern (signs opposite to Portugal).
- **Total AP (with or without ISBN) in Portugal:** log ITS −0.10 [−0.24, +0.04], so the total fall is not distinguishable from zero; the break is at 2014 (the spike). About 20–50% of lost ISBN-visible books reappear without an ISBN (bootstrap CI −32% to +97%).
- Verdict: the visibility shift is well located in time in Portugal but not statistically established as a break, and not replicated in Spain.

## 12. Extra countries (`output/extra_countries/RESULTS_EXTRA.md`)
- Built Poland (1.01M ISBNs; BN, CC0), Estonia (171.5k), Latvia (21.9k, 2014–23 only). Czechia failed (server timeout; rerun command in the report).
- No new fee events: Poland, Czechia, Estonia free; Latvia charged a nominal fee throughout. The test set remains ES 2012, PT 2015, FR 2019.
- 2015–19 combined self-published shares: free-ISBN Poland/Estonia/Latvia ≈ 3%, paid UK 3.15%, versus France 12.6%, NZ 15%, Portugal 10.5%. **Fee level alone does not order national levels**; cataloguing rules, service-imprint lists, legal-deposit coverage and market structure dominate cross-country levels. This weakens any cross-section reading of the fee hypothesis and strengthens the case for within-country event designs.
- Validation (record-only, 60+60): Estonia/Latvia 57/60 clearly self-published, 1/60 clear misses; Poland's author=publisher rows read as plausible (21 clear, 5 uncertain of 26), but its service-imprint flags (Poligraf, Ridero etc.) cannot be confirmed from the record and rest on weak evidence, so Poland's combined share is an upper-bound-style estimate.

## 13. Germany (`output/germany/RESULTS_DE.md`)
- DNB full dump (CC0, 14.2 GB, checksums verified): 2.64M print ISBNs 1995–2023, BoD foreign-branch ISBNs dropped.
- AP share: 1.0% (2000), 0.5% (2008), 2.5% (2018), 4.0% (2019). Combined with service imprints 4.7% (2008) → 19% (2018) → 32% (2023). AP per million: 9.9 (2012) → 50 (2019), similar to France by 2019. The 2013 and 2019 rises come mostly from US-block ISBNs (978-1, Amazon/KDP), not German-block ones.
- Visible breaks: 2004 (BoD takes off while AP falls 972 → 539); AP +56% in 2013; 979-8 negligible until 2020 (39 → 1,903). Large single-year service steps (epubli 2016, BoD 2018) are probably DNB cataloguing artefacts (unverified).
- Fee history: only the current price (€70 per single ISBN, 2022–24) found; no dated change, so Germany is a paid control, not an event.
- Validation (record-only, 30+30): precision about 83–97% (25 clear, 4 weak-tier uncertain, 1 false positive); misses ~3–7%; small sample. Only BoD, tredition, neobooks and R. G. Fischer have service evidence I read.
- Germany shows that a large paid-ISBN country's self-publishing share can rise sharply when free US-issued Amazon ISBNs become available (2013, 2019–20), the same leakage pattern as France; again a national-bibliography share measures use of national ISBN blocks plus catalogued foreign blocks.
