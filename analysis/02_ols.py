"""Analysis 2: is OLS BLUE here? The Gauss-Markov assumptions checked one by one, for version 1's and version 2's
form of the variables.

Why: version 1 estimated the regression on first differences of the levels, found heteroskedasticity and signs of
autocorrelation, and concluded that OLS is not BLUE. A failure of the assumptions can come from the data or from
the form chosen for the variables; the two forms are compared on the same months.

Design: y_t = b0 + b1 gold_t + b2 spx_t + b3 dxy_t + b4 inflation_t + b5 fedfunds_t + u_t, 126 months, February
2015 to July 2025, (i) version 1: differences of the levels; (ii) version 2: log returns in per cent, monthly
inflation and the change of the federal funds rate.
* Table 4: coefficients with classical, White (HC1) and Newey-West (2 lags, as in version 1) standard errors.
* Table 5: the checks of each assumption (RESET, VIF, Breusch-Pagan, White, Breusch-Godfrey, Durbin-Watson) and
  Jarque-Bera, for both forms.
* Table 6: rank correlation of the absolute residual with the Bitcoin price of the previous month.
* Figure 2: residuals against the previous month's Bitcoin price, and their autocorrelations, for both forms.
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import acf

from common import save_table
from blueml.data import load, v1_differences, v2_returns
from blueml.models import diagnostics, fit, standard_errors
from blueml.style import BLUE, INK, decimal_axis, save_figure, source_note, use_style

d = load()
forms = {"v1": v1_differences(d), "v2": v2_returns(d)}
res = {k: fit(v) for k, v in forms.items()}
price_lag = d["BTC/USD"].shift(1)

rows, diag_rows, het_rows = [], [], []
for k, r in res.items():
    se = standard_errors(r)
    for term, row in se.iterrows():
        rows.append({"form": k, "term": term, **{c: float(v) for c, v in row.items()}})
    rows.append({"form": k, "term": "R2", "coef": float(r.rsquared)})
    rows.append({"form": k, "term": "N", "coef": float(r.nobs)})
    for _, row in diagnostics(r).iterrows():
        diag_rows.append({"form": k, **row.to_dict()})
    rho = stats.spearmanr(np.abs(r.resid), price_lag.loc[r.resid.index])
    het_rows.append({"form": k, "spearman_abs_resid_lagged_price": float(rho.statistic), "p": float(rho.pvalue)})
save_table(rows, "table4_coefficients")
save_table(diag_rows, "table5_assumptions")
save_table(het_rows, "table6_residual_scale")
for r in diag_rows:
    print(f"{r['form']} {r['test']:28s} {r['statistic']:10.3f}  p {r['p']:.4f}")

LAGS = 12
acfs = {k: acf(r.resid, nlags=LAGS, fft=True) for k, r in res.items()}
save_table([{"form": k, "lag": L, "acf": float(a[L])} for k, a in acfs.items() for L in range(1, LAGS + 1)],
           "table7_residual_acf")
diag = {k: pd.DataFrame([x for x in diag_rows if x["form"] == k]).set_index("test") for k in res}

use_style()


def draw():
    import matplotlib.pyplot as plt
    from matplotlib import ticker
    fig, axes = plt.subplots(2, 2, figsize=(4.75, 3.35), constrained_layout=True)
    for j, (k, color, unit) in enumerate((("v1", INK, "thousand US\\$"), ("v2", BLUE, "%"))):
        r = res[k]
        ax = axes[0, j]
        scale = 1000 if k == "v1" else 1
        ax.scatter(price_lag.loc[r.resid.index], r.resid / scale, s=6, color=color, lw=0)
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_xscale("log")
        ax.xaxis.set_major_locator(ticker.FixedLocator([300, 3_000, 30_000]))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.xaxis.set_minor_locator(ticker.NullLocator())
        ax.set_xlabel("Bitcoin price last month, US\\$")
        ax.set_title(f"({'ab'[j]}) {'Version 1' if k == 'v1' else 'Version 2'}: residual, {unit}")
        bp, wh = diag[k].loc["Breusch-Pagan", "p"], diag[k].loc["White", "p"]
        source_note(ax, f"Breusch-Pagan p = {bp:.3f}\nWhite p = {wh:.3f}", x=0.03, y=0.97, va="top")
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.45 * (hi - lo))
        decimal_axis(ax)
        ax = axes[1, j]
        band = 1.96 / np.sqrt(r.nobs)
        ax.axhspan(-band, band, color="#e6e6e6", lw=0, zorder=0)
        ax.vlines(range(1, LAGS + 1), 0, acfs[k][1:], color=color, lw=2.0)
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_ylim(-0.6, 0.4)
        ax.set_xticks([1, 3, 6, 9, 12])
        ax.set_xlabel("Lag (months)")
        ax.set_title(f"({'cd'[j]}) Autocorrelation of residuals")
        bg2, bg6 = diag[k].loc["Breusch-Godfrey, 2 lags", "p"], diag[k].loc["Breusch-Godfrey, 6 lags", "p"]
        source_note(ax, f"Breusch-Godfrey p = {bg2:.3f} (2 lags),\n{bg6:.3f} (6 lags)", x=0.03, y=0.03)
        decimal_axis(ax)
    return fig


save_figure("fig2_residuals", draw, lambda: "Figure 2. Residuals of the two regressions: variance and autocorrelation")
