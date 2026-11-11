# METHODS

Descriptive study. No causal claims. Run order: see README.md for the run order (scripts are in `src/`). Run with `.venv/bin/python -I`. `data/raw/` is never modified; provenance is in `data/raw/SOURCES.md` and `download_manifest.jsonl`.

## 1. Background facts (and what they did to the design)

| # | Question | Finding | Source |
|---|---|---|---|
| 1 | NZ ISBNs free? | Yes. National Library allocates ISBNs "at no cost" to eligible NZ-based registrants. I did not find a charging period; the 2006 documentation I saw also says free. | https://natlib.govt.nz/publishers-and-authors/isbns-issns-and-ismns/terms-and-conditions-international-standard-number-service |
| 2 | UK prices | Nielsen charges. Current (2026 page): £93 single, £174 for 10, £387 for 100, £994 for 1000. **Price history by year NOT collected** (Wayback Machine not fetchable here); third-party pages give £89 single/£164 for 10/£369 for 100 (VAT incl., c. 2019), i.e. no clear upward trend; only 2011 and 2018 Nielsen guidance PDFs saved in `data/raw/evidence/`, not yet extracted. UK has charged throughout the study window. | `data/raw/evidence/nielsen_prices.html` |
| 3 | France (AFNIL) | **ISBNs were free until 8 March 2019**, when application fees began. So France was NOT a "paid" country in the main window. Extra services (supplementary lists, new segments) stayed free. | `data/raw/evidence/afnil_history_2019.html`, `afnil_tarification.html` |
| 4 | Québec (BAnQ) | Free for eligible francophone Canadian publishers and self-publishers (Canada.ca and BAnQ guides). Start date of the free policy not established. | https://www.canada.ca/en/library-archives/services/publishers/isbn/about.html ; `qc_isbn_guide.pdf` |
| 5 | BNB selection policy | **Not established.** A web search found no published policy on print-on-demand / self-published inclusion. Large UK shifts (see caveats) may reflect selection changes. | — |
| 6 | BnF self-publishing statistics | Collected: `output/selfpub/bnf_official_benchmarks.csv` (author-depositor share of printed books deposited, 2009–2020, from Observatoire du dépôt légal workbooks). | `data/raw/evidence/Observatoire DL *.xls` |
| 7 | Legal deposit covers self-published? | BnF: yes, and says self-publishing is ~25% of deposited books today (`bnf_selfdeposit.html`). NZ: stated yes. UK: legal deposit applies to all publishers incl. print-on-demand (BL page saved). Québec: legal deposit duty on publishers, within 7 days (BAnQ form). Compliance in practice is not measured. | evidence folder |

**Consequence:** the original "paid vs free" framing holds for UK vs NZ for the whole window. For France vs Québec it holds only from 2019; 2010–2018 compares two free regimes. Results are reported in both periods.

## 2. Data

| Source | File | Notes |
|---|---|---|
| NZ | Publications NZ MARCXML (Sep 2026), 613,748 records | CC-BY 3.0 NZ |
| UK | BNB Linked Open Data, books, **May 2018** RDF (British Library repository), 3.66M records | Handoff's "2014 dump" was outdated. CC0. |
| France | BnF retrospective UNIMARC bulk files (28 files, Jan 2026), 2.78M records | Licence Ouverte. One record lacked 001 (surrogate ID kept; `bnf_parse_errors.json`). |
| Québec | BAnQ legal-deposit ISBN CSV (Données Québec), enriched with full catalogue descriptions from BAnQ annual bibliographies (166,083 records) | 74 malformed rows kept in `banq_malformed_rows.jsonl`. CSV has no carrier codes; format inferred from physical description. Contains non-Québec places and non-book material; filtered via place names (`config/quebec_place_names.txt`, GeoNames) and format audit (`qc_geography_format_audit.csv`). |

## 3. Population

- One row per valid ISBN-13 (checksum validated; ISBN-10 converted). Qualifier text never concatenated to the number (regression test).
- Country of publication: NZ 008=nz; UK via publication-country links (Ireland/imports dropped); FR via 102/place; QC via place decisions.
- Print only: language material, monograph; excludes ebook/epub/pdf/kindle/online/audio/music/map/serial signs, including from ISBN qualifiers.
- Duplicates: one row per ISBN, preferring eligible-country, published, print, most complete record.
- Years 1995–2022 classified. Analysis windows: **UK/NZ 1995–2014** (BNB 2015+ is incomplete: May-2018 snapshot, 2017–18 nearly empty); **FR/QC 2010–2021** (France 2022 is clearly incomplete: 62.9k vs ~77k). Québec starts 2010 (source limit).
- Absolute completeness cannot be measured from one snapshot, so `coverage.csv` reports ratios only and `absolute_completeness_estimate` is blank by design.

## 4. Definition of self-published

`self_pub = author_is_publisher OR service_imprint`, both kept as columns.

- author_is_publisher: normalised personal author name equals publisher (either order), publisher contains full author name, surname + family/trust, compatible initials (K. Brown ↔ Brown, Kay; same surname, compatible given names, ≥1 actual initial), or explicit statement ("l'auteur", "à compte d'auteur", "published by the author"). Single-token names never match. Corporate authors = publisher flagged separately (`corporate_self`), not counted.
- service_imprint: `config/selfpub_services.csv` (43 patterns, tiers platform / author_services / vanity, with evidence URLs and active years; `scope=mixed` imprints are only in a sensitivity variant).
- Compatible-initials matches are ~⅓ of author=publisher matches. Spot-checked, they are overwhelmingly genuine ("K. Brown" publishing Kay Brown).

