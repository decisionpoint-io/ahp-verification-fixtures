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
    if isinstance(x, str):
        num, _, den = x.partition("/")
        return float(Fraction(num) / Fraction(den)) if den else float(Fraction(num))
    return float(x)


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
        # null entries (e.g. "no feasible change" in stability vectors) match
        # only null entries
        within = len(got) == len(exp) and all(
            (a is None) == (b is None) and (a is None or abs(a - b) <= tol)
            for a, b in zip(got, exp))
        shown = "[" + " ".join("null" if v is None else f"{v:.6f}" for v in got) + "]"
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

    defs = {m["key"]: m for m in fx["matrices"]}
    for field in ("global_priorities", "synthesis"):
        block = fx["expected"].get(field)
        if not block:
            continue
        blocks = [(block.get("method", "principal-eigenvector"), block)] + [
            (alt["method"], alt) for alt in block.get("alternates", [])]
        for method, b in blocks:
            wset = weights[method]

            # global scale factor of a matrix: 1 at the root, otherwise the
            # parent matrix's factor times the parent element's local weight
            factor = {}

            def gfactor(key):
                if key not in factor:
                    mdef = defs[key]
                    if not mdef.get("parent"):
                        factor[key] = 1.0
                    else:
                        pkey = mdef["parent"]["matrix"]
                        plocal = dict(zip(defs[pkey]["labels"], wset[pkey]))
                        factor[key] = gfactor(pkey) * plocal[mdef["parent"]["element"]]
                return factor[key]

            if field == "global_priorities":
                # an element's global priority is its matrix's factor times
                # its local weight (covering labels are unique to one matrix)
                G = {}
                for m in fx["matrices"]:
                    for lbl, lw in zip(m["labels"], wset[m["key"]]):
                        if lbl in block["labels"]:
                            G[lbl] = gfactor(m["key"]) * lw
                got = [G[lbl] for lbl in block["labels"]]
            else:
                # synthesis: sum the matrices that compare the alternatives,
                # each scaled by its covering criterion's global priority
                got = np.zeros(len(block["labels"]))
                for m in fx["matrices"]:
                    if m.get("parent") and set(m["labels"]) == set(block["labels"]):
                        aligned = dict(zip(m["labels"], wset[m["key"]]))
                        got += gfactor(m["key"]) * np.array(
                            [aligned[lbl] for lbl in block["labels"]])
            check(f"{field}[{method}]", list(got), b)

    stability = fx["expected"].get("stability")
    if stability and "percent_top" in stability:
        run_percent_top(fx, weights["principal-eigenvector"], stability["percent_top"])


def run_percent_top(fx, wset, pt):
    """Recompute the Percent-Top criterion-weight thresholds of a one-level
    hierarchy under both documented conventions: 'theorem-1' changes only the
    selected weight (Triantaphyllou & Sanchez 1997, Theorem 1 with the
    feasibility condition that the new weight stays in [0, 1]); the
    'proportional-redistribution' alternate also rescales the remaining
    weights so that the sum stays 1. A null threshold means no feasible
    change displaces the top alternative."""
    root = next(m for m in fx["matrices"] if not m.get("parent"))
    crits = pt["criteria"]
    rootw = dict(zip(root["labels"], wset[root["key"]]))
    w = np.array([rootw[c] for c in crits])
    alt_labels = fx["expected"]["synthesis"]["labels"]
    A = np.zeros((len(alt_labels), len(crits)))
    for m in fx["matrices"]:
        if m.get("parent") and m["parent"]["element"] in crits:
            local = dict(zip(m["labels"], wset[m["key"]]))
            A[:, crits.index(m["parent"]["element"])] = [local[l] for l in alt_labels]
    P = A @ w
    top = int(np.argmax(P))

    def thresholds(redistribute):
        rels, new_ws = [], []
        for k in range(len(crits)):
            best = None
            for i in range(len(alt_labels)):
                if i == top:
                    continue
                if redistribute:
                    d = A[i, k] - A[top, k]
                    rest = ((P[i] - P[top]) - w[k] * d) / (1 - w[k])
                    denom = d - rest
                    if abs(denom) < 1e-14:
                        continue
                    x = -rest / denom
                    if not (1e-9 < x < 1 - 1e-9):
                        continue
                else:
                    d = A[top, k] - A[i, k]
                    if abs(d) < 1e-14:
                        continue
                    x = w[k] - (P[top] - P[i]) / d
                    if not (0 <= x <= 1):
                        continue
                rel = (x - w[k]) / w[k] * 100
                if best is None or abs(rel) < abs(best[0]):
                    best = (rel, x)
            rels.append(best[0] if best else None)
            new_ws.append(best[1] if best else None)
        return rels, new_ws

    blocks = [("theorem-1", pt)] + [(alt["method"], alt) for alt in pt.get("alternates", [])]
    for method, block in blocks:
        rels, new_ws = thresholds(redistribute=(method == "proportional-redistribution"))
        check(f"stability.percent_top[{method}].relative_change_percent",
              rels, block["relative_change_percent"])
        check(f"stability.percent_top[{method}].new_weight",
              new_ws, block["new_weight"])


paths = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "fixtures").glob("*.json"))
for p in paths:
    run_fixture(p)
print()
if failures:
    print(f"{len(failures)} value(s) did not recompute")
    sys.exit(1)
print("every stated value recomputes from the fixture inputs")
