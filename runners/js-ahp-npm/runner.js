#!/usr/bin/env node
"use strict";
/*
 * Run the MIT-licensed npm `ahp` package (https://github.com/airicyu/ahp,
 * the library used by the Comcast AHP Tool) against every fixture and check
 * its outputs against the fixtures' expected values.
 *
 * What is checked, and how:
 *
 * - priorities: the package derives priorities with the column-normalization
 *   mean (Saaty's approximate method; see AHP.calculateMatrixConsistency in
 *   its source), not the principal eigenvector. The two methods coincide
 *   exactly on perfectly consistent matrices and differ on inconsistent
 *   ones. Each fixture therefore states expected values per method: this
 *   runner checks the package against the "column-normalization-mean"
 *   alternate where one is present, and against the normative
 *   (eigenvector) values where the matrix is consistent and the methods
 *   coincide. That is a method difference between tools, documented in the
 *   fixtures - not an error on either side.
 *
 * - lambda_max, CI, CR: the package estimates lambda_max as the mean of
 *   (A*w)_i / w_i and uses the classic Saaty (1980) random-index table
 *   (RI_MAP in its source: 0.58, 0.90, 1.12, ...), which matches the
 *   fixtures' "saaty" RI table. For the fixture declared under the
 *   Alonso-Lamata RI table, the runner derives CR = CI / RI_AL(n) from the
 *   package's CI, using the RI values inlined in that fixture.
 *
 * - synthesis / global priorities: checked against the matching
 *   column-normalization-mean alternate, composed from the package's
 *   per-matrix weight vectors. (The package's end-to-end run() declines to
 *   synthesize when a matrix's CR exceeds 0.1 - by design - so composition
 *   here uses its public static per-matrix API uniformly.)
 *
 * - stability fixtures are skipped: the package does not implement
 *   sensitivity analysis. That is a scope note, not a defect.
 *
 * Exit code 0 only if every checked value is within its fixture's tolerance.
 */
const fs = require("fs");
const path = require("path");
const AHP = require("ahp");

const ROOT = path.resolve(__dirname, "..", "..");
const results = [];

function entryValue(x) {
  if (typeof x === "number") return x;
  const parts = String(x).split("/");
  return parts.length === 2 ? Number(parts[0]) / Number(parts[1]) : Number(parts[0]);
}

function toMatrix(rows) {
  return rows.map((r) => r.map(entryValue));
}

function record(fixtureId, name, got, exp, tol) {
  let within, shown;
  if (Array.isArray(exp)) {
    within =
      Array.isArray(got) &&
      got.length === exp.length &&
      got.every((v, i) => Math.abs(v - exp[i]) <= tol);
    shown = "[" + got.map((v) => v.toFixed(6)).join(" ") + "]";
  } else {
    within = Math.abs(got - exp) <= tol;
    shown = got.toFixed(6);
  }
  results.push({ fixtureId, name, within });
  console.log(`    ${within ? "pass" : "FAIL"}  ${name}: ahp ${shown} vs expected ${JSON.stringify(exp)} (tol ${tol})`);
}

// pick the expected block matching the package's method:
// the column-normalization-mean alternate if present, else the normative block
// (fixtures include that alternate for every matrix where the methods differ)
function blockFor(exp) {
  const alt = (exp.alternates || []).find((a) => a.method === "column-normalization-mean");
  return alt || exp;
}