## 5. Validation (limited — read this)

`output/selfpub/validation_<source>.csv` hold 200 flagged + 200 unflagged ISBNs per source (deterministic hash sample); gold-label columns are intentionally blank.
I did a **record-only read** (no web lookups) of 25 flagged + 25 unflagged per source (200 records):
- Flagged: no clear false positives; ~5 borderline sole-trader/company imprints (e.g. "Annabel Langbein Books", "Gestion Nicole Benoît inc.").
- Unflagged: UK and FR essentially all real publishers. NZ and QC each had a few likely misses (pseudonym authors, small imprints such as "Cultural & Political Booklets", "T. Devlin Associates", pseudonym "Val-Bleu"→"Valérie Jacques-Bélair"). Rough recall guess NZ ~80–90%, others higher. **This is a small non-independent sample, not a precision/recall estimate.** Needs human review.
- NZ ISBN pool check (978-0-473 / 978-1-06): flag rate inside pool 27–38%, outside 2–7%. Pool is 13% of NZ print ISBNs in 2005 rising to 50–57% in 2020–21, so overlap is high but far from identical (pool also contains small non-self publishers).
- France benchmark: our author=publisher share correlates r=0.96 (2009–2020) with BnF's author-depositor share, at ~⅔ of its level (BnF counts depositors, we count name matches). Our combined share (with services) correlates only 0.65, because service-imprint counts are volatile (below).

## 6. Sensitivity variants (all in `sensitivity_by_year.csv`)

main; author_only; services_only; author+platform; exclude vanity; include mixed-contract imprints; exclude government/standards; exclude theses; exclude reprints/new editions; all four; exclude initials-only; include contributor matches; exclude unidentified publisher; title-author groups instead of ISBNs.

## 7. Known biases and open problems

1. **UK AuthorHouse/Xlibris drop after 2011–12 is a place-of-publication effect, resolved.** AuthorHouse records in the BNB fall from 1,112 UK-place (Milton Keynes) in 2009 to 40 in 2013, while records placed in Bloomington, IN rise from ~43 to 1,010. The BNB still catalogues them (probably because distributed in the UK), but they fail our UK country filter. So the UK share fall after 2011 reflects imprints moving their stated place to the US, not UK authors stopping. A UK-based author could not be separated from these records. Treat the UK 2012+ share as a lower bound on UK authors using services. Check (`uk_place_sensitivity.py` → `output/selfpub/uk_service_place_sensitivity.csv`, record-level, denominator includes non-UK places): service-imprint records are 1.8–2.3% of BNB print records in 2011–2014 regardless of place, versus 0.7–1.6% when restricted to UK place; the service tail does not disappear.
2. **UK 2004–05 dip** (52k vs 67k in 2003) and **2015+ truncation** are unexplained/snapshot effects.
3. **France service counts are dominated by Édilivre**, whose records fall from ~6,100 (2015) to 875 (2017), then 4,272 (2018); this produces the 2016–17 dip. ISBN blocks show Édilivre's 978-2-334 series ended in 2016 and 978-2-414 began in 2017, but the gap size is unexplained (cataloguing backlog or real). Do not read 2014–2018 France levels as real trend; the author=publisher series is the steadier one.
4. Service lists are drawn from named platforms; unknown small services are missed, particularly in NZ/QC.
5. BnF and BNB record **cataloguing**, not publishing; selection and lag differ by country, so levels are not comparable across countries, only within-country trends.
6. Québec is a strict subset (matched bibliography + identifiable Québec place); comparisons treat it as a sample.
7. US 979-8 ISBNs (Amazon KDP since 2020) are counted in `amazon_and_nz_prefix_context.csv` as *not proof of Amazon*. They are 1,229–1,668/yr in France 2020–21 and ~60/yr in Québec, ~35/yr NZ — authors bypassing national agencies, mostly outside our flag.
8. Price history (item 2 above), BNB selection policy (5) and Québec free-ISBN start date (4) remain open.

## 8. Added 2026-11-01: US data and econometrics

- **US = two imperfect sources.** `build_loc.py`: Library of Congress MDSConnect BooksAll 2016 (MARC21, 43 part files; the 2 GB 'combined' file is truncated at 2^31 bytes by the server, so parts are used). Country filter: 008/15-17 ends in 'u'. Window 1995–2011 only (cataloguing lag in the 2016 snapshot). `build_amazon.py`/`build_amz_catalogue.py`: Amazon Reviews 2023 Books metadata (McAuley Lab; 4.45M products). Print = has Paperback/Hardcover/Mass-market etc. and none of Kindle fields. No country; year parsed from the Publisher string or publication-date field. Unit: ISBN-13, deduped.
- **Service list extended** with 17 US imprints (`sources=us`), evidence URLs are Wikipedia pages not fetched in this run.
- **AFNIL fee dose:** the only AFNIL tariff retrieved is the 2025 page: €37 excl. VAT dossier fee for a first ISBN request (standard, 3 weeks), €28 for a further list. It is a lump sum, not per ISBN. The 2019 amount is not documented here.
- **Statistics** (`econ_*.py`): two-unit comparisons use the log-odds gap series with Newey–West/permutation inference; multi-country DiD uses binomial GLM with year fixed effects, quasi-binomial scale, year-clustered SEs and a year-block bootstrap. Unknown-break tests are sup-F with residual bootstrap p-values. Population series (`config/population_millions.csv`) are rounded approximations from memory, linearly interpolated: replace with official figures before publishing per-capita numbers.
- Results and interpretation: ECON_RESULTS.md.
