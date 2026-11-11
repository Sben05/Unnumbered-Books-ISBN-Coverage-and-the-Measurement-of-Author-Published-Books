# Unnumbered Books: revised paper and replication materials

Revision dated 11 November 2026. Author: Shreeniket Bendre.

Start with `deliverables/UNNUMBERED_BOOKS.pdf`; edit `deliverables/UNNUMBERED_BOOKS.tex`. This is a complete replacement draft with appendices, rather than a revision outline. It is a working paper awaiting independent classification validation, not a submission-ready or peer-reviewed article.

Superseded manuscripts are preserved locally under `archive/drafts/`. The current paper is `deliverables/UNNUMBERED_BOOKS.tex` and its compiled PDF.

## What changed

- Rebuilt the article around ISBN coverage among catalogued author-published books. The scope excludes many service-imprint books and is narrower than all independent publishing.
- Reproduced the within-bibliography decomposition: 60.6% of the 2014–15 log decline in ISBN-bearing classified records is the coverage component.
- Recomputed annual coverage, pooled 2010–14 versus 2015–19 rates, exclusion of 2014, equal-year weighting, alternative classification, deposit-number dating, and a catalogue-entry-year restriction.
- Added two transparent forecasts of the actual coverage outcome, with a single pre-2015 holdout. Moved the earlier ensemble, which predicts a different denominator, into the appendix.
- Added explicit asymmetric classification-error scenarios. An adverse omission probability of approximately 0.515% among post-period ISBN-bearing predicted negatives can erase the pooled decline.
- Verified the original APEL 2014 letter and contemporaneous archived notice against the local PDFs. Both are included with extracted text and hashes.
- Prepared an 800-record blinded pilot plus an overlapping 2,000-record precision-oriented extension, a separate weighted key, and a scorer for completed human labels.
- Used author–year citations and moved implementation paths out of the article's main text.

## Reproduce the numerical revision

Requirements: Python, NumPy, pandas, Matplotlib. Tested versions are recorded in `results/environment.json`; the existing ISBNResearch Python environment contains them. Tectonic compiles the paper.

From the repository root:

```sh
python analysis/analyze.py
python analysis/make_tables.py
python analysis/build_paper.py
```

On this computer, the tested interpreter is `.venv/bin/python`. If Matplotlib's default cache is not writable, use `MPLCONFIGDIR=/private/tmp/isbn-revision-matplotlib` for the first command. No network is required for numerical analysis. A first-time Tectonic installation may need to download its TeX dependencies; compilation succeeded with the existing local installation.

`analyze.py` verifies the provenance manifest and the frozen input, unique IDs, annual counts against the preceding analysis, the exact decomposition, and six overlapping robustness results. It produces three figures, annual counts, robustness estimates, scenario calculations, direct forecasts, and a summary JSON. `make_tables.py` produces five numerical manuscript tables from those inputs and outputs, including the archived ensemble components. A sixth table reconciles the source extraction with the analytical population. Its CSV and TeX are supplied; optionally rerun `python analysis/audit_population.py /path/to/ISBNResearch` with pyarrow and the source project's processed Parquet files to regenerate it. This additional audit is not required to compile the supplied paper or reproduce its direct estimates.

## Data provenance and the reproduction boundary

`inputs/records.csv` has 262,775 unique Portuguese print-book record IDs, publication years 2005–25, and the flags needed for the analysis. It comes from the existing `data/interim/pt_natbib_records.parquet`, filtered by `print_like & pt`, joined one-to-one to the deposit-number field in `bnp_csv_bibliografianacional.parquet`.

The source `pt_natbib_records.parquet` SHA-256 is `5277dc345ce724bda662661e654ad2e64ab8a5b5630cf05f58969935faaa5d76`. The export's hash is in `provenance/manifest.json`. Counts: 189,663 records in 2005–19; 130,324 in 2010–19; 3,277 provisionally classified author-published records in 2010–19. Later publication years remain in the export for the deposit-year alternative, not for post-2019 substantive claims.

The extraction script describes the national-bibliography source as the 7 January 2026 snapshot. That description is inherited provenance, not an independently established common date for all source files. The live public-data portal reports a different update date for its catalogue listing. Dataset metadata dates, resource snapshot dates, download dates, and this revision's freeze date must not be conflated. The full original source-file manifest and filters should receive another independent provenance audit before submission.

BNP distributes its bibliography and catalogue metadata under CC0, as shown on its official public-data listings:

- [Bibliografia Nacional Portuguesa](https://dados.gov.pt/pt/datasets/bibliografia-nacional-portuguesa/)
- [Catálogo BNP](https://dados.gov.pt/pt/datasets/catalogo-bnp/)

`provenance/` preserves the prior numerical outputs, relevant original classification scripts, and both APEL policy PDFs. Scripts there are documentary copies, not an independently executable full raw-data pipeline: their original dependencies and configurations remain in ISBNResearch. The revised code does **not** regenerate national-bibliography membership, the classifier, or ISBN parsing from raw UNIMARC downloads. It reproduces the direct analysis conditional on frozen flags. It also does not rerun the historical international models or same-author analysis; those outputs are explicitly identified as inherited evidence.

The APEL documents are supplied for source verification. Their inclusion does not imply a blanket licence for redistribution of the letters, archived webpage, or third-party scholarship. The GitHub repository publishes the compact replication materials; raw downloads, local archives, and the blinded sample key remain local.

## Human validation

Do not show `validation/DO_NOT_SHOW_CODERS_key.csv` to coders before independent labels are complete. `validation/PILOT_800.csv` is the first 800-record design; `validation/LABELS_2000.csv` includes the same records plus 1,200 additional records. Do not concatenate the sheets. Read `validation/PROTOCOL.md` before labelling.

The sheets are blank. No AI-generated labels have been represented as human judgments. No corrected estimates, precision, recall, or agreement are claimed. The scorer will reject the delivered blank sheet:

```sh
python analysis/score_validation.py validation/LABELS_2000.csv
```

After independent coding and evidence-based adjudication, pass a completed copy to that command. It requires all rows, reviewer identities, and resolved Y/N labels; unresolved U cases require a separate bounded analysis. Treat zero-error bootstrap intervals cautiously and report stratum error bounds.

## Remaining research work

Independent human validation and sensitivity estimates are the main unfinished requirement. The paper also needs broader literature review, independent checking of dataset provenance and record filters, and academic feedback. No additional causal interpretation follows automatically from completing these tasks. Neither a one-time catalogue snapshot nor the announced fee schedule identifies the reform's price effect or the number of books absent from the catalogue.

## Editorial follow-up

The updated draft indents first body paragraphs after headings, repairs the undated BNP citations, and develops the economic contribution in Section 6. It explains effects of selective observation on growth, producer shares, and regression slopes; these are measurement arguments, not a new causal model. Direct forecasts are explicitly sensitivity exercises. The opening and institutional discussion now lead with the Portuguese puzzle and concrete registration rules, while repeated caveats have been consolidated. Human-validation and capture limitations remain explicit.

The prior 313,379-book figure is now reconciled to the 262,775-record export: 8,076 unmatched catalogue records, 502 without usable years, 39,579 outside 2005–25, 212 failing the print filter, and 2,235 without Portuguese country metadata are excluded sequentially. This reconciliation was verified against processed source files and the frozen export's record IDs. It does not establish eligibility for unmatched records or exhaust the original-download provenance audit.

The compiled PDF has 18 pages. `results/manuscript_checks.json` records 13 citation keys, 36 working citation links, 48 internal links, and no broken destinations. These are PDF link checks, not a promise that every external publisher permits unauthenticated downloads.
