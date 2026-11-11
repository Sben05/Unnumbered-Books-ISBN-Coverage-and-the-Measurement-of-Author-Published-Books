# Spain: did the self-published share of catalogued print books fall after ISBN fees began?

Descriptive and time-series only. **Causation is not established.** All files are in `output/spain/`; code is `src/build_es.py` and `src/es_analysis.py`.

## Short answer
The data do **not** show a lasting drop after 2011. The author-as-publisher (AP) share is roughly flat at 1.4–2.3% across 2007–2021. The combined share (AP or service imprint) *rises* from 1.5% (2007) to 9.3% (2021), driven by service imprints that enter the catalogue from about 2008. The one visible feature is a one-year dip in 2012 (combined 3.52% → 2.84%), which is mostly a collapse in Bubok-imprint records (367 in 2011 → 5 in 2012) and is followed by recovery by 2013–14.

## Fee timing (checked against agency pages, with caveats)
- The Agencia del ISBN's own notice says charging starts "el próximo lunes día 12 de diciembre"; the page gives no year, but the context and the 12 Dec 2011 El Español article place it in **2011**. Charging was originally announced for **July 2011** and delayed by administrative delays in signing the FGEE agreement ([agenciaisbn.es notice](https://www.agenciaisbn.es/web/index_temporal.php); [El Español, 12 Dec 2011](https://www.elespanol.com/el-cultural/letras/20111212/isbn-cuesta-euros-titulo/7749682_0.html)).
- The FGEE convenio was signed 30 Nov 2011 and published in the BOE on 28 Dec 2011 ([BOE-A-2011-20448](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2011-20448)). The agency's tariff page lists **€45 for one author/publisher ISBN** (+€50 urgent) ([tarifas](https://agenciaisbn.es/web/tarifas.php)); the page is undated, so the 2011 amount for a single ISBN rests on the BOE annex and the El Español article.
- **Consequence:** the "July 2011" start in the brief is not supported. Publication-year 2011 is essentially a pre-fee year; **2012 is the first exposed year** (ISBNs are assigned before publication). The "~€3 per ISBN" figure was not found; bulk prices per ISBN were roughly €4.5–5.5. There is a single price point for self-publishers, so **no dose-response claim is possible**.
- Caveat: I read these pages through a summarising fetch tool, not as raw text. Re-read the three pages before citing in print. FGEE taking over management in Dec 2010 (secondary source only) is a separate earlier event.

## Data and classifier
965,045 BNE monograph rows → 927,190 Spanish print "Libro" records → 800,531 unique valid ISBN-13 after dedup (137,846 print records have no valid ISBN and are excluded; see bias below). Window 2007–2021; **2007 and 2021 are edge years** (no bibliography-2006 file; bibliography-2022 partial) and **2022 is excluded as incomplete**. Services list: `config/selfpub_services_es.csv`; four user-listed imprints (ExLibric, ViveLibro, Punto Rojo, Adarve) have **no independent evidence located** and are flagged `user_listed_unverified` (see `exclude_unverified_services`). Caligrama is `mixed` and kept out of the main measure.

## Headline numbers (`es_by_year.csv`)
| year | print ISBNs | AP % | service % | combined % |
|---|---|---|---|---|
| 2007 | 46,052 | 1.50 | 0.00 | 1.51 |
| 2010 | 55,496 | 1.92 | 1.35 | 3.28 |
| 2011 | 54,336 | 1.83 | 1.68 | 3.52 |
| 2012 | 51,472 | 1.65 | 1.19 | 2.84 |
| 2013 | 46,222 | 1.71 | 1.58 | 3.29 |
| 2016 | 52,790 | 1.85 | 3.08 | 4.93 |
| 2021 | 48,092 | 2.21 | 7.09 | 9.30 |

Total print ISBNs fall 17% from 2010 to 2013 (55,496 → 46,222), a recession-era denominator change.

