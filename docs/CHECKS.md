# Verification completed

11 November 2026.

- Recomputed the direct analysis from the frozen 262,775-record export; checked input hashes and unique record IDs.
- Matched each 2005–19 annual classified count, classified ISBN count, and retained total against the preceding analysis output.
- Matched six overlapping robustness specifications to the preceding results, allowing for the sign change from ISBN absence to presence.
- Checked the exact log decomposition to numerical precision.
- Recomputed two direct-outcome forecasts and seven classification-error scenarios; retained their underlying output CSVs.
- Verified Equation 5's producer-share identity for every annual observation and reproduced the Portugal fixed-composition example: 1.86% observed ISBN share in 2014 versus 1.53% with 2014 composition and 2015 coverage. The actual 2015 ISBN share is 1.29%.
- Generated all three figures and five numerical manuscript tables from numerical outputs or archived model inputs. Added a sixth table reconciling the source extraction with the analytical population, verified against the processed Parquet files and frozen record IDs.
- Compiled the updated 18-page LaTeX manuscript with Tectonic; checked for missing characters, unresolved references, and overfull boxes. One non-blocking underfull-box warning remains in the bibliography.
- Checked all 13 citation keys against bibliography entries and PDF destinations. All 36 citation links and 48 internal links resolve; the BNP citation displays `BNP, n.d.-b; BNP, n.d.-c`.
- Inspected rendered pages containing the title, figures, robustness table, sensitivity table, and annual-count table. Labels and table columns are legible and fit within the page.
- Checked the 800/2,000 sampling overlap, unique IDs, 40 year/class/ISBN cells, hidden explicit analysis fields, and blank human-label columns.
- Confirmed the validation scorer rejects blank labels. Tested its weighted precision, recall, coverage, and zero-change calculation against a synthetic population in a temporary directory; synthetic labels were never added to research data.
- Read the two original APEL policy PDFs through extracted text and recorded the external sources reviewed in `provenance/SOURCE_REVIEW.md`.

These checks verify reproduction and presentation. They do not establish human classification accuracy, independent raw-data reconstruction, stable bibliography coverage, or a causal effect of the reform. No human-review or classification-corrected result is reported.
