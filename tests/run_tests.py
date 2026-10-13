"""Unit tests. Run from the repository root:  python tests/run_tests.py

Each result is compared with an independent computation: the data file read cell by cell, OLS and the robust
covariance matrices written out in matrix algebra, auxiliary regressions written out for the tests, exact variances
for the Monte Carlo, a perturbation check for the out-of-sample predictions, and the printed output of version 1.
"""

import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blueml.data import REGRESSORS, load, v1_differences, v2_returns  # noqa: E402
from blueml.models import diagnostics, expanding_predictions, fit, monte_carlo, standard_errors  # noqa: E402

warnings.simplefilter("ignore")
failed = 0


def check(name, ok):
    global failed
    print(f"{'ok' if ok else 'FAIL':<5}{name}")
    if not ok:
        failed += 1


# 1. Data: the file of version 1, monthly index, transformations written out
raw = pd.read_excel(Path(__file__).resolve().parents[1] / "data" / "dataset1.xlsx")
d = load()
ok = len(d) == 127 and d.index[0] == pd.Timestamp("2015-01-01") and d.index[-1] == pd.Timestamp("2025-07-01")
ok &= str(raw["date"].iloc[0]) == "2015-01-01 04:50:10" and d.index.freqstr == "MS"
ok &= np.allclose(d["BTC/USD"].values, raw["BTC/USD"].values) and np.allclose(d["CPI-U"].values, raw["CPI-U"].values)
v2 = v2_returns(d)
t = 50
ok &= abs(v2["btc"].iloc[t] - 100 * np.log(d["BTC/USD"].iloc[t + 1] / d["BTC/USD"].iloc[t])) < 1e-12
ok &= abs(v2["inflation"].iloc[t] - 100 * np.log(d["CPI-U"].iloc[t + 1] / d["CPI-U"].iloc[t])) < 1e-12
ok &= abs(v2["fedfunds"].iloc[t] - (d["FEDFUNDS"].iloc[t + 1] - d["FEDFUNDS"].iloc[t])) < 1e-12
v1 = v1_differences(d)
ok &= abs(v1["btc"].iloc[t] - (d["BTC/USD"].iloc[t + 1] - d["BTC/USD"].iloc[t])) < 1e-9 and len(v1) == len(v2) == 126
check("data: 127 months from the file of version 1 (first date fixed); differences and log returns by hand", ok)

# 2. OLS and the three covariance matrices written out
res = fit(v2)
X = res.model.exog
y = res.model.endog
n, k = X.shape
XtX_inv = np.linalg.inv(X.T @ X)
b = XtX_inv @ X.T @ y
e = y - X @ b
V_cl = (e @ e / (n - k)) * XtX_inv
V_hc1 = XtX_inv @ (X.T * e ** 2) @ X @ XtX_inv * n / (n - k)
S = (X * e[:, None]).T @ (X * e[:, None])
for L in (1, 2):
    G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
    S += (1 - L / 3) * (G + G.T)
V_hac = XtX_inv @ S @ XtX_inv
se = standard_errors(res)
ok = np.allclose(b, res.params.values) and np.allclose(np.sqrt(np.diag(V_cl)), se["se_classical"].values)
ok &= np.allclose(np.sqrt(np.diag(V_hc1)), se["se_hc1"].values) and np.allclose(np.sqrt(np.diag(V_hac)), se["se_hac"].values)
check("OLS, classical, White (HC1) and Newey-West (2 lags, Bartlett) standard errors equal the matrix formulas", ok)

