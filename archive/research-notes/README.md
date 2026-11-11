# ISBN self-publishing study (UK vs NZ, France vs Québec, US)

Does the cost of a national ISBN go with how much authors self-publish? Descriptive study using national bibliographies (legal deposit) plus the Amazon catalogue.

## Read these first
- [RESULTS.md](RESULTS.md): every result, table and figure.
- [METHODS.md](METHODS.md): sources, definitions, filters, validation, known biases.
- [docs/MODEL_SPECS.md](docs/MODEL_SPECS.md): regression specifications and what causal claims they can carry.
- [deliverables/](deliverables/): `ISBN_selfpub_review_bundle.pdf` (single upload-ready file) and the Markdown versions.

## Layout
```
README.md  RESULTS.md  METHODS.md
docs/          HANDOFF.md (original plan), REPORT.md and ECON_RESULTS.md (narratives that feed RESULTS.md), MODEL_SPECS.md
deliverables/  review bundle PDF + Markdown
src/           all pipeline code (run from anywhere; paths resolve from the repo root)
tests/         regression tests for ISBN parsing and name matching
config/        selfpub_services.csv (service imprint list), quebec_place_names.txt, population_millions.csv (approximate)
data/raw/      original downloads, never modified; SOURCES.md and download_manifest.jsonl give provenance
data/interim/  parsed Parquet files per source (<source>_catalogue / _records / _classified); _scratch/ = regenerable intermediates
output/selfpub/  all result CSVs, figures/, validation_*.csv (blank gold labels), logs/
archive/openlibrary_2025/  first-phase OpenLibrary 2025 work, not used in the final study
.venv/         Python environment
```

## Run order (always `.venv/bin/python -I src/<script>.py`)
1. Acquire: `acquire_selfpub.py`, `acquire_bnf.py`, `acquire_banq_bibliography.py`, `collect_evidence.py`, `extract_bnf_benchmarks.py`
2. Parse to common schema: `build_nz_selfpub.py` (NZ; uses `build_nz.py`, `build_2025.py` helpers), `build_bnb.py` (UK), `build_bnf.py` (France), `build_banq.py` + `enrich_banq.py` + `finalize_banq.py` (Québec), `build_loc.py` (US LoC), `build_amazon.py` + `build_amz_catalogue.py` (Amazon)
3. Classify: `classify_selfpub.py <uk nz fr qc us amz>`
4. Analyse: `analyze_selfpub.py`, `make_panel.py`, `econ_frqc.py`, `econ_amazon.py`, `econ_did.py`, `uk_place_sensitivity.py`, `econ_figures.py`
5. Write up: `make_results.py` (RESULTS.md), `make_bundle.py` (deliverables/*.md; the PDF was made from the bundle with Chrome headless)

Tests: `.venv/bin/python -I -m unittest discover -s tests`