## Break and ITS results
- **Sup-F** (`es_break_tests.csv`; null linear trend, alt level shift + slope change, 15% trim, residual bootstrap): AP shows **no break** (p = 0.43 iid / 0.51 block, window 2007–2021). For the combined share the best break is **2012** (p = 0.0045 iid / 0.0055 block; 2008–2020: 0.018 / 0.0245); service-only is best at 2010 (2007–2021) or 2012 (2008–2020). **2011 ranks second, never first.** So 2011/2012 is a candidate break for the combined and service series, but not for AP. The iid bootstrap ignores serial correlation and likely understates p; the block version is only a rough check.
- **ITS** (`es_its.csv`; logit share, Newey-West 3 lags): at 2011 the combined series has a level shift of −0.39 logit and slope change −0.15, but the post-break slope is still positive (+0.12/yr). AP at 2011: level shift −0.22, slope change −0.07, post-slope +0.02. These are shifts relative to a steeply rising pre-trend (below), not falls in the raw share. 2012 ranks first among estimable breaks for the combined series; 2010 also shows a significant slope change (a placebo), while 2013–2015 do not. Breaks 2007–2009 are **not estimable** (fewer than 3 pre-years; data start in 2007). With n = 15 the HAC p-values are unreliable and almost certainly too small.
- **Pre-trend** (`es_pretrend.csv`): there are no half-year data (publication dates are years only, no month), so "2007–2011H1" cannot be run; I use 2007–2010 and 2007–2011. Combined slope 0.27 (p = 0.014) and 0.24 (p = 0.003) logit/yr; AP 0.096 (p = 0.10) and 0.070 (p = 0.064). The pre-period is **not flat**, so any ITS level shift is relative to an extrapolated rise.
- **Amazon-assigned ISBNs** (`es_isbn_prefix_by_year.csv`): 979-8 ISBNs are 0–1 per year through 2019, then 139 (2020), 185 (2021), 74 (2022, partial); 402 total. CreateSpace / Independently Published imprints total 19 records. Free Amazon ISBNs are essentially absent from the BNE before 2020, so this file cannot show whether they neutralised the fee during 2012–2019.

## What the design can and cannot claim
- **Can:** describe the shares and their timing; say that the AP share has no detectable break and no lasting decline, and that a one-year dip in the combined share in 2012 is **consistent with** a fee-start year but also with a platform-specific record gap.
- **Cannot:** attribute anything to the fee. There is no clean comparison country or group in this directory, so **no difference-in-differences was run**; a one-control DiD would not be credible. The service series is mechanically a ramp from zero (Círculo Rojo, Letrame, etc. entering), which makes break tests and ITS pick up the slowing of that ramp.

## Known biases
1. **ISBN ≠ sales or output.** Only books with a valid ISBN count; ISBN was made optional in 2008 (secondary source), and 137,846 print records have none. Their share of print records falls from 23.8% (2007) to 8.9% (2021), and from 16.9% to 13.5% across 2011→2012, so there is no sign in this file of a shift into ISBN-less books after the fee.
2. **Classifier precision is unknown.** The AP rule is dominated by initials matches (12,394 of 14,475 AP flags), the weakest rule, and the record-only read found organisations named after authors passing as AP (3 of 9 AP flags read). Service membership depends on a list whose four user-supplied entries are unevidenced. `validation_es.csv` has blank gold labels; no precision/recall is claimed.
3. **Cataloguing practice changes.** Corporate-author = publisher records fall from 497 (2013) to 44 (2014), and Bubok records vanish after 2011 for reasons I did not determine, so some of the series movement may be BNE process rather than behaviour.
4. **2011 confounders:** Eurozone crisis and austerity (print ISBN counts −17% 2010→2013); the Amazon.es launch (2011, taken from the brief, not checked); any legal-deposit or ISBN rule changes around 2011 (not checked).
5. Edge-year incompleteness (2007, 2021, 2022).

## Causation not established
These results are descriptive. They are consistent with, and do not exclude, a small transient effect of fees in 2012; they provide no evidence of a lasting effect and no basis for a causal or dose-response claim.

*Sensitivity (`es_sensitivity.csv/.png`)*: main, author_only, exclude_mixed, exclude_vanity (AP or platform only), exclude_government, exclude_reprints, initial_only (AP matches resting on initials only), plus include_mixed, exclude_initial_matches, exclude_unverified_services. None changes the picture of a flat AP share and rising combined share; `exclude_vanity` shows the 2012 dip most clearly (2.51% → 1.66%) because it keeps Bubok-type platforms.
