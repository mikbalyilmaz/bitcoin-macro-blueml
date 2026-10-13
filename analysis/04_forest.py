"""Analysis 4: the random forest of version 1, in sample and on months it has not seen.

Why: version 1 reported R^2 = 0.87 for a random forest (500 trees, unrestricted depth) fitted to the 126 months and
evaluated on the same 126 months, and compared it with OLS (R^2 = 0.22). A forest with fully grown trees nearly
reproduces the months it was fitted on, so that comparison measures memory, not fit to new data.

Design: both forms of the variables (version 1: differences of levels; version 2: log returns). In sample: R^2 of
OLS and of the forest on all months. Out of sample: for each of the last 60 months, OLS and the forest are fitted on
all earlier months and applied to that month's regressors (the regressors are of the same month, as in version 1,
so this tests whether the fitted relation carries over, not a forecast); R^2 against the mean of the earlier months,
R^2_OS = 1 - sum (y - yhat)^2 / sum (y - ybar)^2.
* Table 9: in-sample and out-of-sample R^2 of OLS and the forest for both forms.
* Figure 4: the same as bars.
"""

import numpy as np

from common import save_table
from blueml.data import load, v1_differences, v2_returns, REGRESSORS
from blueml.models import expanding_predictions, fit, make_forest, r2_against
from blueml.style import BLUE, INK, decimal_axis, save_figure, source_note, use_style

TEST = 60
d = load()
forms = {"v1": v1_differences(d), "v2": v2_returns(d)}
rows = []
preds = {}
for k, df in forms.items():
    ols = fit(df)
    rf = make_forest().fit(df[REGRESSORS].values, df["btc"].values)
    r2_rf = 1 - np.sum((df["btc"].values - rf.predict(df[REGRESSORS].values)) ** 2) / np.sum(
        (df["btc"].values - df["btc"].mean()) ** 2)
    p = expanding_predictions(df, TEST)
    preds[k] = p
    p.to_csv(f"../figures/predictions_{k}.csv", float_format="%.6f")
    rows.append({"form": k, "r2_in_ols": float(ols.rsquared), "r2_in_forest": float(r2_rf),
                 "r2_out_ols": r2_against(p["actual"], p["ols"], p["mean"]),
                 "r2_out_forest": r2_against(p["actual"], p["forest"], p["mean"]),
                 "test_first": f"{p.index[0]:%Y-%m}", "test_last": f"{p.index[-1]:%Y-%m}", "test_months": len(p)})
save_table(rows, "table9_forest")
for r in rows:
    print(r)

use_style()


def draw():
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(4.75, 2.0), constrained_layout=True, sharex=True)
    for ax, r, title in zip(axes, rows, ("(a) Version 1: differences", "(b) Version 2: log returns")):
        labels = ["OLS, in sample", "Forest, in sample", "OLS, new months", "Forest, new months"]
        vals = [r["r2_in_ols"], r["r2_in_forest"], r["r2_out_ols"], r["r2_out_forest"]]
        cols = [INK, BLUE, INK, BLUE]
        y = np.arange(4)[::-1]
        ax.barh(y, vals, color=cols, height=0.6)
        for yi, v in zip(y, vals):
            ax.text(v + (0.02 if v >= 0 else -0.02), yi, f"{v:.2f}", va="center", ha="left" if v >= 0 else "right",
                    fontsize=7, fontweight="bold")
        ax.axvline(0, color=INK, lw=0.7)
        ax.set_yticks(y, labels if ax is axes[0] else [""] * 4)
        ax.set_title(title)
        ax.set_xlim(-0.05, 1.1)
        ax.set_xlabel("$R^2$")
        decimal_axis(ax, "x")
    source_note(axes[1], f"New months: last {TEST},\neach fitted on earlier\nmonths only", x=0.98, y=0.03,
                ha="right")
    return fig


save_figure("fig4_forest", draw, lambda: "Figure 4. Random forest and OLS: fit in sample and on new months")
