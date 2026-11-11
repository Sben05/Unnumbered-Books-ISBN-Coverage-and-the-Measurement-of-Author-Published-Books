# Overnight log (started 2026-11-09 ~05:10)
Assumption: Prof Hanlon's go-ahead = push the study toward the "skeptic-proof" fee case (open items in memory/ECON_RESULTS §6/RESULTS_PT "Not done").
Plan
1. [agent A,B] Hand-label validation samples (6 sources) -> precision/recall -> output/validation_labelled/
2. [agent C] Fee-history facts (UK Nielsen, Quebec, France 2019, BNB policy) + official population -> docs/FEE_HISTORY.md, config/population_official.csv
3. [me] Pooled stacked event study + synthetic control across fee introductions (ES 2012, PT 2015, FR 2019) with never-treated donors (NZ, QC, UK, US) -> src/night_*.py, output/night/
4. Fold into docs/NIGHT_REPORT.md (+ figures); update memory.
Status log below.
- 05:30 event study + placebo done (src/night_events.py, night_placebo.py, night_fig.py -> output/night/): PT 2015 -0.54..-0.80 logit, placebo p<0.03; ES 2012 -0.31 (p~.14-.29); FR 2019 null. Agents A,B,C running.
- 05:25 Agent A (UK/NZ/FR labels) done: precision 98-99%, FN 1-7%; see output/validation_labelled/SUMMARY_uk_nz_fr.md. Waiting on B (QC/ES/PT) and C (fees).
- 05:30 Agent B (QC/ES/PT labels) done: PT prec 99/99 (no pre/post diff), ES 93/97 (org-named-after-author FPs), QC 100/100. Waiting on C (fees).
- 05:40 All agents done. Wrote docs/NIGHT_REPORT.md, output/night/*. Remaining: memory update, stop cron.
## Round 2 (06:00) - user said previous result was disappointing; keep going non-stop, find new hypotheses + download new data (full authority)
Backlog / hypotheses:
 H1 multi-country cross-section: free vs paid ISBN regime -> AP per million (DE paid, SE/FI/NO free, + others)
 H2 extensive margin at fee dates: first-time self-publishers (entrants) vs repeat authors (ES/PT/FR)
 H3 ISBN-less substitution (ES noisbn, PT done) ; H4 rule fixes (org guard) rerun all series + event study
 H5 ISBN block/prefix evidence (self-pub pools) around fees; H6 genre/UDC composition shift at fee
 H7 Amazon 979-8 free-ISBN availability as substitute post-2018 in paid countries
 H8 Wayback fee pages (Nielsen/AFNIL/DE), BNP 2014 note
- 06:15 launched agents: DE (ad15312d), Nordics (a84b0c9d), extra countries (a31e6396), classifier-fix rerun (ae110dbb).
- H2 DONE (src/night_margin.py -> output/night/ap_margin_by_year.csv/png): PT 2014->2015 distinct AP authors 187->147 (-21%), new authors 131->100, books/author 1.29->1.14: fall is on extensive margin (fewer authors) and intensive. ES 2011->2012 authors 876->743 (-15%), recovers by 2014. FR authors keep rising 2019-21.
- H7/H9 DONE (src/night_fr_noamz.py): FRANCE 2020-21: 21-25% of AP books carry Amazon 979-8 ISBNs (appear 2020, 13 in 2019 -> 1229 in 2020), a catalogue/legal-deposit-or-substitution jump. Excluding Amazon ISBNs, FR AP share 4.86% (2019) -> 5.27% (2020) -> 4.95% (2021), vs +0.4pp/yr pre-trend; trend-adjusted gap vs NZ/QC: 2019 +.06, 2020 -.04, 2021 -.21 (pre residual sd ~.05). Suggestive of a lagged fee effect hidden by Amazon-ISBN inflow; one point, noisy donors.
- WARNING: UK catalogue n collapses 70.6k(2014) -> 42.7k(2015) -> 34k -> 10.8k -> 0.9k(2018): UK is unusable as donor after 2014. Event-study donor sets should drop UK post-2014 (PT 2015 LOO nz+fr -0.47/-0.68 stays).
- 06:30 Wayback fee-page agent launch was DENIED by auto-mode classifier (no reason given); not retried/worked around. Needs user decision. Other 4 agents running.
- 06:45 folded H2/H7/UK warning into NIGHT_REPORT sec 7-9
- 06:50 Agent fixes DONE: rule fixes don't change PT/ES/FR conclusions (PT -42%, p=0; ES -27% not robust; FR null). Precision UK .99 NZ 1.0 FR 1.0 ES .979 (in-sample). See output/night_fixed/RESULTS_FIXED.md
- 06:58 Agent H DONE (output/night_h/RESULTS_H.md): H-A composition: no fee-shaped shift (short/poetry/memoir not first to go). H-B PT: AP on small prefixes (<=10 numbers) 45%->32% (DiD -0.33, CI excl 0); first-use of prefix 25%->10%; multi-author prefix share 68%->80%. H-C PT: AP records w/o ISBN 47%->58% vs flat non-AP (DiD +0.53, CI .36-.70); ES weak; no FR/NZ/QC controls. H-D elasticity illustrative only (3 pts). Next: PT ISBN-visibility with placebos.
- 07:05 Agent vis DONE (output/night_vis/RESULTS_VIS.md): PT 2015 ISBN-visibility ITS significant (ISBN share -0.58 Holm p<.001; small prefixes -0.83; first-use -1.30; 2015 ranks 1st of 13 placebo breaks) BUT sup-F block-bootstrap p .07-.45 (none survives Holm); PT non-AP null; ES 2015 null; ES 2012 analogue does NOT replicate (opposite prefix signs). Total AP ITS -0.10 [-0.24,+0.04]; 20-50% of lost ISBN-visible books reappear w/o ISBN (CI -32..+97%).
- 07:20 Agent extra DONE (output/extra_countries/RESULTS_EXTRA.md): built PL (combined 0.6% 1995-2004 -> 3.1% 2015-19; AP 0.44%->1.8%), EE (flat 2.2-2.9%), LV (2014-23 only, 3.3->1.6%). No new fee events (PL/CZ/EE free, LV nominal fee since <=2010). Czechia download timed out (rerun curl from other network). KEY: free-ISBN PL/EE/LV ~3% ~ paid UK 3.15%; FR 12.6, NZ 15, PT 10.5 => fee level alone doesn't order country levels. Waiting: DE (ad15312d), Nordics (a84b0c9d).
- 07:25 FR 979-8 check: 2020 records are real French individual authors with French places (not misclassified); 0 in 2017, 13 in 2019, 1229 in 2020. KDP began 979-8 ISBNs ~2020 (unverified date); consistent with substitution to free Amazon ISBNs post-fee, or deposit change. Not separable here.
- 08:02 Added READ THIS FIRST summary atop NIGHT_REPORT.md
- 08:20 Agent DE DONE (output/germany/RESULTS_DE.md): 2.64M print ISBNs 1995-2023 (DNB CC0). AP share 1.0% (2000) -> 0.5% (2008) -> 2.5% (2018) -> 4.0% (2019); combined 4.7% (2008) -> 19% (2018) -> 32% (2023). Per million AP 9.9 (2012) -> 50 (2019). Big breaks: 2004 (BoD), 2013 (+56%, US-block ISBNs), service steps epubli 2016/BoD 2018 likely DNB artefacts. No dated fee change found (current €70/ISBN). Validation 30+30: precision ~83-97%. Germany = paid control, no event. Nordics agent still running.
