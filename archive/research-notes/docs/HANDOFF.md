# Handoff: self-publishing share, UK vs NZ and France vs Québec

## Goal

Measure the yearly **share of self-published print-book ISBNs** in two country pairs. In each pair, one place's ISBNs cost money and the other's are free (fees still to be confirmed in step 1):

| Pair | Paid ISBNs | Free ISBNs | Data on each side |
|---|---|---|---|
| A | UK (Nielsen) | New Zealand (National Library) | British National Bibliography ↔ NZ national bibliography |
| B | France (AFNIL) | Québec (BAnQ) | BnF national bibliography ↔ BAnQ legal-deposit dataset |

The question: does the self-published share rise faster where ISBNs are free? The study is **descriptive only**, so make no causal claims.

### Decisions already made by the user

1. Pairs: UK vs NZ, and France vs Québec.
2. Unit: **one row per print-book ISBN**. Exclude ebooks, audiobooks, music, maps and serials.
3. **Self-published** = the publisher is the same as an author, **OR** the publisher is a self-publishing service. Keep both parts as separate flags, then combine them.
4. Historical focus for now. Recent Amazon/KDP-era years are out of scope.

## 0. What already exists in this repo

- `.venv/`: Python 3.9 environment with `datasets`, `duckdb`, `pandas`, `isbnlib` and `huggingface_hub`.
- `data/raw/`: original downloads. **Never modify these.** Put each new source in its own folder here.
  - `open-library/`: OpenLibrary editions, Feb-2026 dump (56 Parquet files). Not needed for this study.
  - `natlibnz/pubsnzmetadataxml.zip`: NZ National Library "Publications NZ" MARCXML, Sep-2026, 613,748 records. Licence: CC-BY 3.0 NZ, which requires credit.
- `data/interim/nlnz_records.parquet`: one row per NZ record. Produced by `build_nz.py`.
- `build_2025.py`: shared helpers. Reuse these, don't rewrite them:
  - `clean_isbns`: hyphen stripping, checksum validation, ISBN-10 → ISBN-13
  - `isbn13_valid`
  - `as_list`
  - `clean_publishers`
