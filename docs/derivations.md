# Derivations and source notes

Every expected value in the fixtures is either **published** (taken from the
cited source and cross-checked by recomputation), **derived** (computed by a
stated method from the fixture's own inputs), or **computed-by-hand** (shown
explicitly). No value is invented. The derived values can be reproduced by
anyone with:

```bash
pip install jsonschema numpy
python3 tools/compute_expected.py
```

which recomputes every derived value from the matrices alone and compares it
with what the fixture files state.

## Methods

**principal-eigenvector** (the normative method in these fixtures): the
priority vector is the principal right eigenvector of the judgment matrix,
normalized to sum to 1; lambda_max is the Perron root. CI = (lambda_max − n) /
(n − 1); CR = CI / RI(n) under the RI table the fixture declares.

**column-normalization-mean** (Saaty's approximate method, used by some
implementations, including the npm `ahp` package): normalize each column of
the matrix to sum to 1 and average across columns; lambda_max is estimated as
the mean of (A·w)ᵢ / wᵢ. On perfectly consistent matrices this coincides
exactly with the eigenvector; on inconsistent matrices it differs — by up to
about 0.02 on these fixtures. Where a matrix is inconsistent, fixtures carry
an `alternates` block with the expected values under this method, so a tool
is checked against its own documented method rather than loosely against
another's.

## RI tables

CR depends on the random-index table, so each fixture names its table and
inlines the values. Two tables appear:

| n | saaty (1980) | alonso-lamata (2006) |
|---|---|---|
| 3 | 0.58 | 0.5245 |
| 4 | 0.90 | 0.8815 |
| 5 | 1.12 | 1.1086 |
| 6 | 1.24 | 1.2479 |
| 7 | 1.32 | 1.3417 |
| 8 | 1.41 | 1.4056 |
| 9 | 1.45 | 1.4499 |
| 10 | 1.49 | 1.4854 |

Sources: Saaty (1980), *The Analytic Hierarchy Process*, McGraw-Hill; the
values are also tabulated (Wharton column) in Alonso & Lamata (2006),
"Consistency in the analytic hierarchy process: a new approach", *IJUFKS*
14(4), Table 1, which is the source of the second column. Other published
tables exist (Donegan & Dodd 1991; the estimates in Saaty's 2005 ANP book:
0.52, 0.89, 1.11, 1.25, 1.35, ...); the runner READMEs document which table
each verified implementation uses. **Two tools reporting different CRs for
the same matrix may simply be using different RI tables** — the
`ri-table-saaty` / `ri-table-alonso-lamata` fixture pair exists to make that
concrete, and comparing CI (which is RI-independent) removes the table from
the comparison.

## Per-fixture notes

### drinks-saaty-2008

Matrix, priorities (0.177, 0.019, 0.042, 0.116, 0.190, 0.129, 0.327) and
CR = 0.022 are published in Saaty (2008), Table 2, p. 86. The table as
printed shows (Wine, Tea) = 1/3 in the Wine row but (Tea, Wine) = 2 in the
Tea row, which is not reciprocal. The paper's text states that the reciprocal
entry is automatic ("It is automatic that 1/9 is what one needs to use in the
(wine, coffee) position"), and recomputation distinguishes the readings
cleanly:

* with (Tea, Wine) = 3 (reciprocal of the Wine row): eigenvector
  (0.177457, 0.019149, 0.041831, 0.116417, 0.189572, 0.128781, 0.326793),
  lambda_max 7.176629, CR 0.022302 — the published priorities and CR exactly,
  at the published precision;
* with (Tea, Wine) = 2 (the Tea row as printed): tea's priority becomes
  0.0393 (prints as 0.039, not the published 0.042) and CR 0.0142 (not the
  published 0.022).

The fixture therefore uses (Tea, Wine) = 3. The paper also publishes the
actual relative US consumption for comparison (0.180, 0.010, 0.040, 0.120,
0.180, 0.140, 0.330); that is context about the validation study, not a tool
output, and is recorded in the fixture's notes.

### car-hierarchy-wikipedia

The complete three-level hierarchy: 11 judgment matrices, 133 pairwise
comparisons. The criteria and subcriteria judgments are stated in the
article's prose; the alternative-level judgments are published in the
article's judgment-table images (AHPJonesPurchasePrice04REV01.png,
AHPJonesSafety02.png, AHPJonesPassengerCapacity02.png,
AHPJonesFuelCost02.png, AHPJonesResaleValue03.png,
AHPJonesMaintenanceCosts02.png, AHPJonesStyle01.png,
AHPJonesCargoCapacity02.png). The transcription in this fixture was verified
three independent ways:

1. **entry-by-entry against the images** — all 120 alternative-level
   judgments, including the decimal Fuel Costs intensities (the article's
   MPG ratios to two decimals, e.g. 1.13 = 35/31) and the non-integer
   Maintenance intensities 1.5 and 1.2;
2. **against the article's own displayed results** — under the
   column-normalization approximation, the transcribed matrices reproduce
   the article's per-criterion local priority tables at their printed three
   decimals (Fuel Costs within 0.003), its global priorities within 0.002,
   and the final priorities in its AHPJonesFinalPriorities.png synthesis
   table (0.213, 0.150, 0.109, 0.165, 0.143, 0.220) within 0.002;
3. **against the interactive decision linked from the article's External
   links section** (app.decisionpoint.io/ahp/processes/1u7fb2loziitknizzy7baon5t),
   which contains identical judgments.

