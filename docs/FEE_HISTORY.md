# ISBN fee history and candidate countries for a multi-country event study

Compiled 2026-11-09. Web research with source URLs. P = primary (agency, national library, statistics office, official dataset), S = secondary (blogs, trade press, how-to sites, search-engine summaries). "Unverified" means I did not see it on a page I could read.

**Tool limits that shape the gaps below.** The Wayback Machine returned HTTP 429 to curl after the first few calls and `web.archive.org` is blocked in the WebFetch tool, so no archived Nielsen/AFNIL pricing page could be read. Several national-library sites (kansalliskirjasto.fi, ifla.org, kb.se) returned 403/bot blocks. Anything that would have needed those is marked unverified. A CDX listing of `isbn.nielsenbook.co.uk` is the first thing to try if Wayback access is available from another network.

**Headline.** I could not find any country other than France (2019), Spain (2012, already in the project) and Portugal (2015, already in the project) with a documented free-to-paid change inside 2005-2022. The other countries I checked were either paid throughout (UK, Ireland, Germany, Netherlands, Chile, Brazil), free throughout (Norway, Sweden, Luxembourg, Poland, Canada/Québec, NZ), or I could not establish their history (Belgium, Switzerland, Denmark, Austria, Czechia, Finland). A multi-country fee event study with a clean free-to-paid event is therefore not supported by what I could verify. A paid-versus-free level comparison, using Germany and the Nordics as extra units, is feasible. See section 7.

---

## 1. United Kingdom (Nielsen ISBN Agency)

**When charging started: not established.** Nielsen guidance PDFs from 2011 and 2018 (saved in `data/raw/evidence/nielsen_guidance_2011.pdf`, `nielsen_guidance_2018.pdf`; P, originally from Nielsen) both mention "fees payable" and VAT treatment, so the UK charged throughout 2011-2018. Nothing I read dates the start of charging (Whitaker era or earlier). The window of interest (2005 onward) is unverified for 2005-2010.

**Prices found (single / block of 10 / block of 100 / block of 1000), all stated as UK-VAT-inclusive where the source says so:**

| Date of source | Single | 10 | 100 | 1000 | Source | Type |
|---|---|---|---|---|---|---|
| 27 Jul 2016 (page updated Mar 2022) | £99 | £149 | £352 | n/a | https://rogerpacker.com/?p=6087 | S |
| 8 Nov 2016 | £99 incl. VAT | | | | https://writersuk.blogspot.com/2016/11/nielsen-and-isbn-numbers.html | S |
| c. 2019 (undated third-party guides) | £89 | £164 | £369 | £949 | search summaries quoting the Nielsen store (see `docs/ECON_RESULTS.md`/`METHODS.md` note); not individually verified | S |
| Oct 2023 | £91 (single only) | £174 | £379 | | https://indiepressnetwork.com/2023/10 (not opened; from a search snippet) | S, weak |
| 12 Oct 2026 | £93 | £174 | £387 | £994 | Nielsen store, saved at `data/raw/evidence/nielsen_prices.html`; https://www.nielsenisbnstore.com | P |

Reading: the series is non-monotonic and roughly flat in nominal terms (£99 in 2016, about £89-93 since), so UK price variation over 2005-2024 is small and cannot serve as an event. The single-ISBN price in the Bookseller's report on the online store launch is cited as £89 in a search summary, but the article body is paywalled and I could not read it (https://www.thebookseller.com/news/nielsen-bookscan-launch-online-isbn-store-364306, dated 25 Jul 2016). The £99 vs £89 discrepancy for 2016 is unresolved.

**Online ISBN Store (Nielsen).** Announced 25 Jul 2016 (The Bookseller, headline readable, body paywalled) and reported in Jane Friedman's piece as letting UK and Ireland publishers buy ISBNs online (https://janefriedman.com/the-uk-prices-remain-high/, original 27 Jul 2016). This is an access-friction change in 2016, not a price change. It is a possible UK event for self-publishers (single ISBN purchasable in minutes), but unverified as to magnitude.

