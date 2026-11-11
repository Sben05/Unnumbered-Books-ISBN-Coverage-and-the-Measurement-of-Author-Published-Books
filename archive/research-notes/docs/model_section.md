## A simple model of the author's identification choice

**Set-up.** An author has a finished book with reach value θ (what full visibility to retailers, libraries and catalogues would be worth to them). θ varies across authors. Printing costs k regardless of route. The author chooses one identification route r:

| Route | Visibility a_r | Cost c_r |
|---|---|---|
| N: national ISBN | a_N = 1 (retail ordering, library cataloguing, national statistics) | F + h (fee plus application hassle) |
| P: platform ISBN (e.g., Amazon KDP) | a_P < 1 (visible inside the platform only) | 0 plus lock-in λ (identifier not portable) |
| S: author-service publisher supplying the ISBN | a_S ≤ 1 | F_S, typically far above F (packages, rights terms) |
| O: no identifier | a_O small (local, direct sales) | 0 |

Payoff U_r = a_r·θ − c_r. The author publishes if max_r U_r ≥ k, and takes the route with the highest U_r.

**Thresholds.** Without a platform, authors with θ ≥ θ*_N = (F + h)/(1 − a_O) take a national ISBN and the rest publish without one. With a platform available, the N-versus-P margin is θ(1 − a_P) ≥ F + h + (λ-adjusted terms). A fee raises θ*: marginal authors move to P (where platforms are strong) or O (where they are not). They stop publishing only if their best remaining option no longer covers k.

**Measurement identity.** Let M be self-published books with a national ISBN (what ISBN statistics count) and Q all self-published books (what legal deposit records). Then M = s_N·Q, so Δln M = Δln Q + Δln s_N. ISBN statistics misread output by exactly the change in the share using national ISBNs.

**Predictions and where the paper tests them**

| Prediction | Test in the paper | Result so far |
|---|---|---|
| P1 Raising F lowers s_N much more than it lowers Q | Portugal four-source comparison; decomposition below | Supported |
| P2 Only producers who must make a new request respond (existing prefixes grandfathered) | Self-published vs small publishers (DiD); stock-exposure design | Supported for authors vs publishers; stock design null |
| P3 Low-θ books (short, poetry, local) switch first | Heterogeneity by length and genre | Not supported (technical titles responded most) |
| P4 Where a_P is high, the fee raises platform use rather than O | Platform ISBNs across national bibliographies; France 2019 | Mixed: platform use follows Amazon print markets more than national prices |
| P5 Across countries, the share of national ISBNs going to individuals falls with price | X–Y chart, CERLALC panel and national bibliographies | See section 2 |
| P6 Books without identifiers are less visible (a_O < a_N) | Google Books regression | Supported (association) |

**Decomposition for Portugal (illustrative).** Agency ISBNs to author-publishers (CERLALC) fall from 988 (2014) to 617 (2015): Δln M = −0.47. Self-published books in the national bibliography fall from 392 to 343: Δln Q = −0.13. The difference, −0.34 log points, is the implied fall in the share using national ISBNs. Against 2013 (718 and 313): Δln M = −0.15, Δln Q = +0.09, implied Δln s_N = −0.24. The two series measure different populations (agency category vs name-matched catalogue records), so this is an order of magnitude, not an estimate.

**Calibration (illustrative, attributing the whole change to the reform).** The share of self-published books carrying an ISBN falls from 58.5% (2010–14) to 51.3% (2015–19), a logit change of −0.29. With a fee of €15 + 23% VAT = €18.45, that is about −0.016 logit per euro: a €10 fee would cut the odds of using a national ISBN by roughly 15%. Because the fee came with the online form and the pre-trend was falling, this is an upper-bound-style illustration, not an elasticity estimate.
