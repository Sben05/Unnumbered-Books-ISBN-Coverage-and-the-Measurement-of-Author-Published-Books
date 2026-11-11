# Independent validation of the author-publisher classification

Status: sample prepared, no human labels completed. Revision: 11 November 2026.

## What to code

Use the title, credited authors, statement of responsibility, and publisher fields. Mark:

- `Y`: the metadata indicates that a credited personal author is the publisher, including a clear author-edition statement or a matching personal name.
- `N`: the publisher is a distinct press, organization, government body, or service imprint, without evidence that the credited personal author is the publisher under this definition.
- `U`: evidence is incomplete, contradictory, or ambiguous.

This first pass validates a record-defined class. An author's use of a privately named imprint may not be inferable from these fields. Do not expand the definition to all independent publishing. Record any external investigation separately; it answers a stronger question about actual publishing arrangements.

Enter confidence, evidence or uncertainty, and your name in `reviewer`. Preserve original labels and explanations. Two people should independently code at least the entire 800-record pilot before discussing disagreements. A third person or documented evidence should resolve disagreements. Keep `U` where it cannot responsibly be resolved. Do not use AI-generated responses as independent human reference labels.

Predicted classes, explicit ISBN fields, publication years, and sampling weights are hidden. Incidental clues in titles or publisher strings may remain. Do not open the key or the manuscript's record-level examples during independent coding.

## Sample and precision

Strata: each publication year 2010–19 × predicted author-published yes/no × ISBN present/absent, yielding 40 cells.

| Cell type, within each year | Pilot | Full design |
|---|---:|---:|
| Predicted positive, ISBN | 20 | 20 |
| Predicted positive, no ISBN | 20 | 20 |
| Predicted negative, ISBN | 20 | 120 |
| Predicted negative, no ISBN | 20 | 40 |
| Total across ten years | 800 | 2,000 |

The pilot is contained in the full design. IDs agree between the two sheets. The extra 1,200 rows extend the first sample and are not a second independent sample.

Why expand beyond 400–800? A classification omission probability of roughly 0.515% in the large post-period ISBN-negative population can eliminate the main pooled coverage difference under an adverse one-cell scenario. With zero errors in 100 randomly reviewed records, a one-sided binomial 95% upper error limit is about 2.95%; with 600 it is about 0.50%. Thus an 800-row balanced pilot alone cannot tightly rule out relevant omissions. The larger design has 600 ISBN-negative observations per period, distributed across its five years. This is an approximate detection rationale, not a guarantee of sufficient precision for a corrected decomposition. Finite-population, stratum, and author-clustering effects should be considered after labels arrive.

Sampling seed: 20261110 plus the sorted stratum index; final shuffle seed: 20261111. Within each stratum, pilot observations are the first 20 rows of the full random draw. Population counts and record identifiers are in the separate key. These seeds describe this frozen sample, not a requirement to replace the supplied sample if someone has already started coding.

## Reporting and corrections

Report both unweighted coder disagreement and weighted classification metrics. Do not calculate population accuracy from the balanced sheet without weights. Each record's weight is the population size of its year × predicted label × ISBN cell divided by the number reviewed in that cell.

Estimate true class totals in each cell using adjudicated Y/N labels, then aggregate before computing precision, recall, and ISBN rates. Report pre/post and ISBN-specific accuracy, not just an overall agreement percentage. Compute corrected 2014/2015 counts and the log decomposition as well as the corrected pooled 2010–14/2015–19 coverage change. Preserve both pre-adjudication labels when estimating disagreement.

`score_validation.py` accepts the complete pilot or complete full design. It refuses duplicate IDs, unknown IDs, incomplete strata, missing reviewer names, and blank/U labels. It estimates weighted precision, recall, pre/post coverage, and the corrected headline decomposition. It provides a stratified bootstrap and zero-error stratum bounds. It does not compute coder agreement from one adjudicated column; maintain two original coding files and calculate that separately.

If ambiguity persists, do not force Y/N merely to satisfy the scorer. Report unresolved fractions and calculate adverse assignments of U, preserving population weights. A conservative sensitivity exercise should also allow unseen errors when a cell has zero observed mistakes. Bootstrap certainty at zero observed error is not evidence of perfect classification. No validation result applies to books missing from the national bibliography.
