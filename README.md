# ahp-verification-fixtures

A neutral, citable set of test fixtures for implementations of the Analytic
Hierarchy Process (AHP): judgment matrices with expected outputs, per-value
provenance, and stated numeric tolerances — plus runners that verify open
implementations in CI, and a capture format that records the outputs of tools
which cannot run in CI, with provenance and a re-verification path.

The aim is simple: when two AHP tools give different numbers for the same
judgments, it should be possible to say *why* — a different random-index
table, a different prioritization method, a different rounding — with a
shared, citable reference point. Divergences are documented with their cause.
No tool is called wrong here.

## What's in a fixture

Each file in [`fixtures/`](fixtures/) (validated against
[`schema/fixture.schema.json`](schema/fixture.schema.json)) contains:

* the judgment matrix or matrices (hierarchies carry parent links), with
  entries as numbers or exact fraction strings such as `"1/3"`;
* a **source citation** for the case itself;
* **expected outputs** — priorities, lambda_max, CI, CR, and synthesis where
  applicable — each with a stated absolute **tolerance** and a **provenance**
  field saying whether the value is *published* (with citation),
  *derived* (with the method stated), or *computed by hand*;
* the **RI table** used, named and with its values inlined, because CR
  depends on it;
* where documented prioritization methods disagree on the same matrix, an
  `alternates` block with the expected values under each method, so every
  tool can be verified against its own documented method.

No expected value is invented: every number is published in a cited source
(and cross-checked by recomputation), or derived by a stated method that
anyone can reproduce with [`tools/compute_expected.py`](tools/compute_expected.py).
[`docs/derivations.md`](docs/derivations.md) has the full notes, including
the places where a published source's own values required a documented
reading (a non-reciprocal printed entry, a probable typesetting slip).

## Seed fixtures

| Fixture | Category | Expected values from |
| --- | --- | --- |
| [`drinks-saaty-2008`](fixtures/drinks-saaty-2008.json) | matrix | published (Saaty 2008, Table 2: priorities and CR 0.022) — also the literature known-CR case |
| [`car-hierarchy-wikipedia`](fixtures/car-hierarchy-wikipedia.json) | hierarchy | derived — the complete three-level hierarchy (11 matrices, 133 comparisons, alternatives included), judgments verified against the article's published judgment-table images; Wikipedia's displayed values preserved and explained in `source_reported` |
| [`school-selection-saaty-1977`](fixtures/school-selection-saaty-1977.json) | hierarchy | derived from the published matrices, verified entry-by-entry against Saaty (1977) with the paper's published results cross-checked and preserved in `source_reported`; includes a famously inconsistent criteria matrix (CR ≈ 0.23), and derived Percent-Top criterion-weight stability thresholds under two documented conventions (Theorem 1 and proportional redistribution) |
| [`job-selection-saaty-2008`](fixtures/job-selection-saaty-2008.json) | matrix | published (Saaty 2008, Tables 3–5 priorities) |
| [`college-selection-rwsaaty-1987`](fixtures/college-selection-rwsaaty-1987.json) | matrix | published (R. W. Saaty 1987) — two matrices printed with priorities **and** CRs (0.02 and 0.092), the literature known-CR cases of record |
| [`consistent-n3/n4/n5`](fixtures/consistent-n3.json) | matrix | derived (constructed; CR exactly 0) |
| [`fractional-entries`](fixtures/fractional-entries.json) | matrix | derived (entries like 1/3 and 2.5; reciprocal handling) |
| [`ri-table-saaty`](fixtures/ri-table-saaty.json) / [`ri-table-alonso-lamata`](fixtures/ri-table-alonso-lamata.json) | matrix | derived — the SAME matrix under two RI tables, showing a CR difference that is purely an RI-table difference |
| [`ts1997-example1-criterion-weights`](fixtures/ts1997-example1-criterion-weights.json), [`ts1997-example3-performance-measures`](fixtures/ts1997-example3-performance-measures.json) | stability | published (Triantaphyllou & Sánchez 1997 criticality values) — verify sensitivity implementations, not just priorities |

## Runners vs captures

**Runners** ([`runners/`](runners/)) verify open implementations that anyone
can install and that run in CI on every push:

* [`runners/python-ahpy`](runners/python-ahpy/) — the AHPy library
  (principal eigenvector; its own RI tables, cross-derived transparently);
* [`runners/npm-ahp`](runners/npm-ahp/) — the MIT npm `ahp` package,
  the library used by the Comcast AHP Tool (column-normalization mean;
  classic Saaty RI table).

The two runners themselves differ in prioritization method and RI table —
which is the repository's point in miniature; each runner's README documents
exactly how its tool's outputs map onto the fixtures.

**Captures** ([`captures/`](captures/), validated against
[`schema/capture.schema.json`](schema/capture.schema.json)) record tools that
cannot run in CI — closed-source, GUI-only, or hosted. A capture is a
manually curated snapshot: tool name/version/platform, date, operator,
method of entry, outputs transcribed exactly, the tool's RI table if
determinable, a per-output comparison against the fixture's tolerances, an
**explanation required whenever any output diverges**, and a re-verification
path (instructions, exported artifacts, and/or a URL anyone can open).
[docs/capture-guide.md](docs/capture-guide.md) is the step-by-step guide.
CI validates every capture and fails if a divergence lacks an explanation.

All captures are curated snapshots, for every tool including the
maintainer's own — same schema, same fields, same rules.

## Running everything locally

```bash
pip install jsonschema numpy
python3 tools/validate.py            # schemas + capture tolerance checks
python3 tools/compute_expected.py    # recompute all derived values

pip install -r runners/python-ahpy/requirements.txt
python3 runners/python-ahpy/runner.py

cd runners/npm-ahp && npm install && node runner.js
```

## How to cite

> decisionpoint.io (maintainer), *AHP verification fixtures*,
> https://github.com/decisionpoint-io/ahp-verification-fixtures, version/commit as used.

Per-fixture, cite the fixture's own `source.citation` for the underlying
case alongside the repository reference.

## Contributing

PRs are welcome for:

* **runners** for other open implementations (R's `ahpsurvey`, `ahp` CRAN
  package, Python `pyDecision`, ...) — a runner must map the tool's
  documented method and RI table onto the fixtures explicitly, as the two
  existing runners do;
* **captures** of tools you have access to, following
  [docs/capture-guide.md](docs/capture-guide.md) and the schema's provenance
  requirements;
* **fixtures** with verifiable provenance for every expected value —
  published values must recompute from the published inputs (or the
  discrepancy must be documented in `source_reported`), and derived values
  must state their method.

Maintained by [decisionpoint.io](https://decisionpoint.io). MIT licence.
