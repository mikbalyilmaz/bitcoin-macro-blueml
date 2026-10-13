"""Writes every number and table of the project note from ../figures/*.csv, so that the text cannot drift away
from the analysis. Run from inside paper/:  python make_paper.py

Output: numbers.tex (one macro per quoted number), tab_assumptions.tex and tab_coefficients.tex (table bodies).
"""

import csv
from pathlib import Path

FIG = Path(__file__).resolve().parents[1] / "figures"
OUT = Path(__file__).resolve().parent


def read(name):
    with open(FIG / f"{name}.csv", newline="") as f:
        return list(csv.DictReader(f))


def dec(x, d):
    s = f"{float(x):.{d}f}"
    if float(s) == 0:
        s = s.lstrip("-")
    return s.replace("-", "$-$")


def floor(x, d):
    """Rounded down, for statements of the form p >= value."""
    import math
    return f"{math.floor(float(x) * 10 ** d) / 10 ** d:.{d}f}"


def pval(x, d=3):
    x = float(x)
    return "$<$0.001" if x < 0.001 else f"{x:.{d}f}"


m = {}
t1 = {r["series"]: r for r in read("table1_data")}
m["Months"] = t1["months"]["first"]
m["BtcFirst"], m["BtcLast"] = f"{float(t1['BTC/USD']['first']):,.1f}", f"{float(t1['BTC/USD']['last']):,.0f}"
m["SpxFirst"], m["SpxLast"] = f"{float(t1['SPX']['first']):,.0f}", f"{float(t1['SPX']['last']):,.0f}"
m["BtcGrowth"] = f"{float(t1['BTC/USD']['growth_pct']):,.0f}"
m["SpxGrowth"] = f"{float(t1['SPX']['growth_pct']):,.0f}"
m["CorrLevels"] = dec(t1["corr BTC-SPX levels"]["first"], 2)
m["CorrReturns"] = dec(t1["corr BTC-SPX log returns"]["first"], 2)

ur = {(r["form"], r["series"]): r for r in read("table2_unit_roots")}
lev = [r for (f, _), r in ur.items() if f == "level"]
m["LevelAdfPmin"] = floor(min(float(r["adf_p"]) for r in lev), 2)
m["CpiDiffAdfP"] = dec(ur[("difference (v1)", "CPI-U")]["adf_p"], 2)
m["CpiDiffPpP"] = pval(ur[("difference (v1)", "CPI-U")]["pp_p"])
m["InflAdfP"] = dec(ur[("v2", "CPI-U inflation")]["adf_p"], 2)
m["InflAdfLags"] = ur[("v2", "CPI-U inflation")]["adf_lags"]
m["InflPpP"] = pval(ur[("v2", "CPI-U inflation")]["pp_p"])
ret = [r for (f, _), r in ur.items() if f == "log return (v2)"]
m["RetAdfPmax"] = pval(max(float(r["adf_p"]) for r in ret))
gr = read("table3_granger")
m["GrangerPmin"] = floor(min(float(r["p"]) for r in gr), 2)

coef = {(r["form"], r["term"]): r for r in read("table4_coefficients")}
for f in ("v1", "v2"):
    F = "One" if f == "v1" else "Two"
    m[f"Rsq{F}"] = dec(coef[(f, "R2")]["coef"], 3)
m["Nobs"] = str(int(float(coef[("v2", "N")]["coef"])))
m["SpxOne"] = dec(coef[("v1", "spx")]["coef"], 2)
m["SpxTwo"] = dec(coef[("v2", "spx")]["coef"], 2)
for k, tag in (("classical", "Cl"), ("hc1", "Hc"), ("hac", "Hac")):   # LaTeX macro names: letters only
    m[f"SpxTwoSe{tag}"] = dec(coef[("v2", "spx")][f"se_{k}"], 2)
    m[f"SpxOneSe{tag}"] = dec(coef[("v1", "spx")][f"se_{k}"], 2)
m["FedOneP"] = dec(coef[("v1", "fedfunds")]["p_classical"], 3)
m["FedOnePHc"] = dec(coef[("v1", "fedfunds")]["p_hc1"], 3)
m["ConstTwo"] = dec(coef[("v2", "const")]["coef"], 2)
m["ConstTwoP"] = dec(coef[("v2", "const")]["p_hc1"], 3)
others = [float(coef[("v2", t)]["p_hc1"]) for t in ("gold", "dxy", "inflation", "fedfunds")]
m["OthersTwoPmin"] = floor(min(others), 2)

dg = {(r["form"], r["test"]): r for r in read("table5_assumptions")}
KEYS = {"RESET, powers 2 and 3": "Reset", "largest VIF": "Vif", "condition number": "Cond", "Breusch-Pagan": "Bp",
        "White": "White", "Breusch-Godfrey, 2 lags": "BgTwo", "Breusch-Godfrey, 6 lags": "BgSix",
        "Breusch-Godfrey, 12 lags": "BgTwelve", "Durbin-Watson": "Dw", "Jarque-Bera": "Jb"}
