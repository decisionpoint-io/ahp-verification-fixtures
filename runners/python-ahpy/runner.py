#!/usr/bin/env python3
"""Run the AHPy library (https://github.com/PhilipGriffith/AHPy) against every
fixture and check its outputs against the fixtures' expected values.

What is checked, and how:

* priorities / synthesis / global priorities - AHPy derives priorities with
  the principal-eigenvector method (power iteration), so its outputs are
  checked against each fixture's normative expected values, which use the
  same documented method.

* lambda_max, CI, CR - AHPy reports a consistency ratio but not lambda_max or
  CI. It also uses its own random-index tables: 'dd' (Donegan & Dodd 1991,
  its default) and 'saaty', which in AHPy are the estimates printed in
  Saaty's Theory and Applications of the Analytic Network Process (2005),
  p. 31 - values that differ from the 1980 table used by the fixtures
  (for example 1.35 vs 1.32 at n=7). This is an RI-table difference, not an
  arithmetic one. The runner therefore reconstructs, from AHPy's reported CR
  and AHPy's own RI table:

      CI         = CR_reported * RI_ahpy(n)
      lambda_max = CI * (n - 1) + n
      CR         = CI / RI_fixture(n)

  and checks those against the expected values. The reconstruction uses only
  AHPy's documented RI values and the definitions of CI and CR.

* stability fixtures are skipped: AHPy does not implement sensitivity
  analysis. That is a scope note, not a defect.

Exit code 0 only if every checked value is within its fixture's tolerance.
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import ahpy

ROOT = Path(__file__).resolve().parent.parent.parent

# AHPy's 'saaty' random-index estimates (ahpy.py, _compute_consistency_ratio;
# from Saaty, Theory and Applications of the Analytic Network Process, 2005, p. 31).
RI_AHPY_SAATY = {3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35, 8: 1.40, 9: 1.45, 10: 1.49}

PRECISION = 7
results = []  # (fixture, check, status)


def entry_value(x):
    return float(Fraction(x)) if isinstance(x, str) else float(x)


def comparisons(mdef):
    labels, rows = mdef["labels"], mdef["rows"]
    return {(labels[i], labels[j]): entry_value(rows[i][j])
            for i in range(len(labels)) for j in range(i + 1, len(labels))}


def record(fixture_id, name, got, exp, tol):
    if isinstance(exp, list):
        within = len(got) == len(exp) and all(abs(a - b) <= tol for a, b in zip(got, exp))
        shown = "[" + " ".join(f"{v:.6f}" for v in got) + "]"
    else:
        within = abs(got - exp) <= tol
        shown = f"{got:.6f}"
    results.append((fixture_id, name, within))
    mark = "pass" if within else "FAIL"
    print(f"    {mark}  {name}: ahpy {shown} vs expected {exp} (tol {tol})")


def check_matrix(fixture_id, key, cmp_obj, exp, n, ri_fixture):
    w = [float(cmp_obj.target_weights[lbl]) for lbl in exp["_labels"]]
    record(fixture_id, f"{key}.priorities", w,
           exp["priorities"]["values"], exp["priorities"]["tolerance"])
    cr_reported = float(cmp_obj.consistency_ratio)
    if n >= 3:
        ci = cr_reported * RI_AHPY_SAATY[n]
        cr = ci / ri_fixture[str(n)]
    else:
        ci, cr = 0.0, 0.0
    lam = ci * (n - 1) + n
    record(fixture_id, f"{key}.lambda_max", lam,
           exp["lambda_max"]["value"], exp["lambda_max"]["tolerance"])
    record(fixture_id, f"{key}.ci", ci, exp["ci"]["value"], exp["ci"]["tolerance"])
    record(fixture_id, f"{key}.cr", cr, exp["cr"]["value"], exp["cr"]["tolerance"])


def run_fixture(path):
    fx = json.load(open(path))
    print(f"== {fx['id']}")
    if fx["category"] == "stability":
        print("    skip  AHPy does not implement sensitivity analysis; "
              "stability fixtures are verified via captures.")
        results.append((fx["id"], "(skipped: stability)", None))
        return

    ri_fixture = fx["ri_table"]["values"]
    cmps = {}
    for mdef in fx["matrices"]:
        c = ahpy.Compare(mdef["key"], comparisons(mdef),
                         precision=PRECISION, random_index="saaty")
        cmps[mdef["key"]] = (c, mdef)

    for key, (c, mdef) in cmps.items():
        exp = dict(fx["expected"]["matrices"][key])
        exp["_labels"] = mdef["labels"]
        check_matrix(fx["id"], key, c, exp, len(mdef["labels"]), ri_fixture)

    # hierarchy composition: attach child Compare objects (renamed to their
    # parent element) to the root, then read AHPy's composed weights
    children = [(key, mdef) for key, (c, mdef) in cmps.items() if mdef.get("parent")]
    if children:
        root_key = next(k for k, (c, m) in cmps.items() if not m.get("parent"))
        root_def = cmps[root_key][1]
        kid_objs = []
        for key, mdef in children:
            kid_objs.append(ahpy.Compare(mdef["parent"]["element"], comparisons(mdef),
                                         precision=PRECISION, random_index="saaty"))
        root = ahpy.Compare(root_key, comparisons(root_def),
                            precision=PRECISION, random_index="saaty")
        root.add_children(kid_objs)

        gp = fx["expected"].get("global_priorities")
        if gp:
            # composed leaf weights; elements without children keep their own
            # (root-level) weight as their global priority
            child_elements = {m["parent"]["element"] for _, m in children}
            got = []
            label_map = {}
            for (key, mdef), kid in zip(children, kid_objs):
                for lbl in mdef["labels"]:
                    label_map[lbl] = float(kid.global_weights[lbl])
            for lbl in root_def["labels"]:
                if lbl not in child_elements:
                    label_map[lbl] = float(root.local_weights[lbl])
            got = [label_map[lbl] for lbl in gp["labels"]]
            record(fx["id"], "global_priorities", got, gp["values"], gp["tolerance"])

        syn = fx["expected"].get("synthesis")
        if syn:
            got = [float(root.target_weights[lbl]) for lbl in syn["labels"]]
            record(fx["id"], "synthesis", got, syn["values"], syn["tolerance"])


def main():
    paths = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "fixtures").glob("*.json"))
    print(f"AHPy {getattr(ahpy, '__version__', '(version not exposed)')} runner; "
          f"priorities: principal eigenvector; CR cross-derived from AHPy's RI table "
          f"to the fixture's declared RI table (see header comment).\n")
    for p in paths:
        run_fixture(p)

    print("\n== summary ==")
    by_fx = {}
    for fid, name, status in results:
        by_fx.setdefault(fid, []).append(status)
    width = max(len(f) for f in by_fx)
    failed = 0
    for fid, statuses in by_fx.items():
        checked = [s for s in statuses if s is not None]
        if not checked:
            print(f"  {fid:<{width}}  skipped (not applicable)")
        elif all(checked):
            print(f"  {fid:<{width}}  pass ({len(checked)} checks)")
        else:
            bad = sum(1 for s in checked if not s)
            failed += bad
            print(f"  {fid:<{width}}  FAIL ({bad}/{len(checked)} checks)")
    if failed:
        print(f"\n{failed} check(s) failed")
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