function runFixture(file) {
  const fx = JSON.parse(fs.readFileSync(file, "utf8"));
  console.log(`== ${fx.id}`);
  if (fx.category === "stability") {
    console.log("    skip  the ahp package does not implement sensitivity analysis; stability fixtures are verified via captures.");
    results.push({ fixtureId: fx.id, name: "(skipped: stability)", within: null });
    return;
  }

  const riFixture = fx.ri_table.values;
  const weights = {}; // matrix key -> package's weight vector

  for (const mdef of fx.matrices) {
    const n = mdef.labels.length;
    const { ci, ri, cr, weightedVector } = AHP.calculateMatrixConsistency(toMatrix(mdef.rows));
    weights[mdef.key] = weightedVector;
    const lambda = ci * (n - 1) + n;
    // the package's RI table is the classic Saaty table; when the fixture
    // declares a different RI table, derive CR from the package's CI
    const crChecked = fx.ri_table.name === "saaty" ? cr : ci / riFixture[String(n)];
    const exp = fx.expected.matrices[mdef.key];
    const b = blockFor(exp);
    record(fx.id, `${mdef.key}.priorities`, weightedVector, b.priorities.values, b.priorities.tolerance);
    record(fx.id, `${mdef.key}.lambda_max`, lambda, b.lambda_max.value, b.lambda_max.tolerance);
    record(fx.id, `${mdef.key}.ci`, ci, b.ci.value, b.ci.tolerance);
    record(fx.id, `${mdef.key}.cr`, crChecked, b.cr.value, b.cr.tolerance);
  }

  if (!fx.matrices.some((m) => m.parent)) return;
  const defs = Object.fromEntries(fx.matrices.map((m) => [m.key, m]));

  // global scale factor of a matrix: 1 at the root, otherwise the parent
  // matrix's factor times the parent element's local weight
  const factor = {};
  function gfactor(key) {
    if (!(key in factor)) {
      const m = defs[key];
      if (!m.parent) {
        factor[key] = 1.0;
      } else {
        const p = defs[m.parent.matrix];
        const plocal = weights[p.key][p.labels.indexOf(m.parent.element)];
        factor[key] = gfactor(p.key) * plocal;
      }
    }
    return factor[key];
  }

  const gp = fx.expected.global_priorities;
  if (gp) {
    // a covering criterion's global priority is its matrix's factor times
    // its local weight (covering labels are unique to one matrix)
    const got = gp.labels.map((lbl) => {
      const m = fx.matrices.find((mm) => mm.labels.includes(lbl));
      return gfactor(m.key) * weights[m.key][m.labels.indexOf(lbl)];
    });
    const b = blockFor(gp);
    record(fx.id, "global_priorities", got, b.values, b.tolerance);
  }

  const syn = fx.expected.synthesis;
  if (syn) {
    // sum the matrices that compare the alternatives, each scaled by its
    // covering criterion's global priority
    const got = syn.labels.map(() => 0);
    for (const m of fx.matrices) {
      if (!m.parent) continue;
      if ([...m.labels].sort().join("|") !== [...syn.labels].sort().join("|")) continue;
      m.labels.forEach((lbl, i) => {
        got[syn.labels.indexOf(lbl)] += gfactor(m.key) * weights[m.key][i];
      });
    }
    const b = blockFor(syn);
    record(fx.id, "synthesis", got, b.values, b.tolerance);
  }
}

function main() {
  const pkg = require("ahp/package.json");
  console.log(
    `npm ahp ${pkg.version} runner; priorities: column-normalization mean (the package's documented method); RI: classic Saaty table from the package source, cross-derived where a fixture declares a different table (see header comment).\n`
  );
  const args = process.argv.slice(2);
  const files = args.length
    ? args
    : fs.readdirSync(path.join(ROOT, "fixtures")).filter((f) => f.endsWith(".json")).sort()
        .map((f) => path.join(ROOT, "fixtures", f));
  for (const f of files) runFixture(f);

  console.log("\n== summary ==");
  const byFx = new Map();
  for (const r of results) {
    if (!byFx.has(r.fixtureId)) byFx.set(r.fixtureId, []);
    byFx.get(r.fixtureId).push(r.within);
  }
  const width = Math.max(...[...byFx.keys()].map((k) => k.length));
  let failed = 0;
  for (const [fid, statuses] of byFx) {
    const checked = statuses.filter((s) => s !== null);
    if (checked.length === 0) {
      console.log(`  ${fid.padEnd(width)}  skipped (not applicable)`);
    } else if (checked.every(Boolean)) {
      console.log(`  ${fid.padEnd(width)}  pass (${checked.length} checks)`);
    } else {
      const bad = checked.filter((s) => !s).length;
      failed += bad;
      console.log(`  ${fid.padEnd(width)}  FAIL (${bad}/${checked.length} checks)`);
    }
  }
  if (failed) {
    console.log(`\n${failed} check(s) failed`);
    process.exit(1);
  }
  console.log("\nall checks passed");
}

main();