- `build_nz.py`: streaming MARCXML parser. Use it as the template for any other MARC source. Run with `.venv/bin/python -I build_nz.py`, because downloaded files are untrusted (`-I` is Python's isolated mode).
- `selfpub_by_year.py`: an unrun draft. Its "small publisher block" measure is **not** the user's definition. Replace it or delete it.

### Known facts and pitfalls from earlier work

- **NZ completeness:** NZ data is good from 1990 to 2022. 2023–24 are about 70–77% of normal volume, and 2025+ is badly incomplete, because the National Library's cataloguing rate fell sharply in 2025–26.
- **NZ creation dates:** the record-creation date (008/00-05) is distorted by an apparent 2016 system migration (145k records carry that year), so don't use it to measure cataloguing lag.
- **NZ self-publisher block:** NZ's ISBN block 978-0-473 appears to be the agency's pool for small and self-publishers. From 2024 a new block, 978-1-06, appears. Use these blocks to *validate* the self-publishing flag, not to define it.
- **Non-book records in NZ:** these include ~370 standards documents a year (Standards NZ / Standards Australia), plus sound recordings, music and maps that also carry ISBNs.
- **Amazon ISBNs:** a 979-8 ISBN or a CreateSpace ISBN is US-issued, wherever the author lives. Count these per country and year; they show authors in that country using Amazon instead of their own agency.

## 1. Confirm the background facts first

Record each answer, with a source URL, in `METHODS.md`. The country-pair logic depends on them.

1. Were **NZ ISBNs free** throughout the study years? Has the National Library ever charged?
2. **UK ISBN prices** over time. Nielsen sells single ISBNs and blocks of 10, 100 and 1,000. When did charging start, and what were the prices by year?
3. **France:** the AFNIL fee structure and its history.
4. **Québec:** are BAnQ's ISBNs free, since when, and are publishers eligible?
5. **British National Bibliography selection policy:** does it include self-published and print-on-demand books, or exclude any categories? Did that change over time?
6. **BnF self-publishing statistics:** the BnF's legal-deposit monitoring reports publish yearly self-publishing ("auto-édition") shares. Collect them per year; they're the benchmark in step 6.
7. **Legal deposit:** does it cover self-published books in each of the four places? It is stated to for NZ.

## 2. Get the data

Save each source in `data/raw/<source>/`. Add a row to `data/raw/SOURCES.md` with the URL, download date, licence, file names and checksums.

| Source | Where | Notes |
|---|---|---|
| NZ | already downloaded | — |
| UK: British National Bibliography | data.gov.uk "Linked Open British National Bibliography" (British Library) | The books dump is from Feb 2014 (N-Triples / RDF-XML), so coverage is up to about 2013. Check the British Library Research Repository for a later books dump (2018 forthcoming-books files are known to exist; those are *planned* books and must be kept separate). CC0 licence. If something newer is needed, email `metadata@bl.uk`. |
| France: BnF national bibliography | "BnF API et jeux de données" (api.bnf.fr) | Find the bulk book-record downloads (UNIMARC or Intermarc). The SRU API at catalogue.bnf.fr is the fallback. Check the licence (likely Licence Ouverte). |
| Québec: BAnQ | Données Québec, BAnQ legal-deposit / publications CSV (2010–present, updated weekly) | Download its data dictionary too. Coverage starts in **2010**. |

Before parsing a whole file, look at a small piece of it: the format, the record count, the year range, and which fields exist. Fields to look for:
- ISBN, title, author(s), publisher(s), place, year
- physical format / carrier, so print can be told from ebook
- record type
- language

## 3. Parse every source into one common format

Write one `data/interim/<source>_records.parquet` per source, with these columns:

`source, record_id, country_code, pub_year, isbn13 (one row per valid ISBN), isbn_qualifier, title, authors_personal (list), authors_corporate (list), publishers (list), place, record_type, bib_level, carrier, language`

Where each field comes from:
- **MARC 21** (NZ, BNB if it's MARC):
  - `020$a` ISBN, `020$q` qualifier (pbk / hbk / ebook / epub / pdf)
  - `100`/`700` personal names, `110`/`710` corporate names
  - `245` title
  - `260`/`264#1` `$a` place, `$b` publisher, `$c` date
  - `008`/07-10 year, `008`/15-17 country of publication
  - leader/06 record type, leader/07 bibliographic level
  - `007` (`cr` = online), `338` carrier, `300` physical description
  - **Extend `build_nz.py` to capture `100/700/110/710`, `020$q`, `007`, `338` and `300`. Its current parser doesn't keep author names, which the author = publisher test needs.**
- **UNIMARC** (BnF):
  - `010$a` ISBN (`$b` qualifier)
  - `100` dates, `102` country
  - `200$a` title
  - `210`/`214` `$a` place, `$c` publisher, `$d` date
  - `700`/`701`/`702` personal names, `710`/`711`/`712` corporate names
  - `135` / `181`–`183` content and carrier
- **BNB RDF:**
  - `bibo:isbn13` / `bibo:isbn10`
  - `dct:title`
  - `dct:creator` / `dct:contributor`, followed to the person's name
  - `blt:publication`, which is an event node: `event:agent` is the publisher, `event:place` the place, `event:time` the year
  - format and medium properties
  - Parse by streaming; the files are large.
- **BAnQ CSV:** follow its data dictionary.

## 4. Filter to the study population

1. **Country of publication**
   - NZ: `008` country = `nz`.
   - BNB: UK only. Drop Ireland using the place / country code.
   - BnF: France (`102` = FR, or the place).
   - Québec: published in Québec. Check that the BAnQ file doesn't include the rest of Canada or other countries.
2. **Print books only:** language material (leader/06 = `a`), monographs (leader/07 = `m`), and none of these signs of an ebook: `007` = `cr`, `338` = online resource, or a `020$q` saying ebook / epub / pdf / kindle. Drop audio, music, maps and serials.
3. **Years**
   - UK vs NZ: about 1995–2013, ending where the BNB dump ends.
   - France vs Québec: 2010 to the latest year that is complete in **both** sources.
   - Measure completeness per year in step 7 before fixing the end year.
4. **Duplicates:** keep one row per ISBN within each source. If an ISBN has several records, keep the most complete one and keep its record ID.
5. **Possible exclusions:** decide with the user, and report results both ways:
   - government publications
   - standards documents
   - theses
   - reprints and new editions

## 5. Classify each ISBN as self-published

Keep every part as its own column. Final rule: `self_pub = service_imprint OR author_is_publisher`.

### 5a. Self-publishing service list (`config/selfpub_services.csv`)

Columns: `name_pattern, country/language, tier, evidence_url`.

- `tier` takes one of these values:
  - `platform`: pure self-publishing platforms
  - `author_services`: author pays, with professional services
  - `vanity`: subsidy publishers, "à compte d'auteur"
- Report results with and without the `author_services` and `vanity` tiers.

Starting candidates. Verify each one before adding it.

- **English:** CreateSpace; Independently published; BookSurge; Lulu; AuthorHouse; Xlibris; iUniverse; Trafford; Matador / Troubador; Grosvenor House; New Generation Publishing; FeedARead; CompletelyNovel; Authors OnLine; UPfront; YouCaxton; SilverWood; Mereo; Clink Street; Austin Macauley (vanity/hybrid); Olympia (vanity/hybrid); Pegasus (vanity); Book Guild (hybrid).
- **NZ-specific:** find these empirically. Candidates include Copy Press, Mary Egan Publishing and Bookprint-type services.
- **French:** BoD (Books on Demand); Edilivre; Les Éditions du Net; Publibook; Librinova; TheBookEdition; Société des Écrivains; Lulu; Amazon / CreateSpace / Independently published; plus "à compte d'auteur" publishers.
- **Québec-specific:** find these empirically.

How to grow the list: for each source, list publishers that have **many distinct authors, mostly one title each**. Review the top candidates by hand, with a web check.

### 5b. Author = publisher (`author_is_publisher`)

- **Normalise names:** lowercase; remove accents and punctuation; swap "Surname, Forename" to "Forename Surname"; drop dates and roles; drop words like Ltd, Limited, Publishing, Publications, Press, Books, Éditions and Editions.
- **Count a match when:**
  - the normalised publisher equals any normalised personal author name (in either word order), or
  - the publisher contains the author's full name, or
  - the publisher is the author's surname plus a family word such as "family" or "trust".
- **Also match explicit statements:** "the author", "published by the author", "self-published", "l'auteur", "chez l'auteur", "à compte d'auteur", "auto-édition".
- Use **personal** authors only. A government department or society that is both author and publisher is not self-publishing; flag those separately as `corporate_self`.
- **Edge cases to handle explicitly:**
  - initials (J. Smith vs John Smith)
  - several authors
  - editors and illustrators
  - Māori and French name forms
  - publisher strings that list several names

### 5c. Check how accurate the flags are

1. **Hand-check a sample:** for each source, randomly pick 200 ISBNs that are flagged and 200 that aren't. Label them by hand using the record and a web lookup. Report precision and recall, i.e. how many flagged books really are self-published and how many self-published books get caught. Save the samples as `output/selfpub/validation_<source>.csv`.
2. **NZ:** compare the flag against the 978-0-473 / 978-1-06 blocks. Expect high overlap but not identical results; describe what's different.
3. **France:** compare the yearly trend with the BnF's published self-publishing shares from step 1.6. Our level may differ because our definition differs, but the trend should broadly match.
4. Improve the rules and the service list, then re-check. Log every change in `METHODS.md`.

## 6. Coverage and quality report

Write `output/selfpub/coverage.csv`, plus a short summary, for each source and year:
- total records
- the share with an ISBN
- the share left after the print filter
- the share with a publisher
- the share with a personal author
- duplicate ISBNs
- and an estimate of completeness

Flag years affected by cataloguing delay or by the dump cutoff.

## 7. Analysis

1. **Per pair, country and year:** count print ISBNs, compute the self-published share (combined, and each part separately), and add a 95% Wilson confidence interval.
2. **Charts:**
   - UK vs NZ over the shared window.
   - France vs Québec over the shared window.
   - Mark the dates of any ISBN fee changes found in step 1.
3. **Growth:** compare the trend over time for each country (the slope of share against year), and the change between early and late windows. Keep it descriptive.
4. **Sensitivity checks**, reported side by side:
   - the service list with and without the `author_services` and `vanity` tiers
   - author = publisher only, versus services only
   - with and without government and standards publications
   - counting titles instead of ISBNs (group by normalised title + author)
5. **Context table:** per country and year, count ISBNs that are Amazon or CreateSpace (979-8, CreateSpace blocks, "Independently published" imprints). These are authors in that country using US-issued Amazon ISBNs, which partly bypasses the national agency.

## 8. Outputs

- `output/selfpub/<pair>_by_year.csv`
- `output/selfpub/coverage.csv`
- `output/selfpub/validation_*.csv`
- `output/selfpub/figures/*.png`
- `config/selfpub_services.csv`
- `METHODS.md`: the facts from step 1, every definition and filter, rule changes, known biases.
- One script per stage, in the style of the existing ones:
  - `build_<source>.py` for each source
  - `classify_selfpub.py`
  - `analyze_selfpub.py`
  - Each should be re-runnable, and none should modify `data/raw/`.

## 9. Questions to raise with the user along the way

- Exclusions in step 4.5: should government publications, standards, theses and reprints stay in?
- Should `author_services` and `vanity` count as self-published in the main result, or only in the sensitivity checks?
- If the BNB dump stops at about 2013, is that enough, or should we ask the British Library for a 2014–2022 extract?
- Should we later add titles counted per author, or first-time publishers, as extra measures?
