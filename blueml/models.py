"""OLS, the Gauss-Markov checks, robust covariance matrices, the Monte Carlo experiment and the random forest.

The linear model y = X beta + u with n observations and k columns of X (a constant included). The Gauss-Markov
theorem: if (A1) the model is linear in beta, (A2) X has full column rank, (A3) E[u | X] = 0 and (A4)
Var(u | X) = sigma^2 I (constant variance, no correlation between observations), then the OLS estimator
b = (X'X)^{-1} X'y has the smallest variance among all estimators that are linear in y and unbiased: it is BLUE.
Normality of u is not needed for BLUE; it gives exact t and F distributions in small samples.

Author: Muhammed Ikbal Yilmaz
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan, het_white, linear_reset
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera

from .data import REGRESSORS

HAC_LAGS = 2            # version 1's Newey-West lag


def fit(df, y="btc", x=REGRESSORS):
    X = sm.add_constant(df[list(x)])
    return sm.OLS(df[y], X).fit()


def diagnostics(res):
    """One row per check. A1 linearity: RESET (squares and cubes of the fitted values). A2: largest VIF and the
    condition number of the scaled X. A4a constant variance: Breusch-Pagan and White. A4b no autocorrelation:
    Breusch-Godfrey with 2, 6 and 12 lags, and Durbin-Watson. Normality (not a Gauss-Markov assumption):
    Jarque-Bera."""
    X = res.model.exog
    u = res.resid
    vif = [variance_inflation_factor(X, i) for i in range(1, X.shape[1])]
    Xs = X[:, 1:] / X[:, 1:].std(axis=0)
    rows = [("A1 linearity", "RESET, powers 2 and 3", float(linear_reset(res, power=3, use_f=True).fvalue),
             float(linear_reset(res, power=3, use_f=True).pvalue)),
            ("A2 no collinearity", "largest VIF", float(max(vif)), np.nan),
            ("A2 no collinearity", "condition number", float(np.linalg.cond(Xs)), np.nan),
            ("A4 constant variance", "Breusch-Pagan", float(het_breuschpagan(u, X)[0]), float(het_breuschpagan(u, X)[1])),
            ("A4 constant variance", "White", float(het_white(u, X)[0]), float(het_white(u, X)[1]))]
    for L in (2, 6, 12):
        bg = acorr_breusch_godfrey(res, nlags=L)
        rows.append(("A4 no autocorrelation", f"Breusch-Godfrey, {L} lags", float(bg[0]), float(bg[1])))
    rows.append(("A4 no autocorrelation", "Durbin-Watson", float(durbin_watson(u)), np.nan))
    jb = jarque_bera(u)
    rows.append(("normality (not A1-A4)", "Jarque-Bera", float(jb[0]), float(jb[1])))
    return pd.DataFrame(rows, columns=["assumption", "test", "statistic", "p"])


def standard_errors(res, hac_lags=HAC_LAGS):
    """Classical, White (HC1) and Newey-West (HAC, Bartlett kernel, `hac_lags` lags) standard errors."""
    model = res.model
    out = pd.DataFrame({"coef": res.params, "se_classical": res.bse,
                        "se_hc1": model.fit(cov_type="HC1").bse,
                        "se_hac": model.fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags}).bse})
    for k in ("classical", "hc1", "hac"):
        out[f"p_{k}"] = 2 * stats.norm.sf(np.abs(out["coef"] / out[f"se_{k}"])) if k != "classical" else res.pvalues
    return out


# ------------------------------------------------------------------------------------------ Monte Carlo
def monte_carlo(X, beta, sigma, weights, reps=20_000, seed=42, focus=1):
    """Draws y = X beta + u with fixed X, `reps` times, for two error laws:
       "A": u_t ~ N(0, sigma^2), the Gauss-Markov assumptions hold;
       "B": u_t ~ N(0, sigma^2 s_t^2) with s_t^2 = (1 / weights_t) / mean(1 / weights), the variance changes over
            time (A4 fails) while the average variance is the same.
    Two linear unbiased estimators of beta: OLS, b = (X'X)^{-1} X'y, and weighted least squares with the weights
    w_t, b_w = (X'WX)^{-1} X'Wy. Both are linear in y and unbiased under either law. Under A, OLS is BLUE; under B,
    WLS with w_t proportional to 1/Var(u_t) is (generalised least squares).
    Also records whether the classical and the White (HC1) 95% intervals of the OLS coefficient `focus` contain the
    true value. Returns a dict of arrays per law."""
    rng = np.random.default_rng(seed)
    X = np.asarray(X, float)
    n, k = X.shape
    w = np.asarray(weights, float)
    s2 = (1 / w) / np.mean(1 / w)
    XtX_inv = np.linalg.inv(X.T @ X)
    A_ols = XtX_inv @ X.T                                  # b = A_ols y
    XtW = X.T * w
    A_wls = np.linalg.inv(XtW @ X) @ XtW
    H = X @ A_ols
    lev = np.diag(H)
    z = stats.norm.ppf(0.975)
    out = {}
    for law in ("A", "B"):
        sd = sigma * (np.ones(n) if law == "A" else np.sqrt(s2))
        U = rng.standard_normal((reps, n)) * sd
        Y = X @ beta + U
        b = Y @ A_ols.T
        bw = Y @ A_wls.T
        e = Y - b @ X.T
        s2_hat = (e ** 2).sum(axis=1) / (n - k)
        se_cl = np.sqrt(s2_hat * XtX_inv[focus, focus])
        meat = (A_ols[focus] ** 2)                         # HC1: sum_t a_t^2 e_t^2 * n/(n-k)
        se_hc1 = np.sqrt((e ** 2 @ meat) * n / (n - k))
        bt = beta[focus]
        out[law] = {"ols": b[:, focus], "wls": bw[:, focus],
                    "cover_classical": np.abs(b[:, focus] - bt) <= z * se_cl,
                    "cover_hc1": np.abs(b[:, focus] - bt) <= z * se_hc1,
                    "sd_ols_theory": float(np.sqrt((A_ols[focus] ** 2 * sd ** 2).sum())),
                    "sd_wls_theory": float(np.sqrt((A_wls[focus] ** 2 * sd ** 2).sum())),
                    "lev_max": float(lev.max())}
    return out


# ------------------------------------------------------------------------------------------ random forest
def make_forest(seed=42):
    """The random forest of version 1: 500 trees, unrestricted depth, at least 2 observations to split."""
    from sklearn.ensemble import RandomForestRegressor
    return RandomForestRegressor(n_estimators=500, random_state=seed, max_depth=None, min_samples_split=2, n_jobs=-1)


def expanding_predictions(df, test_months, y="btc", x=REGRESSORS):
    """For each of the last `test_months` months t: OLS and the random forest are fitted on all earlier months and
    applied to the regressors of month t (the same month: like version 1, this measures how well the fitted
    relation carries over to new months, not a forecast); the benchmark is the mean of y over earlier months."""
    rows = []
    X = df[list(x)].values
    Y = df[y].values
    for t in range(len(df) - test_months, len(df)):
        Xtr, ytr = X[:t], Y[:t]
        ols = np.linalg.lstsq(np.column_stack([np.ones(t), Xtr]), ytr, rcond=None)[0]
        rf = make_forest().fit(Xtr, ytr)
        rows.append({"month": df.index[t], "actual": Y[t], "mean": ytr.mean(),
                     "ols": float(ols[0] + X[t] @ ols[1:]), "forest": float(rf.predict(X[t:t + 1])[0])})
    return pd.DataFrame(rows).set_index("month")


def r2_against(actual, pred, bench):
    return float(1 - np.sum((actual - pred) ** 2) / np.sum((actual - bench) ** 2))
