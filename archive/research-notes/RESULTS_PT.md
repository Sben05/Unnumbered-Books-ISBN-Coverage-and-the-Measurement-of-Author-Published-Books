> **Revision notice (2026-11-09).** A later audit (deliverables/PAPER_EVIDENCE_AUDIT.md, deliverables/PORTUGAL_PAPER_DRAFT.md, output/paper_pt/) found that the agency-defined author-edition prefix (978-989-20 / -33) does NOT fall at 2015 (380 → 432 books; allocation rate flat at ~900 serials/yr), unlike the author-name (AP) series below. The AP headline should be read as a statement about how author names appear in publisher fields and which prefixes books use, not as a fall in author-published output. Also corrected: the fee section's claim that no author price was found (see 'Correction' there). Original text kept below.

# Portugal: did the self-published share of catalogued print books fall after ISBN fees began (1 Jan 2015)?

Descriptive and time-series only. **Causation is not established.** Files are in `output/portugal/`; code is `src/pt_load.py`, `src/build_pt.py`, `src/pt_analysis.py` (main results), `src/ap_consistent.py`, `src/es_apc.py`, `src/pt_robustness.py` (this revision's checks). Same design as `RESULTS_ES.md`, with a longer pre-period.

## Headline (revised after the robustness checks)
1. **The author-as-publisher (AP) fall at 2015 is not an artifact of the 2014 cataloguing change.** A format-invariant AP rule gives almost the same series (2013: 175, 2014: 223, 2015: 149 books vs 180, 241, 158 with the original rule) and the sup-F break stays at **2015**.
2. **But it is a fall from a peak, not a fall below the long-run level.** AP share is 1.53% in 2015 (consistent rule) vs 2.29% in 2014; the 2016–2025 average (1.61%) equals the 2005–2014 average (1.61%), is 0.34 pp above 2005–09, and 0.30 pp below 2010–14. A return to the long-run mean is as consistent with the data as a fee effect.
3. **The most distinctive 2015 event is about visibility, not volume.** The share of AP records that carry an ISBN drops from 51% (2014) to 39% (2015) and recovers to 50% by 2019; total AP (with or without ISBN) falls much less and has no distinctive break. This is consistent with a temporary move off ISBNs, and it is the finding I would lead with, as a hypothesis.
4. Spain gives only weak comparison evidence (below). The combined (AP + service) share remains uninterpretable as a fee test (one imprint, Chiado, dominates).

## Fee timing and size (one press source; caveats)
Fee from **1 January 2015**, charged by APEL, which has run the national ISBN agency since 1988; before 2015 the state and APEL shared the cost, so registration was effectively free to users ([Observador, 10 Sep 2015](https://observador.pt/?p=838672)). Table in that article: professional publishers €100 per 10 titles / €3,000 per 1,000; non-professional €150 / €4,500. **No per-ISBN price for a self-publishing author was found, so no dose-response test is possible.** **Correction (2026-11-09): this statement is wrong.** APEL's current service rules (https://apel.pt/isbn/normas-de-servico/, read 2026-11-09, saved in data/raw/apel/normas.html) list a single author-edition ISBN ("ISBN individual (edições de autor)") at €15 excluding VAT, and the user supplied an 11 Dec 2014 APEL notice reporting the same €15 (that document could not be retrieved here and is unverified). Also listed: €25 initial registration for non-members (applicability to a first-time individual author unresolved), and online-only applications, so price and procedure changed together. A price now exists for the author-edition class, but it is a single price (€15) with no cross-sectional or over-time variation inside the class, so it still does not provide a credible dose-response design. I read the article through a summarising tool; re-check before citing. ISBNs are obtained before publication, so publication-year 2015 is partly exposed and 2016 is the first fully exposed year.

## Data
1,313,291 BNP catalogue records (UNIMARC XML) → 812,811 Portuguese print monographs → **294,728 unique valid ISBN-13**; 472,271 print records have no valid ISBN (22–29% of print records each year since 2010). Window 2005–2025 (2026 excluded; flags on 2005, 2008, 2025). Service list `config/selfpub_services_pt.csv`: Chiado (8,485 records) and Cordel d'Prata dominate, both with weak evidence; unevidenced imprints (e.g. Atlântico Press) are `mixed` and outside the main measure.

## Check 1: the 2014 cataloguing change (`pt_ap_consistent_by_year.csv`, `pt_break_tests_consistent.csv`)
- **What changed:** publisher strings in AP records go from initials-style (58% of 2013 AP records, e.g. "J. R. Castro") to full names (4.5% initials in 2014). The change follows **publication year, not cataloguing date**: 2013-published books catalogued in 2014 still show initials (70 records), while 2014-published books catalogued the same year mostly do not (32 of 5,106). It reads as a rule applied to new items from 2014, not a back-catalogue re-edit. BNP documentation of the change was **not found** (a 2021 presentation says Portugal still uses its 1984 cataloguing rules; nothing on 2014).
- **Format-invariant rule** (`ap_pure`: every publisher token is a surname token, a given-name token or the initial of a given name; at least one surname and one given-name token) matches initials and full names alike. Its initials-token count falls 105 → 11 (2013 → 2014) while full-name matches rise 70 → 212, so total AP is stable across the switch. Union with the original rule = `ap_consistent`.
- **Break tests:** `ap_consistent` best break is **2015** in both windows (2005–2025: F = 10.5, p = 0.012 iid / 0.063 block; 2009–2024: F = 14.2, p = 0.009 / 0.016). `ap_pure`: 2015, p = 0.013 / 0.079 and 0.017 / 0.019. The earlier exact-name-only break at 2014 was the format effect and disappears when the rule is format-invariant.
- **Record comparison** (`pt_ap_2013_vs_2014_record_profile.csv`): the flagged books are the same kind in both years (median 130 vs 155 pages; 96% vs 93% first editions; printer named on 74% vs 79%; literature ≈ 45% vs 50% of UDC classes), with modest shifts (applied sciences 8% → 2%, arts 6% → 13%). My read of 22 + 22 records found poetry, local history, children's stories and memoirs in both, and one institutional false positive in 2014 (a municipality named on a book by Júlio Pomar). `ap_2013_vs_2014_sample_for_hand_labelling.csv` holds 50 + 50 records for **human labelling, not done**.
- **Caution:** AP jumps in 2014 in both ISBN-bearing (175 → 239) and ISBN-less records (163 → 230). A 2014 spike common to both groups could be partly recording practice, which would make 2015 a return from an inflated year.

## Check 2: pre-trend and placebos (`pt_placebo_distribution.csv`, `pt_yoy_changes.csv`, `pt_nonlinear_trend.csv`, `pt_baseline_comparison.csv`)
- **Year-on-year:** 2015 is the **largest one-year fall in 20 years** (−0.41 logit, −0.76 pp; −2.0 SD of pre-fee changes). By exchangeability that is a one-in-twenty event, not a rarity; 2007 → 2008 fell by a comparable −0.35 logit and reversed within two years.
- **Placebo breaks using only pre-fee data (2005–2014):** breaks at 2009–2012 produce *upward* level shifts; only the 2008 placebo (3 pre-years) produces a comparable fall (−0.46 logit), driven by that 2007 → 2008 drop.
- **Non-linear trend:** a quadratic fitted to 2005–2014 predicts 2.70% for 2015 against 1.54% actual, outside its 95% prediction interval in 2015 and 2016 but inside from 2017 (intervals widen; quadratic extrapolation beyond a few years is not informative). The quadratic-baseline ITS level shift at 2015 is −0.39 logit (p < 0.001, HAC; unreliable at n = 21).
- **Baselines:** see Headline 2. The pre-period is not flat (AP slope +0.07 logit/yr over 2005–2014, p = 0.006), so level shifts are measured against an extrapolated rise.

## Check 3: ISBN substitution (`pt_total_selfpub_consistent.csv`)
| year | AP with ISBN | AP without ISBN | share of AP records with ISBN | AP rate, all print records |
|---|---|---|---|---|
| 2013 | 179 | 165 | 52% | 2.58% |
| 2014 | 240 | 232 | 51% | 3.23% |
| 2015 | 165 | 253 | 39% | 2.78% |
| 2016 | 151 | 205 | 42% | 2.49% |
| 2018 | 158 | 210 | 43% | 2.79% |
| 2019 | 160 | 158 | 50% | 2.39% |
- Share of AP records with ISBN: best break **2015** (p = 0.017 iid / 0.14 block, 2005–2025; 0.017 / 0.057, 2009–2024); ITS level shift −0.57 logit, ranked first of 13 break years. An upward jump at 2011 (44% → 54%) shows the ratio also moves for other reasons.
- Total AP (ISBN or not): ITS level shift at 2015 only −0.15 logit (p = 0.011, rank 6 of 13); sup-F best break 2010 in 2005–2025 and 2014 in 2009–2024 (p = 0.13, not significant). Total self-publishing by this measure fell far less than the ISBN-bearing part.
- Interpretation (hypothesis, not established): the fee may have reduced *ISBN use* by self-publishers more than self-publishing. The ISBN-less set is also the part of the catalogue most exposed to cataloguing-practice drift.

## Check 4: Spain as a comparison (`pt_es_*.csv`, `pt_es_ap_comparison.png`)
Same format-invariant rule applied to Spain. AP share 2014 → 2015: Portugal 2.29% → 1.53%; Spain 1.95% → 1.75%.
- Spain alone: ITS level shift at 2015 −0.14 logit (p = 0.018, rank 3 of 10), but no sup-F break (p = 0.64). Spain also dips in 2015, so a common shock or noise cannot be excluded.
- Portugal over the common 2007–2021 window: best break 2015 but **p = 0.21** (block), not significant at 15 years.
- Gap (Portugal − Spain) ITS at 2015: level shift −0.31 logit (p = 0.006, rank 3), slope change −0.076 (p = 0.009, rank 2). The gap was already trending up before 2015 (+0.054 logit/yr, p = 0.13), so parallel trends are not established. Spain is itself fee-treated (2011), has its own cataloguing change in 2013 → 14 (corporate-author records 497 → 44), and uses different services; **this is a one-control gap comparison, not an identified DiD.**

## What the design can and cannot claim
- **Can:** the AP fall at 2015 is robust to the cataloguing change, is the largest annual fall in the series, and coincides with a fall in the ISBN-visible fraction of self-publishing that recovers by 2019.
- **Cannot:** separate the fee from regression to a long-run mean, the 2014 spike, Spain-shared shocks or other 2015 events; show that total self-publishing fell; claim a dose-response; or interpret the combined share.

## Not done
Irish (free-ISBN) comparison data were not acquired; no synthetic control or stacked DiD; BNP documentation not found; the 50 + 50 hand labels and the 400-row validation sample are unlabelled; confounders (2011–14 recession, print-on-demand growth, Clube de Autores in 2022) not tested. ISBN ≠ output, classifier precision is unknown, and Chiado's 2022 trough (34 records) and Cordel d'Prata's growth are unexplained.

## Causation not established
These results are consistent with a modest, partly transient effect of the fee on how self-publishers use ISBNs, and equally with return to a long-run mean after a 2014 peak, a Spain-shared shock, or other changes. They do not support a causal or dose-response claim.
