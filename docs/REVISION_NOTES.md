# Editorial and evidence review

11 November 2026.

The revised paper takes the feedback's measurement contribution seriously, while making the missing validation harder to overlook. The old manuscript spread its argument across forecasts, international prices, platform substitution, discoverability, and institutional gates. The new draft centres the relationship between one catalogue count and its ISBN-bearing subset. Its framework distinguishes catalogue capture from identifier coverage. It does not claim that the catalogue gives total publication output.

The 2014–15 arithmetic survives reproduction. There are 392 → 343 classified records, 240 → 171 with ISBNs, and a decline in coverage from 61.2% to 49.9%. The exact log identity is −0.338975 = −0.133531 − 0.205444. The coverage fraction is 0.606073. Agency assignments of 988 → 617 are context, not a component of this identity.

The longer-window evidence is clearer when stated directly: 58.5% → 51.3% ISBN coverage; excluding 2014 gives 57.6% → 51.3%. The descriptive differential against all other catalogue records is −6.55 points; excluding 2014 gives −5.75 points. These are not the prior model's −13.9-point comparison against selected small publishers. Both can exist because the populations, windows, and specifications differ.

The newly computed direct-outcome forecast fits coverage itself. It uses a single 2012–14 holdout and 2005–11 training, then refits through 2014. The logit trend fits that holdout better than a five-year mean, but the post-period gap changes from −7.0 to −16.8 points depending on extrapolation. The manuscript reports this as assumption sensitivity, not a causal interval. The old seven-model ensemble is documented in the appendix with its different denominator.

The most important new diagnostic is asymmetric classification sensitivity. Uniform error assumptions preserve a decline, but they conceal the leverage of the large negative population. Adding approximately 289 missed author-published records among 56,037 post-period ISBN-bearing predicted negatives erases the pooled change if every other cell is correct. This does not show that the classifier makes those errors. It shows that a good-looking overall accuracy rate is insufficient. Validation must bound period-specific, ISBN-specific omissions.

The supplied APEL letter and archived announcement PDFs were located and their text extracted. They resolve the earlier review's missing-document issue for the announced 2015 rules. The application of initial prefix-registration charges to individual requests, actual unused allocations, actual costs, and individual responses remain unobserved.

All direct numerical results and manuscript tables reproduce from the local frozen input. The extraction is conditional on prior machine flags: raw-data classification has not been independently re-created in this revision. The scorer was checked to reject the blank human-review sheet. No human labels have been invented or substituted with AI assessments.

Before submission, complete independent validation, reassess the headline under the resulting uncertainty and ambiguity bounds, audit the acquisition/filter provenance, broaden the literature review, and obtain academic feedback. The revised draft is a more focused working paper, not evidence that these tasks have already been completed.

## Subsequent editorial revision

Incorporated the user's follow-up on indentation, economic contribution, citations, sample reconciliation, and voice. Section 6 now derives the distinction between output growth and coverage growth, the relationship between catalogue and ISBN-only producer shares, and the slope distortion when outcome coverage covaries with a regressor. Examples cover apparent entry, product variety, and mismatched revenue/title denominators, without claiming estimated revenue, productivity, or welfare effects. A newly verified citation to Bhandari et al. (2020), AER: Insights, connects the discussion to evidence on economic measurement and sample representativeness.

The introduction begins with Portugal's 37.6% assignment decline and 12.5% classified-record decline, then resolves the population mismatch through a comparison within the bibliography. Institutional prose follows the announced changes an applicant would encounter. Repeated reviewer-facing qualifications were reduced; classifier uncertainty and incomplete catalogue capture remain prominent in their proper sections. Forecasts are expressly labelled sensitivity exercises, not causal counterfactuals.

The previous 313,379-book extraction is reconciled to 262,775 retained records using source-file counts and exact record-ID checks. No regression estimates or headline arithmetic changed. Body indentation now includes first paragraphs after headings. The BNP date suffixes are protected against natbib's year-compression parsing, and all 13 citation keys were checked against the bibliography and PDF link destinations.

## Final explanatory refinements

Replaced the abstract's either-or question with the user's question about the respective contributions of fewer recorded books and changing coverage. The introduction now explains the economic intuition with an unchanged-book-count example before naming nonclassical measurement error. Section 6 connects Equation 5 to Portugal's actual 2014/2015 counts: catalogue shares 2.70%/2.29%, ISBN-only shares 1.86%/1.29%, and an ISBN-only share of 1.53% when 2014 catalogue composition is combined with 2015 coverage. This is expressly a fixed-composition accounting reference. `analyze.py` now verifies the share identity for every annual observation and exports the example to `results/producer_share_example.csv`.

The validation section explicitly identifies independent coding and adjudication as the main requirement before journal submission. Sensitivity calculations identify potentially consequential errors but cannot estimate their actual frequency. No human labels or accuracy results have been supplied or claimed.
