# Runner: npm `ahp` package (JavaScript)

Runs the MIT-licensed [`ahp`](https://www.npmjs.com/package/ahp) npm package
(github.com/airicyu/ahp — the library used by the Comcast AHP Tool) against
every fixture and checks its outputs against the fixtures' expected values.

```bash
npm install
node runner.js               # all fixtures
node runner.js ../../fixtures/drinks-saaty-2008.json
```

## How the tool's outputs map onto the fixtures

| Output | package behaviour | How it is checked |
| --- | --- | --- |
| priorities | column-normalization mean (Saaty's approximate method; `AHP.calculateMatrixConsistency` in the package source) | against each fixture's `column-normalization-mean` alternate expected block; for perfectly consistent matrices the methods coincide and the normative values are used |
| lambda_max | estimated as the mean of `(A*w)_i / w_i` | against the same alternate block |
| CI, CR | classic Saaty (1980) RI table (`RI_MAP` in the package source), matching the fixtures' `saaty` table | directly; for the fixture declared under the Alonso–Lamata table, CR is derived from the package's CI using the RI values inlined in that fixture |
| synthesis / global priorities | `run()` composes a full goal→criteria→items model | composed from the package's per-matrix weight vectors via its public static API (see note) |

Two method notes, both documented per-fixture rather than treated as errors:

* The package derives priorities with the **column-normalization mean**, not
  the principal eigenvector. The two coincide exactly on consistent matrices
  and differ on inconsistent ones (by up to ~0.02 on these fixtures). The
  fixtures state expected values for both documented methods, so the package
  is verified strictly against an independent implementation of its own
  method — tolerance 1e-6 — rather than loosely against another method's
  values.

* The package's end-to-end `run()` declines to synthesize when any matrix's
  CR exceeds 0.1 (by design, with a dedicated error type). The school fixture's
  criteria matrix is a famously inconsistent published example (CR ≈ 0.23),
  so composition in this runner uses the package's public
  `calculateMatrixConsistency` API per matrix uniformly, with the weighted
  products computed in the runner.

Stability fixtures are skipped: the package does not implement sensitivity
analysis (a scope note, not a defect).
