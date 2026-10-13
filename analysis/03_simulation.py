"""Analysis 3: what BLUE means, shown with the data's own regressors (Monte Carlo).

Why: the checks of analysis 2 say whether the assumptions are rejected; they do not show what is lost when an
assumption fails. The Gauss-Markov theorem compares OLS with every other estimator that is linear in y and
unbiased. A simulation with fixed regressors makes that comparison visible.

Design: X = the regressors of version 2 (126 months) with a constant; beta and sigma = version 2's OLS estimates;
20,000 samples of y = X beta + u (seed 42) under two laws of u:
  A: u_t ~ N(0, sigma^2), the Gauss-Markov assumptions hold;
  B: Var(u_t) proportional to 0.25 + z_t^2, z_t the standardised S&P 500 return of month t: the error variance
     grows with the size of the market's move (A4 fails), with the same average variance as A.
Two linear unbiased estimators of the S&P 500 coefficient: OLS, and weighted least squares with weights
1 / (0.25 + z_t^2). Under A, OLS is BLUE and WLS is not; under B, WLS uses the true variances (generalised least
squares) and OLS is no longer best.
* Table 8: mean, standard deviation (simulated and exact) of both estimators, and the coverage of the classical and
  the White (HC1) 95% intervals of OLS, under A and B.
* Figure 3: (a), (b) the distributions of both estimators under A and B; (c) coverage of the intervals.
"""

import numpy as np

from common import save_table
from blueml.data import load, v2_returns, REGRESSORS
from blueml.models import fit, monte_carlo
from blueml.style import BLUE, INK, RED, decimal_axis, save_figure, source_note, use_style

d = load()
df = v2_returns(d)
res = fit(df)
X = res.model.exog
beta = res.params.values
sigma = float(np.sqrt(res.scale))
FOCUS = 1 + REGRESSORS.index("spx")
z = (df["spx"] - df["spx"].mean()) / df["spx"].std()
weights = 1 / (0.25 + z.values ** 2)
REPS = 20_000
mc = monte_carlo(X, beta, sigma, weights, reps=REPS, seed=42, focus=FOCUS)

rows = []
for law, r in mc.items():
    rows.append({"law": law, "true": float(beta[FOCUS]), "mean_ols": float(r["ols"].mean()),
                 "mean_wls": float(r["wls"].mean()), "sd_ols": float(r["ols"].std()), "sd_wls": float(r["wls"].std()),
                 "sd_ols_exact": r["sd_ols_theory"], "sd_wls_exact": r["sd_wls_theory"],
                 "cover_classical": float(r["cover_classical"].mean()), "cover_hc1": float(r["cover_hc1"].mean()),
                 "reps": REPS, "sigma": sigma, "var_ratio_max_min": float(weights.max() / weights.min())})
save_table(rows, "table8_simulation")
for r in rows:
    print({k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()})

use_style()


def draw():
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(4.75, 3.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1])
    bt = beta[FOCUS]
    lo = min(mc[k][e].min() for k in mc for e in ("ols", "wls"))
    hi = max(mc[k][e].max() for k in mc for e in ("ols", "wls"))
    edges = np.linspace(bt - 3.2, bt + 3.2, 120)
    for j, (law, title) in enumerate((("A", "(a) A: constant variance"), ("B", "(b) B: variance grows with |S&P move|"))):
        ax = fig.add_subplot(gs[0, j])
        r = mc[law]
        for key, color, lab in (("ols", BLUE, "OLS"), ("wls", INK, "WLS")):
            h, e = np.histogram(r[key], bins=edges, density=True)
            ax.stairs(h, e, color=color, lw=1.4)
            k = int(np.argmax(h))
        ax.axvline(bt, color=RED, ls=(0, (1, 1.4)), lw=1.3)
        ax.set_title(title)
        ax.set_xlabel("Estimate of the S&P 500 coefficient")
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        source_note(ax, f"s.d. OLS {r['ols'].std():.2f}\ns.d. WLS {r['wls'].std():.2f}", x=0.98, y=0.97, ha="right",
                    va="top")
        decimal_axis(ax, "x")
    ax0 = fig.axes[0]
    ax0.text(0.02, 0.97, "Blue: OLS\nBlack: WLS\nRed: true value", transform=ax0.transAxes, va="top", fontsize=6.6)
    ax = fig.add_subplot(gs[1, :])
    labels, vals, cols = [], [], []
    for law in ("A", "B"):
        for key, name in (("cover_classical", "classical"), ("cover_hc1", "White (HC1)")):
            labels.append(f"{law}: {name}")
            vals.append(100 * mc[law][key].mean())
            cols.append(INK if key == "cover_classical" else BLUE)
    y = np.arange(len(vals))[::-1]
    ax.barh(y, vals, color=cols, height=0.6)
    for yi, v in zip(y, vals):
        ax.text(v - 0.5, yi, f"{v:.1f}%", va="center", ha="right", fontsize=7, fontweight="bold", color="white")
    ax.axvline(95, color=RED, ls=(0, (1, 1.4)), lw=1.3)
    ax.set_yticks(y, labels)
    ax.set_xlim(60, 100)
    ax.set_title("(c) How often the 95% interval of OLS contains the true value")
    decimal_axis(ax, "x")
    return fig


save_figure("fig3_simulation", draw, lambda: "Figure 3. BLUE in a simulation with the data's regressors")
