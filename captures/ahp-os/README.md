# Captures: AHP-OS

Captures for AHP-OS (bpmsg.com), recorded per
[docs/capture-guide.md](../../docs/capture-guide.md). Model building and
judgment entry are automated in the operator's browser, with every entered
judgment read back and checked against the fixture before calculation;
outputs are transcribed verbatim and manually checked by the operator before
commit (the automation is noted in each capture's `captured.notes`).

| Fixture | Date | Result |
| --- | --- | --- |
| [drinks-saaty-2008](drinks-saaty-2008.json) | 2026-11-16 | priorities, lambda_max and CR all match the expected values at the tool's display precision |
| [college-selection-rwsaaty-1987](college-selection-rwsaaty-1987.json) | 2026-11-16 | all outputs match at display precision; the n=4 display pinned the tool's CR basis to the Alonso–Lamata linear fit, confirmed in the published source code (github.com/bpmsg/ahp-os) |
| [ri-table-saaty](ri-table-saaty.json) / [ri-table-alonso-lamata](ri-table-alonso-lamata.json) | 2026-11-16 | one session covering the pair: priorities and lambda_max match both fixtures; the displayed CR (3.4%) diverges from both expected CRs and is explained — the tool implements Alonso & Lamata's linear fit (effective RI(4) = 0.9094), which differs from the 1980 table and from A&L's own Table 1 values |
| [school-selection-saaty-1977](school-selection-saaty-1977.json) | 2026-11-16 | partial (criteria, Learning, Vocational Training): priorities and eigenvalues match at display precision; all three CRs diverge and are explained — at n=3 the tool's linear-fit RI (0.4793) sits ~17% below the fixture's table value (0.58), giving the repository's most visible RI-convention difference (5.6% vs 4.6%, 21.8% vs 18.0%) |
