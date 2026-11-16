# How to produce a capture

A **capture** records the outputs a tool produced for one fixture, for tools
that cannot run in CI — closed-source, GUI-only, or hosted. Captures are
manually curated snapshots: dated, versioned, operator-attributed, and
re-verifiable. Every tool is captured the same way, with the same schema and
the same fields; no tool gets special status.

A capture never asserts that a tool is right or wrong. It records what the
tool produced, whether that is within the fixture's stated tolerance of the
expected values, and — whenever it is not — the cause, stated factually.

## Step by step

1. **Pick a fixture** from `fixtures/` and read its `description`, `scale`
   and `ri_table` blocks before starting. Note the matrix labels and entry
   values (fraction strings such as `"1/3"` mean exactly one third).

2. **Record the tool's identity before entering anything**: exact name,
   version as the tool reports it (`undetermined` if it doesn't), and
   platform. For hosted tools also note the date, since hosted versions
   change silently.

3. **Enter the fixture's judgments into the tool**, following the tool's own
   conventions. If the tool only accepts whole numbers plus reciprocals,
   or only a slider, say so in `captured.notes`. Enter exactly the fixture's
   values; do not adjust judgments to make the tool's consistency check pass.

4. **Export what the tool allows** — a model file, a report, a CSV, or at
   minimum screenshots of the matrices and results. Place exported files
   under `captures/<tool-slug>/artifacts/` and list them in
   `reverify.artifacts`.

5. **Transcribe the outputs exactly as displayed**, at the precision the tool
   displays, into the `outputs` block — priorities, and whichever of
   lambda_max / CI / CR the tool shows (use `null` for values the tool does
   not display, and say so in `notes`). Do not round, renormalize, or
   back-derive values the tool did not show.

6. **Determine the tool's RI table and prioritization method if you can** —
   from its documentation, published source, or vendor support — and record
   them in `ri_table` and `prioritization_method` with how you determined
   them. If you cannot, record `undetermined`. Many CR differences between
   tools are RI-table differences (see the `ri-table-*` fixture pair), so
   this field does a lot of work.

7. **Compare each output with the fixture's expected values** within the
   fixture's stated tolerance, and record the result per output in
   `matches_expected`. If the tool's documented method matches one of the
   fixture's alternate expected blocks, compare against that block and name
   it in `compared_to`.

8. **Explain any divergence.** If any output is outside tolerance,
   `explanation` is required (CI enforces this). State the cause, not a
   verdict: "uses the Alonso–Lamata RI estimates; CI and priorities match"
   is a complete explanation. If you cannot determine the cause, say what
   you ruled out and record the cause as undetermined.

9. **State the re-verification path** in `reverify`: free-text instructions
   that let anyone repeat the session, and/or the exported artifacts, and/or
   a URL anyone can open without an account that reproduces the fixture in
   the tool. At least one is required.

10. **Validate before opening a PR**:

    ```bash
    pip install jsonschema numpy
    python3 tools/validate.py
    ```

## File layout

```
captures/<tool-slug>/<fixture-id>.json
captures/<tool-slug>/artifacts/<fixture-id>.<ext>   (exported files, optional)
```

One capture file per (tool, fixture) pair. A new session with a newer tool
version is a new capture; do not overwrite an old capture that correctly
records what an older version produced — move superseded captures to a dated
file name (e.g. `drinks-saaty-2008.v1.2.json`) if the tool slug stays.
