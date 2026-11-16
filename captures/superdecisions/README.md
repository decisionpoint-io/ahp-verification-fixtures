# Captures: SuperDecisions (web)

Captures for the SuperDecisions web application (superdecisions.com, V4
Platform), recorded per [docs/capture-guide.md](../../docs/capture-guide.md).
Model building and judgment entry are automated in the operator's browser,
with the completed judgment matrix checked against the fixture before
transcription; outputs are transcribed verbatim and manually checked by the
operator before commit (the automation is noted in each capture's
`captured.notes`). Model files are saved in the operator's connected Google
Drive and can be exported on request.

| Fixture | Date | Result |
| --- | --- | --- |
| [drinks-saaty-2008](drinks-saaty-2008.json) | 2026-11-16 | priorities match the expected values at display precision; the displayed inconsistency (0.0218) uses a different random-index table than the fixture declares (RI(7) = 1.35, consistent with the estimates in Saaty's 2005 ANP book) and is within the published CR's tolerance here — see the capture's `ri_table` |
| [college-selection-rwsaaty-1987](college-selection-rwsaaty-1987.json) | 2026-11-16 | priorities match at display precision; the criteria matrix's inconsistency (0.0206 vs published CR 0.02) is the first capture divergence on record, explained as a random-index difference (effective RI(4) = 0.89 vs the fixture's 0.90, same CI) |
| [car-hierarchy-wikipedia](car-hierarchy-wikipedia.json) | 2026-11-16 | all 11 local priority vectors and the final synthesis (via the tool's supermatrix) match at display precision, decimal judgments accepted; four inconsistency figures diverge within 0.001 and are explained as random-index differences (effective RI 0.89/1.25 at n=4/6 vs the fixture's 0.90/1.24, same CI) |
