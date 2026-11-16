# Runner: AHPy (Python)

Runs [AHPy](https://github.com/PhilipGriffith/AHPy) against every fixture and
checks its outputs against the fixtures' expected values.

```bash
pip install -r requirements.txt
python3 runner.py            # all fixtures
python3 runner.py ../../fixtures/drinks-saaty-2008.json
```

## How the tool's outputs map onto the fixtures

| Output | AHPy behaviour | How it is checked |
| --- | --- | --- |
| priorities | principal eigenvector (power iteration) | directly against the fixtures' normative expected values, which use the same documented method |
| synthesis / global priorities | hierarchy composition via `add_children` | directly against the fixtures' expected values |
| CR | reported; AHPy offers two RI tables: `dd` (Donegan & Dodd 1991, the default) and `saaty`, which in AHPy carries the estimates from Saaty's *Theory and Applications of the Analytic Network Process* (2005), p. 31 | see below |
| lambda_max, CI | not exposed | reconstructed from the reported CR (see below) |

AHPy's `saaty` RI values (0.52, 0.89, 1.11, 1.25, 1.35, ... from the 2005 ANP
book) differ from the Saaty (1980) table the fixtures declare (0.58, 0.90,
1.12, 1.24, 1.32, ...). AHPy's default `dd` table was checked against
Donegan & Dodd (1991) directly — it matches their "Actual RI" column
(0.4914, 0.8286, 1.0591, ...) exactly. Both are published random-index tables; a CR computed
under one is not comparable with a CR computed under the other. The runner
therefore reconstructs, using only AHPy's documented RI values and the
definitions of CI and CR:

```
CI         = CR_reported x RI_ahpy(n)
lambda_max = CI x (n - 1) + n
CR         = CI / RI_fixture(n)
```

and checks those against the expected values. This removes the RI table from
the comparison, which is exactly the point the `ri-table-*` fixture pair
makes.

Stability fixtures are skipped: AHPy does not implement sensitivity analysis
(a scope note, not a defect).
