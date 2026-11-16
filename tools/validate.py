#!/usr/bin/env python3
"""Validate all fixtures and captures against the schemas, and tolerance-check
captures against their fixtures' expected values.

Checks, in order:
 1. every fixtures/*.json validates against schema/fixture.schema.json,
    its id matches its file name, matrices are square and reciprocal,
    and matrix labels match row counts;
 2. every captures/**/*.json validates against schema/capture.schema.json
    and references an existing fixture;
 3. every capture's outputs are re-compared against the fixture's expected
    values (or the named alternate block) within the stated tolerances, the
    recomputed result must agree with the capture's own matches_expected,
    and any divergence (matches: false) REQUIRES a top-level explanation.

Exit code 0 only if everything passes.
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
failures = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg):
    print(f"  ok    {msg}")


def entry_value(x):
    return float(Fraction(x)) if isinstance(x, str) else float(x)


def load(path):
    with open(path) as f:
        return json.load(f)


fixture_schema = Draft7Validator(load(ROOT / "schema" / "fixture.schema.json"))
capture_schema = Draft7Validator(load(ROOT / "schema" / "capture.schema.json"))

print("== fixtures ==")
fixtures = {}
for path in sorted((ROOT / "fixtures").glob("*.json")):
    fx = load(path)
    errors = sorted(fixture_schema.iter_errors(fx), key=lambda e: e.json_path)
    if errors:
        for e in errors:
            fail(f"{path.name}: {e.json_path}: {e.message}")
        continue
    if fx["id"] != path.stem:
        fail(f"{path.name}: id '{fx['id']}' does not match file name")
        continue
    for m in fx.get("matrices", []):
        rows = m["rows"]
        n = len(rows)
        if len(m["labels"]) != n or any(len(r) != n for r in rows):
            fail(f"{path.name}: matrix '{m['key']}' is not square or labels mismatch")
            continue
        for i in range(n):
            for j in range(n):
                a, b = entry_value(rows[i][j]), entry_value(rows[j][i])
                if abs(a * b - 1.0) > 1e-9:
                    fail(f"{path.name}: matrix '{m['key']}' not reciprocal at ({i},{j})")
        keys = {mm["key"] for mm in fx["matrices"]}
        exp_keys = set(fx["expected"].get("matrices", {}))
        if exp_keys - keys:
            fail(f"{path.name}: expected.matrices keys {exp_keys - keys} have no matrix definition")
    fixtures[fx["id"]] = fx
    ok(path.name)

print("== captures ==")
capture_files = sorted((ROOT / "captures").glob("*/*.json"))
if not capture_files:
    print("  (no captures recorded yet)")
for path in capture_files:
    cap = load(path)
    errors = sorted(capture_schema.iter_errors(cap), key=lambda e: e.json_path)
    if errors:
        for e in errors:
            fail(f"{path}: {e.json_path}: {e.message}")
        continue
    fx = fixtures.get(cap["fixture_id"])
    if fx is None:
        fail(f"{path}: fixture_id '{cap['fixture_id']}' does not exist")
        continue

    any_divergence = False
    for out_path, verdict in cap["matches_expected"].items():
        parts = out_path.split(".")
        # locate the captured output value
        node = cap["outputs"]
        try:
            for p in parts:
                node = node[p]
        except (KeyError, TypeError):
            fail(f"{path}: matches_expected key '{out_path}' has no matching output")
            continue
        # locate the expected value (normative or named alternate)
        exp = fx["expected"]
        try:
            for p in parts[:-1]:
                exp = exp[p]
            field = parts[-1]
            compared = verdict.get("compared_to", "expected")
            if compared != "expected":
                alts = [a for a in exp.get("alternates", []) if a["method"] == compared]
                if not alts:
                    fail(f"{path}: '{out_path}' compared_to '{compared}' not found in fixture")
                    continue
                exp_block = alts[0][field] if field in alts[0] else alts[0]
            else:
                exp_block = exp[field]
        except (KeyError, TypeError):
            fail(f"{path}: no expected value for '{out_path}'")
            continue

        tol = verdict["tolerance"]
        exp_vals = exp_block.get("values", exp_block.get("value"))
        if isinstance(exp_vals, list):
            got = node if isinstance(node, list) else node.get("values")
            within = (got is not None and len(got) == len(exp_vals)
                      and all(abs(a - b) <= tol for a, b in zip(got, exp_vals)))
        else:
            got = node
            within = got is not None and abs(got - exp_vals) <= tol
        if within != verdict["matches"]:
            fail(f"{path}: '{out_path}' matches={verdict['matches']} but recheck says {within}")
        if not verdict["matches"]:
            any_divergence = True

    if any_divergence and not cap.get("explanation"):
        fail(f"{path}: outputs diverge from expected values but no explanation is given")
    if not failures or all(str(path) not in f for f in failures):
        ok(str(path.relative_to(ROOT)))

print()
if failures:
    print(f"{len(failures)} failure(s)")
    sys.exit(1)
print(f"all checks passed ({len(fixtures)} fixtures, {len(capture_files)} captures)")
