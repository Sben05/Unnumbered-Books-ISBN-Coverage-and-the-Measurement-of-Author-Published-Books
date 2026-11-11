# Unnumbered Books

**ISBN Coverage and the Measurement of Author-Published Books in Portugal**  
Shreeniket Bendre · Working paper, November 2026

[Read the current paper](deliverables/UNNUMBERED_BOOKS.pdf) · [Edit the LaTeX](deliverables/UNNUMBERED_BOOKS.tex) · [Replication notes](docs/REPLICATION.md)

This paper compares ISBN-bearing books with all books classified as author-published in Portugal's national bibliography. Its main result is an accounting decomposition of changing identifier coverage. Independent human classification validation remains outstanding; the paper does not identify a causal fee effect.

## Where things are

| Folder | Contents |
|---|---|
| `deliverables/` | The current manuscript and PDF. Start here. |
| `analysis/` | Code for the current paper, compilation, and PDF checks. |
| `inputs/` | Frozen, compact record-level input used by the current analysis. |
| `results/` | Numerical outputs, manuscript tables, and verification reports. |
| `figures/` | The current paper's three figures, in PDF and PNG. |
| `validation/` | Blank blinded coding sheets, protocol, and scoring instructions. |
| `provenance/` | Policy documents, inherited numerical inputs, and their hash manifest. |
| `docs/` | Replication details, checks, revision notes, and source research. |
| `src/`, `config/`, `tests/` | Earlier acquisition/classification pipeline and its regression tests. |
| `archive/` | Superseded drafts and historical notes. See its index. |

The large raw/intermediate datasets in `data/`, older outputs in `output/`, the local Python environment, old draft bundles, and private validation key are kept locally and excluded from Git. The GitHub repository includes the compact input needed to reproduce the current analysis.

## Reproduce the paper

Python 3.9 or later and [Tectonic](https://tectonic-typesetting.github.io/) are required. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
make reproduce
```

`make reproduce` runs the direct analysis, regenerates five numerical tables, compiles the manuscript, and checks PDF citations and cross-references. The population-reconciliation table is supplied frozen; regenerating it requires the original processed source files. Tectonic may download TeX resources on its first run.

To compile only after editing the manuscript:

```sh
make paper
make check
```

The current source is always `deliverables/UNNUMBERED_BOOKS.tex`; there is no separate "revised" draft to choose between. Run scripts from any directory, or use Make from this root.

## Validate the classification

Read [the protocol](validation/PROTOCOL.md) before giving a coder either sheet. The 800-record pilot is a subset of the 2,000-record full design. Do not combine them as independent samples. The local `DO_NOT_SHOW_CODERS_key.csv` is intentionally not published. Completed human labels have not been supplied or fabricated.

```sh
.venv/bin/python analysis/score_validation.py path/to/completed_labels.csv
```

Scoring requires the private key and complete adjudicated labels. See [replication notes](docs/REPLICATION.md) for weighting, uncertainty, and the limits of the frozen-data replication.

## Earlier research pipeline

The scripts in `src/` retain their source/data directory structure. They support the earlier multi-country research and require additional dependencies and locally archived data. They are not part of `make reproduce`. To run their existing classification tests:

```sh
.venv/bin/python -m pip install -r requirements-pipeline-tests.txt
make test
```

Older report assemblers write to `archive/`, so they do not replace the current paper. [The archive index](archive/README.md) explains where earlier drafts and logs went.

## Sources and reuse

BNP's public dataset listings identify the underlying bibliographic metadata as CC0. Preserve source attribution and the distinction between supplied metadata, derived classifications, and original scholarship. Included policy documents retain their underlying rights. This repository does not assign a blanket licence to third-party materials or to the manuscript.