**Not obtained:** prices before 2016; any Wayback snapshot. Candidate URLs to try: `isbn.nielsenbook.co.uk` (Wayback availability API returns a 15 Mar 2019 snapshot: http://web.archive.org/web/20190315110709/http://www.isbn.nielsenbook.co.uk:80/), `www.nielsenisbnstore.com` (snapshots 25 Jun 2016, 29 Jul 2016, 9 Dec 2022 returned by the availability API). I confirmed these snapshots exist but could not read their content.

Confidence: high that the UK charged 2011-2026 and that single-ISBN prices have been £89-£99 since 2016; low on anything earlier.

## 2. Ireland

- **Issuance (P):** The National Library of Ireland says it does not issue ISBNs; publishers get them from Nielsen's ISBN Store. https://www.nli.ie/collections/using-our-collections/publishers (fetched 2026-11-09).
- **Price:** the same as the UK (Nielsen store, sterling; Irish publishers can quote euro prices on registration forms, and Irish publishers with a valid VAT number are not charged UK VAT; Nielsen 2011 and 2018 guidance PDFs, local copies). Irish ISBNs are therefore paid, with the same schedule as the UK, for the whole 2011-2026 period I could verify. No free period found.
- **Bibliographic data:** I found no bulk download or open licence for the NLI catalogue. Individual records can be exported (MARC/MARCXML) from https://catalogue.nli.ie, but no dump or data licence page turned up (S: search summary; not exhaustively checked). The BNB (CC0, covers "books published or distributed in the UK and Ireland") is the practical source for Irish-published books, and the BNB already includes them. An "Ireland control" inside BNB would share the Nielsen fee, so it is not a fee-contrast control; it is only a same-fee neighbour and would need a publisher-address filter.
- Confidence: high on Nielsen as the ISBN source; medium-high that no NLI bulk data exists.

## 3. France (AFNIL) and other countries

### 3a. France 2019

- **Date (P, official communiqué reproduced by a blog):** From Friday 8 March 2019 all AFNIL procedures went online and "pour toute première demande d'ISBN ou toute demande de création d'une nouvelle marque ... des frais de gestion de dossier s'appliquent. Les autres services liés à l'ISBN, comme une liste complémentaire ou une demande de nouveau segment demeurent gratuits." The communiqué is dated 7 Mar 2019. Reproduced at https://gaellekermen.net/2016/06/10/publication-afnil-et-isbn/ (S for the reproduction; local copy `data/raw/evidence/afnil_history_2019.html`). AFNIL's new website launched 20 Mar 2019 per the International ISBN Agency news item (P): https://www.isbn-international.org/node/318.
- **Exact 2019 amount: not verified from a primary source.** A search-summary of several how-to sites says the launch price was €25 excl. VAT (€30 incl.) for a standard 3-week first request and €50 for 2-day urgent processing (S, from https://www.afnil.org/tarification/ and how-to sites; I could not open an archived 2019 AFNIL page). Treat €25 HT as likely but unconfirmed. The current schedule (P, `data/raw/evidence/afnil_tarification.html`, https://www.afnil.org/tarification/) is €37 HT standard (€44.40 incl. VAT), €87 accelerated, €154 urgent for a first request; €28 for an additional list. The fee is a dossier fee, not a per-ISBN price, and a first request yields a 10-number list or larger (the author's blog describes receiving 50).
- **Self-publishers:** AFNIL has a separate "particulier" (individual/auto-éditeur) form; the fee wording is "première demande d'ISBN (société ou particulier)" in the current schedule (P, local copy), so it applies to self-publishers at the same level as companies. Before 2019, free for both.
- **Consequence for the project:** a one-off €25-37 fee is small relative to the UK's £90+ single ISBN, consistent with the null in `docs/ECON_RESULTS.md` section 4. A second, separate event is the move to online-only applications on 8 Mar 2019 (same day).
- Confidence: date high; mechanism high; 2019 euro amount low-medium.

### 3b. Other countries: ISBN fees and bibliography access

Status columns: Fee history (what I verified); Bulk open data (what I verified).

| Country | ISBN fee history | Fee change in 2005-2022? | National bibliography bulk data | Source(s) |
|---|---|---|---|---|
| Germany | MVB ISBN-Agentur charges. Prices as of 1 Aug 2022: single €70, 10 for €225, 100 for €300, 1000 for €400 excl. VAT (P). A 2011 price sheet hosted on a forum showed a €129 base fee plus €19/€39/€69 for 10/100/1000 (S, unclear provenance; I could not read the PDF text). | Probably price/structure changes, not a free-to-paid event; dates and amounts unverified | **Yes.** DNB title data, CC0 1.0, full dumps at https://data.dnb.de/opendata/ : `dnb-all_lds.{ttl,rdf,nt,jsonld,hdt}.gz` (6-9.5 GB, RDF). Weekly/ongoing MARC21 and MARC21-XML at https://data.dnb.de/DNBlfdMarc21 and https://data.dnb.de/DNBlfdMarc21xml (retained 100 days only; SFTP also). Licence stated at https://data.dnb.de/opendata/ . | https://german-isbn.de/isbn/preise-und-pakete ; https://www.dnb.de/EN/Professionell/Metadatendienste/Datenbezug/Laufend/_content/zugangMetadatenNationalbibliografieND_akk.html ; https://openglam.org/?p=2558 (S: CC0 since 2014-15) |
| Netherlands | CB (Centraal Boekhuis) runs the ISBN agency for NL and Flanders; paid, amount not read ("Wat kost een ISBN?" article exists at service.isbn.nl but body not fetched) | Unverified | Not verified (KB Dutch bibliography bulk status unknown) | https://service.isbn.nl/hc/nl ; S: EUR library FAQ |
| Belgium | Agencies per language region; fee status not established | Unverified | KBR Belgian Bibliography: bulk status not verified | https://www.isbn-international.org/node/87 ; https://www.kbr.be/collections/belgian-bibliography |
| Switzerland | Not established (agency believed to be run by the publishers' association; unverified) | Unverified | Not verified | none |
| Sweden | **Free** for publishers with a Swedish address (KB brochure 2023, P). No fee history found. | No change found | Libris / Swedish National Bibliography released CC0 in 2011 (S: https://lists.w3.org/Archives/Public/public-xg-lld/2011Sep/0440.html , https://infodocket.com/2014/02/14/library-data-national-library-of-sweden-signs-agreement-with-oclc-re-cc0-license ). Current dump location not verified; Libris XL has an OAI-PMH service (https://github.com/libris/librisxl) | https://www.kb.se/download/18.280a529018702e6727e363d/1681904094677/ISBN-2023.pdf |
| Finland | Fee status not verified (kansalliskirjasto.fi blocked). Believed free; unverified. | Unknown | **Yes (S, unconfirmed on the primary page).** Fennica national bibliography, CC0, full data as RDF and MARC; https://www.kansalliskirjasto.fi/en/news/finnish-national-bibliography-released-open-data ; https://www.avoindata.fi/data/en/dataset/fennica ; https://data.nationallibrary.fi | search summary only |
| Norway | **Free** to assign (P: "It is free to be assigned an ISBN"); any individual with a Norwegian address can apply | No change found | Norwegian national bibliography bulk status not verified (IFLA page 403) | https://www.nb.no/en/service/isbn-norway/ |
| Denmark | Dansk ISBN-Kontor at DBC Digital; price not shown on the pages I could read | Unverified | Not verified | https://www.isbn.dk/ |
| Poland | Biblioteka Narodowa e-ISBN service; a news item says use is free (S, undated); history not established | Unverified | `data.bn.org.pl` API (not verified) | https://dzieje.pl/node/26005 |
| Czechia | National Library ISBN agency; fee unknown | Unverified | NKP open data page exists (https://www.nkp.cz/en/about-us/professional-activities/open-data); not opened | |
| Brazil | Fees charged by Biblioteca Nacional via Fundação Miguel de Cervantes: R$22 per ISBN, R$36 with barcode, R$290 system registration (Dec 2019, S: https://www.diariodepernambuco.com.br/noticia/brasil/2019/12/biblioteca-nacional-deixa-de-fazer-o-isbn-de-livros-e-perde-r-4-milho.html). Agency changed to Câmara Brasileira do Livro from **1 March 2020** (P: https://www.isbn-international.org/node/333). CBL said it would maintain the price. | Agency change only; no free-to-paid event | Not verified | |
| Chile | Cámara Chilena del Libro is the ISBN agency (since 1987); fee payable (S) | Unverified | Only annual statistical reports (https://camaradellibro.cl/wp-content/uploads/2026/03/Informe_ISBN_2025.pdf), no verified catalogue dump | |
| Spain | Fee introduced with FGEE agreement (BOE 28 Dec 2011); €45 single (see `RESULTS_ES.md`) | **Yes, 2012** (already in project) | in project | |
| Portugal | Fees from 1 Jan 2015 (already in project) | **Yes, 2015** (already in project) | in project | |
| Luxembourg | Free (P: https://guichet.public.lu/de/entreprises/sectoriel/medias/edition/numero-identification-isbn-issn-ismn.html) | None found | Not verified; tiny market | |
| Austria | Hauptverband runs the agency; fee not found | Unverified | ONB open data not verified | |

Countries named in the request that I could not resolve: Switzerland, Belgium, Denmark, Netherlands (fee history), Finland (fee status), Norway/Sweden/Finland/Denmark/Belgium/Netherlands (current dump URLs).

## 4. Québec (BAnQ)

- **Free since 1979 (P, local `data/raw/evidence/qc_isbn_guide.pdf`, BAnQ "Guide ISBN"):** "En 1979, la Bibliothèque nationale du Québec (BAnQ) ... attribue gratuitement aux éditeurs francophones canadiens du secteur privé" ISBN blocks (prefix 2). No fee at any point was found.
- **Self-publishers:** the guide states that in self-publishing, the author becomes the publisher by default and can request ISBNs (P, same PDF; `qc_selfpublishing_guide.pdf`, "Petit guide de l'autoédition au Québec", 2019). Library and Archives Canada (P) states free ISBNs for Canadian self-publishing authors "physically located in Canada" and directs French-only publishers to BAnQ: https://www.canada.ca/en/library-archives/services/publishers/isbn/about.html (dated 2026-10-09). Self-published books are excluded from the CIP programme (P, BAnQ self-publishing guide). Legal deposit is mandatory (free; usually two copies).
- BAnQ ISBN eligibility conditions in full were not read. The BAnQ-hosted PDF at https://www.banq.qc.ca/sites/default/files/2022-08/Guide_autoedition_Qc.pdf is in the evidence folder under a different name.
- Confidence: high that Québec has had no fee in the study period.

## 5. British National Bibliography selection policy (self-published and POD)

**Not established; no published policy found.**
- BNB scope (S, search summaries of IFLA and BL pages): books and serials published or distributed in the UK and Ireland that the BL receives under legal deposit, with metadata coming from CIP, in-house cataloguing and derived records. Self-published and POD books are not named as excluded. IFLA page (403 to me): https://www.ifla.org/g/bibliography/british-national-bibliography/ ; summary at https://www.ifla.org/?p=105725.
- Legal deposit applies regardless of print run or POD (BL-linked article, S: https://www.pressreader.com/uk/writing-magazine/20210201/282613150504841 ; local `data/raw/evidence/uk_legal_deposit.html`, `uk_print_deposit.html`). A 2024 BL research report reportedly found the cost of print deposit is a barrier for POD self-publishers (S; report not located).
- Practical implication: the BNB reflects deposit receipt plus catalogue-prioritisation, and any change in how the BL claims or catalogues self-published POD titles after the Legal Non-Print Deposit and print deposit practice changes (Legal Deposit Libraries Act 2003; non-print regulations 2013) would produce a level shift in the UK series that is not driven by fees. I found no document dating such a change. This remains the main open threat to the UK result and needs a direct question to BL Metadata Services (not something I can answer from the web).

## 6. Official population series

- **File:** `config/population_official.csv` (columns `iso3,year,population`), 570 rows.
- **World Bank SP.POP.TOTL** (P), fetched via curl 2026-11-09 from `https://api.worldbank.org/v2/country/GBR;NZL;FRA;CAN;USA;ESP;PRT;IRL;DEU;NLD;BEL;CHE;SWE;FIN;NOR;DNK;BRA;CHL/indicator/SP.POP.TOTL?format=json&per_page=2000&date=1995:2024`. Source last updated 2026-10-08 per the API response. 18 countries x 30 years (1995-2024) = 540 rows, no missing values. Values are mid-year population. Note: these are World Bank estimates (UN WPP/national statistics offices); GBR 2024 = 69,281,000.
- **Québec:** appended as `CAN_QC` (subnational code, not an ISO3). Source: Statistics Canada table 17-10-0009-01 (quarterly population estimates), full-table CSV `https://www150.statcan.gc.ca/n1/tbl/csv/17100009-eng.zip`; I used the 1 July (Q3) value for each year, 1995-2024 (30 rows). Values: 1995 7,219,219; 2010 7,929,479; 2019 8,483,186; 2024 8,982,312. Also available from ISQ (https://statistique.quebec.ca) as a repackaging of the same StatCan estimates (S, not used). Caveat: StatCan revises these estimates after each census, so a later download can differ slightly; 2024 values are preliminary updated postcensal.
- The existing `config/population_millions.csv` is flagged "approximate" in the README; this file supersedes it for per-capita work but I did not compare the two or modify the old file.

## 7. Ranked candidate additional countries (feasibility for a fee event study)

Criteria: (a) an ISBN fee level or change I can document, (b) open bulk bibliography I have verified, (c) a self-publishing service sector large enough to classify.

| Rank | Country | Role in design | Fee status | Bulk data | Main obstacles |
|---|---|---|---|---|---|
| 1 | **Germany** | Paid country with very large self-publishing ecosystem (BoD, tredition, epubli, etc.); extra "paid" unit and possible price/structure change | Paid, €70 single (Aug 2022); 2011 sheet suggests a different structure; change dates unknown | CC0 DNB full dump (RDF, 6-9.5 GB) at https://data.dnb.de/opendata/ , verified | No free-to-paid event; needs a price history (Wayback) to exploit price variation; Germany's legal deposit and ISBN-less titles behave differently; RDF parsing heavy |
| 2 | **Sweden** | Free-ISBN control with CC0 national bibliography | Free (2023 KB brochure); no history found | CC0 declared (2011, 2014; S); current bulk file location unverified | Control only; no event; dump URL must be located via KB technical pages |
| 3 | **Finland** | Free(?)-ISBN control, CC0 bulk Fennica (RDF and MARC) | Fee status unverified | Fennica CC0 (S, not opened on primary page) | Fee status must be confirmed; small market |
| 4 | Norway | Free-ISBN control (P verified free) | Free | Bulk status unverified | Need to confirm open data |
| 5 | Netherlands | Paid, large POD sector; shared with Flanders | Paid; history unknown | Not verified | Both obstacles open |
| 6 | Brazil | 2020 agency change (BN to CBL); fees existed before | Charged R$22-36 per ISBN pre-2020; price said to be maintained | Not verified | No fee event; data unknown |
| 7 | Chile, Denmark, Belgium, Switzerland, Poland, Czechia, Austria | Possible controls | Mostly unknown | Mostly unknown | Insufficient evidence |

**Best three: Germany, Sweden, Finland.** Together they would add one paid and two (probable) free comparison units with open bulk data, supporting a level comparison of self-published share against ISBN cost across UK, DE vs NZ, SE, FI, NO. They do not provide the clean multi-country fee event study the plan hoped for, because the only free-to-paid events I can document (France 2019, Spain 2012, Portugal 2015) are the three the project already has. Recommend treating a "multi-country event study" as the existing FR/ES/PT events plus a cross-section of paid versus free levels.

## 8. What would most improve this file

1. Wayback CDX access for `isbn.nielsenbook.co.uk`, `nielsenisbnstore.com`, `afnil.org/tarification` and `german-isbn.de` pricing pages (would give UK price series, the exact 2019 AFNIL amount, German price changes).
2. A direct question to BL Metadata Services about BNB handling of POD/self-published titles.
3. Open `kansalliskirjasto.fi`, `kb.se`, `nb.no` data pages from a normal browser to confirm dump URLs and Finnish ISBN fee status.


## Portugal correction and new primary sources (2026-11-09, later revision)
- APEL service rules page (https://apel.pt/isbn/normas-de-servico/; saved data/raw/apel/normas.html, normas.txt): author-edition ISBN €15; 10-ISBN prefix €100 (professional)/€150 (non-professional); 100: €500/€750; 1,000: €3,000/€4,500; non-member initial registration €25; urgent €50; barcode €10; all excl. VAT; online-only form; author-edition prefixes 989-20 and 989-33, max 3 ISBNs per entity. Page shows a 2026 footer, so it is current terms, not a dated 2015 snapshot.
- APEL report, Sept 2014 (data/raw/apel/a-COMERCIO_LIVREIRO_APEL__SET2014_SEC.pdf; text apel_report_sep2014.txt): official counts of ISBNs allocated per year 2002–2013 (e.g. 14,913 in 2007; 17,131 in 2012; 19,060 in 2013), ISBNs to author-editors 855 until 2007 and 3,692 until Jan 2014, and the definition of the 989-20 category (individuals or organisations publishing one title).
- The user-supplied 11 Dec 2014 notice (e-geo.fcsh.unl.pt) could not be retrieved (DNS failure); a `curl -k` attempt was blocked and not repeated. Earlier statement 'no per-ISBN price for a self-publishing author was found' is superseded. See deliverables/PAPER_EVIDENCE_AUDIT.md.
