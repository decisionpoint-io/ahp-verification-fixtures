#!/usr/bin/env python3
"""Recompute every derived expected value in the fixtures from the matrices
alone, and compare against what the fixture files state. This is the
reproduction path for all 'derived' provenance in this repository: anyone can
run it and confirm that the stated expected values follow from the stated
inputs by the stated methods.

Methods implemented (both are documented in each fixture's provenance):

  principal-eigenvector     the principal right eigenvector of the matrix
                            (numpy.linalg.eig; the Perron root is lambda_max),
                            normalized to sum to 1.
  column-normalization-mean Saaty's approximate method: normalize each column
                            to sum to 1 and average across columns; lambda_max
                            is estimated as the mean of (A*w)_i / w_i.

For both: CI = (lambda_max - n) / (n - 1) and CR = CI / RI(n) using the RI
table declared in the fixture.

Stability fixtures: the preferences P_i = sum_j W_j * a_ij are recomputed;
the sensitivity thresholds themselves are published values from the cited
paper (see docs/derivations.md for the full recomputation notes).

Usage: python3 tools/compute_expected.py [fixture.json ...]
       (no arguments: all fixtures)
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
failures = []


def entry_value(x):
    return float(Fraction(x)) if isinstance(x, str) else float(x)


def to_array(rows):
    return np.array([[entry_value(x) for x in r] for r in rows])


def eigenvector(A):
    n = A.shape[0]
    vals, vecs = np.linalg.eig(A)
    i = np.argmax(vals.real)
    lam = float(vals[i].real)
    w = np.abs(vecs[:, i].real)
    return w / w.sum(), lam


def column_normalization_mean(A):
    w = (A / A.sum(axis=0)).mean(axis=1)
    lam = float(np.mean((A @ w) / w))
    return w, lam


def consistency(lam, n, ri_values):
    ci = (lam - n) / (n - 1) if n > 1 else 0.0
    cr = ci / ri_values[str(n)] if n >= 3 else 0.0
    return ci, cr


def check(name, got, block, kind="value"):
    tol = block["tolerance"]
    exp = block.get("values", block.get("value"))
    if isinstance(exp, list):
        within = len(got) == len(exp) and all(abs(a - b) <= tol for a, b in zip(got, exp))
        shown = "[" + " ".join(f"{v:.6f}" for v in got) + "]"
    else:
        within = abs(got - exp) <= tol
        shown = f"{got:.6f}"
    status = "ok  " if within else "FAIL"
    print(f"    {status}  {name}: recomputed {shown} vs stated {exp} (tol {tol})")
    if not within:
        failures.append(name)


def run_fixture(path):
    fx = json.load(open(path))
    print(f"== {fx['id']} ({fx['category']})")
    if fx["category"] == "stability":
        dm = fx["decision_matrix"]
        P = to_array(dm["performance"]) @ np.array(dm["weights"])
        prefs = fx["expected"]["stability"].get("preferences")
        if prefs:
            check("preferences", P, prefs)
        print("    (sensitivity thresholds are published values; see docs/derivations.md)")
        return

    ri_values = fx["ri_table"]["values"]
    methods = {"principal-eigenvector": eigenvector,
               "column-normalization-mean": column_normalization_mean}
    weights = {m: {} for m in methods}
    for mdef in fx["matrices"]:
        key = mdef["key"]
        A = to_array(mdef["rows"])
        n = A.shape[0]
        exp = fx["expected"]["matrices"][key]
        blocks = [("principal-eigenvector", exp)] + [
            (alt["method"], alt) for alt in exp.get("alternates", [])]
        for method, block in blocks:
            w, lam = methods[method](A)
            weights[method][key] = w
            ci, cr = consistency(lam, n, ri_values)
            label = f"{key}[{method}]"
            if block.get("priorities", {}).get("provenance", {}).get("type") == "published" \
               or "provenance" not in block.get("priorities", {}):
                pass  # published values are still compared, within their stated tolerance
            check(f"{label}.priorities", w, block["priorities"])
            check(f"{label}.lambda_max", lam, block["lambda_max"])
            check(f"{label}.ci", ci, block["ci"])
            check(f"{label}.cr", cr, block["cr"])
        # fill in the other method for consistent matrices (no alternates block)
        for method in methods:
            if key not in weights[method]:
                weights[method][key], _ = methods[method](A)

    for field in ("global_priorities", "synthesis"):
        block = fx["expected"].get(field)
        if not block:
            continue
        parented = {m["key"]: m.get("parent") for m in fx["matrices"]}
        root_key = next(k for k, p in parented.items() if p is None)
        root_def = next(m for m in fx["matrices"] if m["key"] == root_key)
        blocks = [(block.get("method", "principal-eigenvector"), block)] + [
            (alt["method"], alt) for alt in block.get("alternates", [])]
        for method, b in blocks:
            wset = weights[method]
            root_w = dict(zip(root_def["labels"], wset[root_key]))
            if field == "global_priorities":
                # children replace their parent element; childless elements keep their weight
                out = dict(root_w)
                for m in fx["matrices"]:
                    if m.get("parent"):
                        pw = out.pop(m["parent"]["element"])
                        for lbl, lw in zip(m["labels"], wset[m["key"]]):
                            out[lbl] = pw * lw
                got = [out[lbl] for lbl in block["labels"]]
            else:
                # synthesis: criteria-weighted sum of per-criterion alternative priorities
                got = np.zeros(len(block["labels"]))
                for m in fx["matrices"]:
                    if m.get("parent"):
                        got += root_w[m["parent"]["element"]] * wset[m["key"]]
            check(f"{field}[{method}]", list(got), b)


paths = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "fixtures").glob("*.json"))
for p in paths:
    run_fixture(p)
print()
if failures:
    print(f"{len(failures)} value(s) did not recompute")
    sys.exit(1)
print("every stated value recomputes from the fixture inputs")