Every numeric result the article displays — criteria priorities 0.504 /
0.237 / 0.042 / 0.217, the factor table, the local tables, and the final
synthesis — is consistent with the column-normalization approximation. The
exact principal-eigenvector results differ by up to about 0.003 without
changing the ranking (Odyssey 0.2191, Accord Sedan 0.2147, CR-V 0.1665,
Accord Hybrid 0.1497, Element 0.1438, Pilot 0.1061). The article does not
state which prioritization method its software used. The fixture's normative
expected values are the eigenvector derivation, with column-normalization
alternates per matrix; all displayed article values are preserved in
`source_reported`. Neither set is wrong; they are outputs of different
documented prioritization methods applied to the same judgments.

One caution for anyone cross-checking against summarized or scraped copies
of the article: the final priorities appear only in the synthesis-table
image, not in the article text (which names just the 0.220 / 0.213 top two
and the ranking order). The values above were read from the image itself and
confirmed by recomputation from the article's own local and global priority
tables.

### school-selection-saaty-1977

Matrices from Saaty (1977) as reproduced in arXiv:1802.01989, Section 5.2.
The original's priority values are behind a paywall, so all expected values
here are derived; the derived criteria weights (0.3208, 0.1395, 0.0348,
0.1285, 0.2374, 0.1391) and final priorities (A 0.3673, B 0.3785, C 0.2542)
agree, at their rounding, with the values widely reproduced in the secondary
literature. Two properties make this fixture useful:

* the criteria matrix is a famously inconsistent published example
  (lambda_max ≈ 7.42 at n = 6; CR ≈ 0.229 under the Saaty RI table), so it
  exercises tools' behaviour beyond the CR ≤ 0.1 convention;
* the A/B margin is about 0.01, and the eigenvector and
  column-normalization syntheses rank them differently (B first vs A first).
  Implementations using different documented prioritization methods can
  legitimately report different top choices here, which makes this fixture a
  sharp method-sensitivity probe.

### job-selection-saaty-2008

Tables 3–5 of Saaty (2008) publish three matrices with their priority
vectors (criteria: 0.036, 0.122, 0.262, 0.075, 0.506; flexibility
subcriteria: 0.091, 0.218, 0.691; salary alternatives: 0.555, 0.258, 0.124,
0.064). Recomputation reproduces all of them exactly at the published
precision. The source does not publish consistency figures for these
matrices, so lambda_max, CI and CR are derived. The example's remaining
matrices are not published in the paper and are not included.

### consistent-n3 / n4 / n5

Constructed as a_ij = wᵢ/wⱼ from exact weight vectors (6/10, 3/10, 1/10),
(8, 4, 2, 1)/15 and (16, 8, 4, 2, 1)/31. Perfect consistency is exact, not
approximate: lambda_max = n, CI = CR = 0, and the construction weights are
recovered exactly by any correct method (eigenvector and approximate methods
coincide on consistent matrices). Tolerances on CR are 1e-9 — a correct
implementation differs from zero only by floating-point residue.

### fractional-entries

Constructed 3×3 matrix mixing fraction strings (1/3, 1/7) and decimals (2.5,
0.4) to exercise entry parsing and reciprocal handling across notations;
0.4 = 1/2.5 so the matrix is reciprocal. Mildly inconsistent by construction
(a13 = 2.5 vs a12·a23 = 7/3), all expected values derived.

### ri-table-saaty / ri-table-alonso-lamata

The same constructed 4×4 matrix under two declared RI tables. Priorities,
lambda_max and CI are identical; CR is 0.034555 under Saaty's table and
0.035281 under Alonso–Lamata's. See the RI section above.

### ts1997-example1-criterion-weights and ts1997-example3-performance-measures

Published values transcribed from the authors' archived full version of
Triantaphyllou & Sánchez (1997) at csc.lsu.edu/trianta (Tables 2–5 and 9–12
respectively). Before inclusion, every value was recomputed from the printed
decision matrices:

* **Example 1** — the preferences and every feasible threshold in Table 5
  reproduce within 1.0 percentage point (the paper computed them from
  intermediate values rounded to four decimals), with one exception: the
  (A2, A3) entry under C3 prints as 0.0262 absolute / 9.1099 percent, while
  recomputation from the printed matrix gives about 0.262 / 91.1 —
  consistent with a decimal-place slip in typesetting. The quantities the
  paper derives from that entry (the Percent-Any critical value, criticality
  degree D′₃, sens(C3), and the sensitivity ordering) inherit it, so they are
  preserved in `source_reported` with an explanation rather than stated as
  expected values. The Percent-Top conclusion (C3 at 64.8818%) is unaffected
  and recomputes to 64.876.
* **Example 3 (the paper's WSM/AHP performance-measure example)** — the
  preferences recompute exactly, and all Table 11 criticality degrees for
  rows A1–A4 recompute within 0.3 under the model the paper describes
  (percent change in a_ij with column j renormalized, solved for the ranking
  reversal). The printed A5-row thresholds against target A4 (10.0, 14.9,
  3.5) did not reproduce under that same model — decreasing an A5
  performance value cannot make the already-preferred A4 overtake A5, and
  the reversal recomputes as an increase (about −8.9% under C1) — so the A5
  criticality degrees are preserved in `source_reported` with an
  explanation rather than stated as expected values.

No open implementation in `runners/` currently computes these sensitivity
measures, so the stability fixtures are verified via captures; they are
schema-validated and their preferences are recomputed in CI.