# 3. Breusch-Pagan and Breusch-Godfrey as n R^2 of their auxiliary regressions
dg = diagnostics(res).set_index("test")
aux = np.linalg.lstsq(X, e ** 2, rcond=None)[0]
f2 = X @ aux
r2_bp = 1 - np.sum((e ** 2 - f2) ** 2) / np.sum((e ** 2 - (e ** 2).mean()) ** 2)
lagged = np.column_stack([np.r_[np.zeros(L), e[:-L]] for L in (1, 2)])
Z = np.column_stack([X, lagged])
fz = Z @ np.linalg.lstsq(Z, e, rcond=None)[0]
r2_bg = 1 - np.sum((e - fz) ** 2) / np.sum((e - e.mean()) ** 2)
ok = abs(dg.loc["Breusch-Pagan", "statistic"] - n * r2_bp) < 1e-8
ok &= abs(dg.loc["Breusch-Pagan", "p"] - stats.chi2.sf(n * r2_bp, k - 1)) < 1e-10
ok &= abs(dg.loc["Breusch-Godfrey, 2 lags", "statistic"] - n * r2_bg) < 1e-8
ok &= abs(dg.loc["Durbin-Watson", "statistic"] - np.sum(np.diff(e) ** 2) / np.sum(e ** 2)) < 1e-12
check("Breusch-Pagan and Breusch-Godfrey equal n R^2 of the auxiliary regressions; Durbin-Watson by hand", ok)

# 4. Monte Carlo: both estimators unbiased, simulated s.d. equal to the exact s.d., Gauss-Markov inequality
w = 1 / (0.25 + ((v2["spx"] - v2["spx"].mean()) / v2["spx"].std()).values ** 2)
mc = monte_carlo(X, b, np.sqrt(res.scale), w, reps=20_000, seed=1, focus=2)
ok = True
for law, r in mc.items():
    for key in ("ols", "wls"):
        sd_exact = r[f"sd_{key}_theory"]
        ok &= abs(r[key].mean() - b[2]) < 4 * sd_exact / np.sqrt(20_000)
        ok &= abs(r[key].std() / sd_exact - 1) < 0.03
ok &= mc["A"]["sd_ols_theory"] < mc["A"]["sd_wls_theory"] and mc["B"]["sd_wls_theory"] < mc["B"]["sd_ols_theory"]
check("simulation: OLS and WLS unbiased, s.d. as the exact formula; OLS best under A, WLS (GLS) best under B", ok)

# 5. Out-of-sample predictions use only earlier months
small = v2.iloc[:40].copy()
p1 = expanding_predictions(small, 3)
pert = small.copy()
pert.iloc[-2:, pert.columns.get_loc("btc")] += 500.0          # change the realized returns of the last two months
p2 = expanding_predictions(pert, 3)
ols_first = np.linalg.lstsq(np.column_stack([np.ones(37), small[REGRESSORS].values[:37]]), small["btc"].values[:37],
                            rcond=None)[0]
ok = np.isclose(p1["ols"].iloc[0], ols_first[0] + small[REGRESSORS].values[37] @ ols_first[1:])
ok &= np.isclose(p1["forest"].iloc[0], p2["forest"].iloc[0]) and np.isclose(p1["ols"].iloc[0], p2["ols"].iloc[0])
ok &= np.isclose(p1["mean"].iloc[0], small["btc"].values[:37].mean())
check("out-of-sample predictions: fitted on earlier months only; changing later months leaves them unchanged", ok)

# 6. Version 1's own code reproduces its printed results
from blueml.legacy import run_v1  # noqa: E402

ns, printed = run_v1()
v1res = ns["ols_model"]
ok = round(v1res.rsquared, 3) == 0.223 and abs(v1res.params["ΔSPX"] - 16.1312) < 5e-4
ok &= "Durbin-Watson statistic: 1.6739" in printed and "Statistic: 107.9186, p-value: 0.0000" in printed
ok &= abs(float(re.search(r"'LM p-value': np.float64\(([\d.e-]+)\)", printed).group(1)) - 0.0386) < 5e-4
ok &= "0.9398" in printed and "0.3586" in printed and "Lag 1:  F-test p=0.1965" in printed
r2_rf = float(re.search(r"R² Score: ([\d.]+)", printed).group(1))
ok &= abs(r2_rf - 0.8705) < 0.01
check(f"version 1's own code: R2 0.223, SPX 16.1312, DW 1.6739, BP p 0.0386, JB, correlations, Granger, "
      f"forest R2 {r2_rf:.4f}", ok)

print(f"\n{failed} check(s) failed.")
sys.exit(1 if failed else 0)