for (f, test), r in dg.items():
    F = "One" if f == "v1" else "Two"
    key = KEYS[test]
    if r["p"] not in ("", "nan"):
        m[f"{key}{F}P"] = pval(r["p"])
    m[f"{key}{F}"] = dec(r["statistic"], 2 if key not in ("Jb",) else 1)
sc = {r["form"]: r for r in read("table6_residual_scale")}
m["RhoOne"], m["RhoOneP"] = dec(sc["v1"]["spearman_abs_resid_lagged_price"], 2), pval(sc["v1"]["p"])
m["RhoTwo"], m["RhoTwoP"] = dec(sc["v2"]["spearman_abs_resid_lagged_price"], 2), pval(sc["v2"]["p"])

sim = {r["law"]: r for r in read("table8_simulation")}
m["SimReps"] = f"{int(sim['A']['reps']):,}"
m["SimTrue"] = dec(sim["A"]["true"], 2)
for law in ("A", "B"):
    for k in ("sd_ols", "sd_wls"):
        m[f"Sim{law}{'Ols' if k == 'sd_ols' else 'Wls'}"] = dec(sim[law][k], 2)
    m[f"Sim{law}Cl"] = f"{100 * float(sim[law]['cover_classical']):.1f}"
    m[f"Sim{law}Hc"] = f"{100 * float(sim[law]['cover_hc1']):.1f}"
    m[f"Sim{law}MeanOls"] = dec(sim[law]["mean_ols"], 3)
    m[f"Sim{law}MeanWls"] = dec(sim[law]["mean_wls"], 3)
m["SimVarRatio"] = dec(sim["A"]["var_ratio_max_min"], 0)

fo = {r["form"]: r for r in read("table9_forest")}
for f in ("v1", "v2"):
    F = "One" if f == "v1" else "Two"
    for k in ("r2_in_ols", "r2_in_forest", "r2_out_ols", "r2_out_forest"):
        name = {"r2_in_ols": "InOls", "r2_in_forest": "InRf", "r2_out_ols": "OutOls", "r2_out_forest": "OutRf"}[k]
        m[f"{name}{F}"] = dec(fo[f][k], 2)
m["TestFirst"], m["TestLast"], m["TestMonths"] = fo["v2"]["test_first"], fo["v2"]["test_last"], fo["v2"]["test_months"]
(OUT / "numbers.tex").write_text("".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in m.items()), encoding="utf-8")

# Table: assumptions, both forms
ORDER = [("A1 linearity", "RESET, powers 2 and 3", "RESET ($F$)"),
         ("A2 no collinearity", "largest VIF", "largest VIF"),
         ("A4 constant variance", "Breusch-Pagan", "Breusch--Pagan"),
         ("A4 constant variance", "White", "White"),
         ("A4 no autocorrelation", "Breusch-Godfrey, 2 lags", "Breusch--Godfrey, 2 lags"),
         ("A4 no autocorrelation", "Breusch-Godfrey, 6 lags", "Breusch--Godfrey, 6 lags"),
         ("A4 no autocorrelation", "Durbin-Watson", "Durbin--Watson"),
         ("not required", "Jarque-Bera", "Jarque--Bera (normality)")]
lines = []
for a, test, lab in ORDER:
    cells = []
    for f in ("v1", "v2"):
        r = dg[(f, test)]
        cells.append(dec(r["statistic"], 2))
        cells.append(pval(r["p"]) if r["p"] not in ("", "nan") else "--")
    lines.append(f"{a.split(' ', 1)[0] if a != 'not required' else '--'} & {lab} & " + " & ".join(cells) + " \\\\")
(OUT / "tab_assumptions.tex").write_text("\n".join(lines) + "\n\\bottomrule\n", encoding="utf-8")

# Table: coefficients of version 2 with three standard errors
NAMES = {"const": "constant", "gold": "gold", "spx": "S\\&P 500", "dxy": "dollar index", "inflation": "inflation",
         "fedfunds": "fed funds rate (change)"}
lines = []
for t, lab in NAMES.items():
    r = coef[("v2", t)]
    lines.append(f"{lab} & {dec(r['coef'], 2)} & {dec(r['se_classical'], 2)} & {dec(r['se_hc1'], 2)} & "
                 f"{dec(r['se_hac'], 2)} & {pval(r['p_hc1'])} \\\\")
(OUT / "tab_coefficients.tex").write_text("\n".join(lines) + "\n\\bottomrule\n", encoding="utf-8")
print(f"Wrote numbers.tex ({len(m)} macros), tab_assumptions.tex and tab_coefficients.tex.")
