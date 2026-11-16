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
