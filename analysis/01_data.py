"""Analysis 1: the data, stationarity, and which form of the variables the regression should use.

Why: the Gauss-Markov theorem is about a linear model with constant error variance. Version 1 regressed the change
of the Bitcoin price in US dollars on changes of the other variables. Bitcoin rose from 218 to 115,765 dollars, so
a typical monthly change in dollars grows with the price level, whatever the model; the log return does not.

Design:
* Table 1: first and last values, growth, and the correlation of Bitcoin with the S&P 500 in levels and in returns.
* Table 2: ADF and Phillips-Perron tests (version 1's tests, constant only) on the levels, version 1's differences
  and version 2's log returns and inflation.
* Table 3: version 1's Granger causality tests (S&P 500 returns to Bitcoin returns, 1 to 6 lags), re-computed.
* Figure 1: (a) Bitcoin and the S&P 500, January 2015 = 100, log scale; (b) the dependent variable of version 1,
  the monthly change of Bitcoin in US dollars; (c) the dependent variable of version 2, the monthly log return.
"""

import numpy as np
import pandas as pd
from arch.unitroot import PhillipsPerron
from statsmodels.tsa.stattools import adfuller, grangercausalitytests

from common import save_table
from blueml.data import load, v1_differences, v2_returns
from blueml.style import BLUE, INK, MUTED, decimal_axis, end_label, event_line, save_figure, source_note, use_style

d = load()
dv1, dv2 = v1_differences(d), v2_returns(d)

# Table 1
rows = []
for col in d.columns:
    s = d[col]
    rows.append({"series": col, "first": float(s.iloc[0]), "last": float(s.iloc[-1]),
                 "growth_pct": float(100 * (s.iloc[-1] / s.iloc[0] - 1)), "min": float(s.min()), "max": float(s.max())})
lr = dv2[["btc", "spx"]]
rows.append({"series": "corr BTC-SPX levels", "first": float(d["BTC/USD"].corr(d["SPX"]))})
rows.append({"series": "corr BTC-SPX log returns", "first": float(lr["btc"].corr(lr["spx"]))})
rows.append({"series": "months", "first": len(d)})
save_table(rows, "table1_data")


def unit_root(x):
    x = x.dropna()
    a = adfuller(x, autolag="AIC")
    pp = PhillipsPerron(x)
    return {"n": len(x), "adf": float(a[0]), "adf_p": float(a[1]), "adf_lags": int(a[2]),
            "pp": float(pp.stat), "pp_p": float(pp.pvalue)}


rows = []
for col in d.columns:
    rows.append({"form": "level", "series": col, **unit_root(d[col])})
NAMES = {"btc": "BTC/USD", "gold": "XAU/USD", "spx": "SPX", "dxy": "DXY", "inflation": "CPI-U", "fedfunds": "FEDFUNDS"}
for k, v in NAMES.items():
    rows.append({"form": "difference (v1)", "series": v, **unit_root(dv1[k])})
for k, v in NAMES.items():
    label = {"inflation": "CPI-U inflation", "fedfunds": "FEDFUNDS change"}.get(k, v)
    rows.append({"form": "log return (v2)" if k not in ("inflation", "fedfunds") else "v2", "series": label,
                 **unit_root(dv2[k])})
save_table(rows, "table2_unit_roots")

# Table 3: version 1's Granger test on log returns (log of BTC and SPX, first differences)
lr_v1 = np.log(d[["BTC/USD", "SPX"]] / d[["BTC/USD", "SPX"]].shift(1)).dropna()
g = grangercausalitytests(lr_v1[["BTC/USD", "SPX"]], maxlag=6)
save_table([{"lag": L, "F": float(g[L][0]["ssr_ftest"][0]), "p": float(g[L][0]["ssr_ftest"][1])} for L in range(1, 7)],
           "table3_granger")

use_style()


def draw():
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib import ticker
    fig = plt.figure(figsize=(4.75, 3.3), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1])
    ax = fig.add_subplot(gs[0, :])
    for col, color, lab in (("BTC/USD", BLUE, "Bitcoin"), ("SPX", INK, "S&P 500")):
        idx = 100 * d[col] / d[col].iloc[0]
        ax.plot(idx.index, idx.values, color=color, lw=1.6)
        end_label(ax, idx.index[-1], idx.iloc[-1], f"{lab} {idx.iloc[-1]:,.0f}", color, dx=3)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(ticker.FixedLocator([50, 100, 1_000, 10_000, 100_000]))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.yaxis.set_minor_locator(ticker.NullLocator())
    ax.set_xlim(d.index[0], d.index[-1] + pd.Timedelta(days=900))
    ax.spines["bottom"].set_bounds(mdates.date2num(d.index[0]), mdates.date2num(d.index[-1]))
    ax.set_title("(a) Prices, January 2015 = 100, log scale")
    source_note(ax, "Monthly, 2015-01 to 2025-07 (Source: version 1's file:\nInvesting.com, FRED, BLS)", x=0.02, y=0.97,
                va="top")
    axes = [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
    ax = axes[0]
    ax.bar(dv1.index, dv1["btc"].values / 1000, width=25, color=INK)
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_title("(b) Version 1: change, thousand US\\$")
    ax = axes[1]
    ax.bar(dv2.index, dv2["btc"].values, width=25, color=BLUE)
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_title("(c) Version 2: log return, %")
    fig.axes[0].set_xticks([pd.Timestamp(f"{y}-01-01") for y in range(2016, 2026, 2)])
    for a in axes:
        a.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (2016, 2020, 2024)])
    for a in [fig.axes[0]] + axes:
        a.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for a in axes:
        decimal_axis(a)
    return fig


save_figure("fig1_data", draw, lambda: "Figure 1. Bitcoin and the S&P 500, and the two dependent variables")
