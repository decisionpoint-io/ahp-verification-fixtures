# Captures: decisionpoint.io

Captures for the hosted [decisionpoint.io](https://decisionpoint.io)
application, recorded per [docs/capture-guide.md](../../docs/capture-guide.md)
— the same schema, fields and rules as every other tool captured here.

Re-verification paths use public decisions, openable without an account.

| Fixture | Date | Result |
| --- | --- | --- |
| [car-hierarchy-wikipedia](car-hierarchy-wikipedia.json) | 2026-11-16 | all 11 local priority vectors, all 11 per-matrix consistency ratios, the global priorities and the final synthesis match the fixture's expected values at display precision; re-verification via a [public decision](https://app.decisionpoint.io/ahp/processes/1u7fb2loziitknizzy7baon5t) that is also linked from the Wikipedia article's External links |
| [drinks-saaty-2008](drinks-saaty-2008.json) | 2026-11-17 | the displayed priorities equal the published values digit for digit and the consistency figure matches; re-verification via a [public decision](https://app.decisionpoint.io/ahp/processes/1ubjp6e9uoydkbwhaiczruo4l) |
| [college-selection-rwsaaty-1987](college-selection-rwsaaty-1987.json) | 2026-11-17 | both matrices' priorities and consistency ratios match at display precision; re-verification via two public decisions ([criteria](https://app.decisionpoint.io/ahp/processes/1ubjp6fae5e05ccm25zdfb1i8), [location](https://app.decisionpoint.io/ahp/processes/1ubjp6fou3r2laem8obbtz30r)) |
| [school-selection-saaty-1977](school-selection-saaty-1977.json) | 2026-11-17 | all seven priority vectors, all seven per-matrix consistency ratios and the synthesis match at display precision (School B first); the sensitivity page's Stability Overview matches the fixture's Percent-Top `proportional-redistribution` block on every row, including the critical criterion (Learning) — the convention difference from Theorem 1 is explained in the capture; re-verification via a [public decision](https://app.decisionpoint.io/ahp/processes/1ubjp6g538axfzqc6uv7nwmxb) |

Single-matrix fixtures (drinks, the two college matrices) are represented as
decisions with one criterion and the compared items as alternatives, so the
published ranking equals the matrix's priority vector directly. In every
capture the decision was built through the application's public API from the
fixture's matrices, and the stored judgments were read back through the same
API and confirmed to reproduce the fixture entry for entry before the outputs
were transcribed.

## Why there is no capture of the ts1997 stability fixtures

The application enforces Saaty's fundamental scale on judgment entry (each
judgment between 1/9 and 9). The Triantaphyllou & Sánchez (1997) example
matrices were generated as normalized data directly, not from 1–9-scale
judgments: reconstructing Example 1's decision matrix as consistent judgment
ratios needs values up to ≈ 18.8, and every ratio involving alternative A4
under criterion C1 exceeds 9, so no judgment set the application accepts can
represent those fixtures. That is a property of the data, not a defect of the
tool. The application's Percent-Top stability implementation is instead
verified against the derived stability expectations of
`school-selection-saaty-1977` (see that capture and
[docs/derivations.md](../../docs/derivations.md)).
