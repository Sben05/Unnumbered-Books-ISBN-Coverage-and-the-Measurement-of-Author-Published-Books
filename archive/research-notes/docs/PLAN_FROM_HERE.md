# Plan from here (2026-11-09, after the user's downloads)

## Where the evidence stands (all descriptive)
| Source (independent of each other) | 2013 | 2014 | 2015 | 2016 | 2017 | What it measures |
|---|---|---|---|---|---|---|
| CERLALC T4.3: ISBNs to author-publishers | 718 | 988 | 617 | 606 | 884 | agency assignments (category definition unknown) |
| CERLALC T4.1 / APEL: all ISBNs | 19,060* | 25,000 | 18,715 | 18,367 | 19,155 | agency assignments (incl. PALOP) |
| Pordata/BNP: legal-deposit monograph registrations | 15,284 | 16,841 | 16,530 | 16,138 | 15,724 | printer-requested deposit numbers, no ISBN needed |
| BNP national bibliography: AP books, total | 313 | 392 | 343 | 323 | 359 | self-published books, with or without ISBN |
| … of which without ISBN | 128 (41%) | 152 (39%) | 172 (50%) | 165 (51%) | 165 (46%) | |
| … all other books without ISBN | 10.1% | 10.0% | 10.7% | 11.8% | 10.7% | comparison group, same catalogue |
| BNP: books on author-edition prefixes 989-20/33 | 386 | 381 | 440 | 441 | 487 | agency category as catalogued |
*APEL 2014 report. Files: output/paper_pt/natbib_isbn_by_ap_year.csv, data/raw/cerlalc, data/raw/pordata, data/raw/apel.

Reading: agency ISBNs to self-publishers fall sharply in 2015; deposited self-published books do not; the share of them without an ISBN jumps (largest one-year rise in 2005–25) while other books barely move. **Unresolved:** catalogued author-edition-prefix books rise while CERLALC's author-publisher ISBNs fall; and the 2014 spike appears in every series.

## Thesis to pursue
Charging for an identifier shifted small producers off the identifier rather than out of production (the "visibility margin"). Frame as formalisation costs and informal production, not as a book-market curiosity.

## Steps, in priority order
1. **Reconcile the agency numbers (2–3 days).** CERLALC vs APEL (2018: 17,912 vs 18,627; the round 25,000 in 2014); what CERLALC counts as "autor-editor"; whether PALOP is included; stockpiling test (989-20 serials vs cumulative assignments: 3,692 by Jan 2014 + 988 + 617 …). If the serial frontier outruns cumulative assignments, the categories differ.
2. **Human labels (1 week, the step only a person can do).** ~300 national-bibliography records, 2013–2017, stratified by AP × ISBN present; check whether no-ISBN AP books are truly self-published and whether ISBNs are missing from the record but printed in the book (spot-check physical copies or retailer listings).
3. **Centrepiece design: within-catalogue difference-in-differences, book level.** Outcome: no ISBN. Groups: self-published (AP + author-edition statements) vs established publishers, same cataloguers, same years. Event-study coefficients by year with pre-period shown; inference by randomisation over placebo years plus wild bootstrap clustered by year. Be explicit that the AP no-ISBN share was falling before 2015, so the claim is a trend reversal.
4. **Exposure heterogeneity (strongest identification idea).** Producers who already held a prefix with unused numbers before 2015 faced no new cost; first-time self-publishers faced €15 (+€25 registration if it applied). Compare post-2015 no-ISBN rates for repeat self-publishers with pre-2015 prefix stock vs first-timers. Data: BNP author × prefix history (first use of each registrant prefix), APEL prefix list.
5. **Visibility consequence.** Match AP books with and without ISBN to retailers (Wook/Bertrand), Google Books, Open Library and library holdings. Shows whether dropping the ISBN cost market reach; this is the economics, without it the paper is about cataloguing.
6. **Replication: Spain 2012** with the same within-catalogue design (BNE data already in data/interim/es_*). Two fee events with the same pattern turn a case into a result.
7. **Short model.** Author chooses produce/no and ISBN/no; fee F vs distribution value v. Predicts low-v books (poetry, memoir, local history, short runs) drop the ISBN first; test with UDC/extent.
8. **Send the APEL/BNP data request** (deliverables/DATA_REQUEST_APEL_BNP_DRAFT.md), now citing these numbers.

## Honest ceiling
With 1–7 done well, a strong field or applied journal is realistic. A top-five submission needs the visibility consequence (5), the exposure design (4) and a replication (6) all to hold, plus a broader formalisation framing.

---
## Revision after the 2026-11-09 afternoon tests (no data request)
**Test results.** APEL's per-prefix usage counts are not public (login only). Widening the capacity design to all publishers adds no power. The legal-deposit running number works as a printing-time clock and shows the self-published no-ISBN share stepping up at the fee date (H2-2014 40% → H1-2015 50%), but each half-year has only ~150 books. Mechanism tests do not line up: same-author change is null, and repeat self-publishers respond more than first-timers (opposite of "entrants pay"). See output/paper_pt/WORKLOG.md.

**Revised strategy, in order:**
1. **Lead with the measurement result, which is robust.** For the same 2014→2015 change, the agency's self-publisher ISBNs fall 38%, legal deposit falls 2%, catalogued self-published books do not fall, and the share of them without ISBN rises ~10 points against a flat comparison group. Claim: identifier-based statistics misread small-producer output when identifiers are priced. This needs no behavioural identification.
2. **Same four-source comparison for Spain (2012) and France (2019).** Spain: BNE catalogue (have), INE legal-deposit book production tables (public), Panorámica de la edición española (agency, incl. author-editors; public). France: BnF catalogue (have; re-parse keeping ISBN-less records), BnF dépôt légal observatory (author-depositor shares already extracted in output/selfpub/bnf_official_benchmarks.csv). Three events → a general result.
3. **Visibility outcome.** Match self-published books with and without ISBN to Porbase (Portuguese union catalogue; library holdings), Open Library (CC0 dump), Google Books, Amazon Reviews 2023 (have). Shows whether dropping the ISBN costs reach.
4. **Human check of ~300 records** (2013–17, AP × ISBN). Especially: is the post-2015 rise in AP no-ISBN records a cataloguing-recording change?
5. **Mechanism, honestly.** Test the "3-ISBN author-edition cap pushes repeat self-publishers onto a €150 block" story (authors' prior 989-20 counts); report all nulls (capacity, same-author, entrants).
6. **Freeze primary outcomes now**; everything else labelled exploratory, with the full list of tests run.
