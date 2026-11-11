# Paper reframe (agreed direction, 9 Nov 2026)

## Thesis
When identification becomes costly, small producers keep creating but become less visible to the institutions that distribute, preserve and measure their work. Where national ISBNs cost money, many authors take identifiers from platforms (Amazon/KDP) instead, so they are visible to the platform but not to the national agency, the national library or national statistics.

## Structure
1. **What an ISBN is and who pays.** Agencies, prices, what the number unlocks (ordering, metadata feeds, library cataloguing, statistics). Table of fee regimes.
2. **Across countries: price vs self-publishing share (the X–Y chart).**
   - X = price of one ISBN for an individual author, converted to US dollars at PPP (World Bank PA.NUS.PPP).
   - Y (main panel) = share of new ISBNs assigned to author-publishers, CERLALC 2020 Table 4.3 / 4.1, ~18 Ibero-American countries, same definition (output/paper_pt/cerlalc_author_publisher_share.csv: Mexico 4.4%, Portugal 4.7%, Spain ~6%, … Bolivia 41%).
   - Second panel = our national bibliographies (NZ, Québec, FR, PL, EE, LV, PT, ES, DE, UK), own definitions, labelled as not strictly comparable.
   - Platform substitution: UK and US national bibliographies catch 35 and 57 Amazon-issued ISBN books in 2012 against ~24,000 on Amazon; France's 979-8 books jump from 13 (2019) to 1,229 (2020) after its fee; Germany's rise comes largely from US-block ISBNs.
   - Status: Y done for CERLALC; **X needs price research for each agency (to do)**.
3. **Portugal 2015 as the detailed case.** Subsidy withdrawn 31 Dec 2014 → €15 single ISBN, blocks €100–4,500, online-only, existing prefixes grandfathered (primary documents). Agency ISBNs to self-publishers −38%, deposits −2%, self-published books steady, share without ISBN 39% → 50%; DiD vs small publishers +13.9 pp; synthetic control and forecasts agree. Wording: "shows", "consistent with", not "proves". Bundled with online form.
4. **What happens when an author does not buy a national ISBN: three routes.**
   - 4a **No ISBN at all.** Less discoverable: Google Books found 3.7% vs 8.3% (self-published, no ISBN vs ISBN). To do: larger sample + regression with controls (year, genre/UDC, pages, publisher type), title+author matching for both groups.
   - 4b **Author-service / vanity publishers** that supply the ISBN for a fee. Portugal: service imprints rise from 1.6% (2010) to 11.2% (2015) of ISBN books. To do: compile sources on costs and practices (e.g., Writers' Guild 2024 report already in data/raw/evidence; ALLi watchdog; Portuguese press on Chiado) — only verified sources.
   - 4c **Amazon/platform ISBN.** Identifier tied to the platform ("Independently published"), not in national bibliographies (numbers above), self-publishers ineligible for Library of Congress CIP (official LoC page). To do: KDP free-ISBN terms (primary page), portability limits.
5. **Why it matters: measurement → decisions.** Only documented examples: ISBN-based cross-country statistics (CERLALC ranks countries by ISBNs per 10,000 people), Bowker self-publishing figures, library/CIP eligibility. To do: find verified cases where rules, prizes, lending remuneration, grants or acquisition depend on ISBN registration. Do not claim a policy would have differed unless a source says so.
6. **Long-run consequences** (argued, labelled as such): gaps in the national record and preservation, research datasets built on ISBNs, under-recognition of independent authors.
7. **Limits.** Cross-country levels not comparable; one detailed case; fee and form bundled; visibility ≠ sales; AI-labelled data; unverified items listed.

## Not to use without a source
- "Self-published books are omitted from the public domain" — not found in project files or searches; origin unknown.

## Order of work
1. X–Y chart: collect single-ISBN prices for CERLALC countries + PPP factors.
2. Visibility regression (4a) with controls on a larger Google Books sample.
3. Source compilation for 4b, 4c and 5.
4. Rewrite the draft in this structure; move older material (Spain/France event studies, mechanism tests) to an appendix.
