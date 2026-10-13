# Changes

## Version 2.0.0

### New

- `blueml/` holds the data handling (version 1's differences and version 2's log returns), OLS with the checks of
  the Gauss–Markov assumptions (RESET, VIF and condition number, Breusch–Pagan, White, Breusch–Godfrey with 2, 6
  and 12 lags, Durbin–Watson, and Jarque–Bera reported separately), classical, White (HC1) and Newey–West standard
  errors, a Monte Carlo experiment, the random forest of version 1 with expanding-window predictions, and a runner
  for the notebook of version 1.
- The regression is estimated in both forms, version 1's differences of the levels and monthly log returns, with
  every check side by side.
- A simulation that shows what BLUE means: OLS against weighted least squares with fixed regressors, with constant
  error variance and with error variance that changes over the sample, and the coverage of classical and White
  95% intervals.
- The random forest and OLS evaluated on months not used in fitting (the last 60 months, each fitted on all earlier
  months).
- The data file of version 1 is stored in the repository.
- Unit tests (`tests/run_tests.py`), four figures, CSV tables, and a project note in English whose numbers are
  written from the tables.
- `CITATION.cff`, `requirements.txt`, `.gitignore`, a GitHub Actions workflow that runs the tests.

### Corrections to version 1

| # | Version 1 | Version 2 |
|---|---|---|
| 1 | The dependent variable was the monthly change of Bitcoin in US dollars. Bitcoin rose from 218.5 to 115,765 dollars, so a typical dollar change grows with the price level: the error variance cannot be constant (Breusch–Pagan $p = 0.039$, White $p = 0.013$; rank correlation of the absolute residual with last month's price 0.57). The text called these changes "Bitcoin returns". | Monthly log returns in per cent for Bitcoin, gold, the S&P 500 and the dollar index; monthly inflation; the change of the federal funds rate. With these, no check of A1, A2 or A4 rejects (Breusch–Pagan $p = 0.844$, White $p = 0.837$, Breusch–Godfrey $p = 0.421$ with 2 lags). Version 1's form is kept for comparison. |
| 2 | Normality (Jarque–Bera) was listed among the Gauss–Markov tests. | Normality is not a Gauss–Markov assumption; Jarque–Bera is reported separately, as the condition for exact $t$ and $F$ tests in small samples. |
| 3 | Autocorrelation was read from "Durbin–Watson < 2" (1.67), without critical values. | Breusch–Godfrey tests with 2, 6 and 12 lags; Durbin–Watson is reported alongside. |
| 4 | "OLS provides unbiased estimates" after the tests: unbiasedness requires $E[u \mid X] = 0$ (A3), which no residual test can check. | A3 is stated as an assumption; the note explains why the S&P 500 coefficient describes co-movement in the same month, not an effect. |
| 5 | The text said that the CPI change becomes stationary "when differenced a second time"; the notebook computes no second difference. For the first difference, ADF does not reject a unit root ($p = 0.37$). | Both tests are reported for the CPI change and for inflation (ADF $p = 0.37$ and $0.32$, Phillips–Perron $p < 0.001$); no claim about a second difference. |
| 6 | The random forest's $R^2 = 0.87$ was computed on the months it was fitted on, and the constant column of the OLS design was included as a feature. | The forest uses the five regressors only and is evaluated on months not used in fitting: $R^2$ 0.00 (differences) and 0.01 (log returns), against 0.15 and 0.17 for OLS. |
| 7 | The data file was not in the repository, and the notebook read it from an absolute path on the author's computer (`/Users/.../Gauss-Markov Project/dataset1.xlsx`); figures were saved to the same folder. | The file is in `data/`; all paths are relative to the repository. |
| 8 | The first date of the file is 2015-01-01 04:50:10. | Every date is set to the first day of its month; the file is unchanged. |
| 9 | Cells ran `pip install` and printed an execution time. | Dependencies are listed in `requirements.txt`; the timers are not carried over. |
| 10 | The README linked to and cited a repository named `Gauss-Markov-BTC-Analysis`, and named only Investing.com and FRED as sources while listing BLS for the CPI-U. | The README links to this repository and states the sources as version 1 names them. |

Version 1's notebook is kept unchanged in `legacy/`; `blueml/legacy.py` runs it on the stored data and the unit
tests check that it reproduces its printed results ($R^2$ 0.223, S&P 500 coefficient 16.1312, Durbin–Watson 1.6739,
Breusch–Pagan $p$ 0.0386, forest $R^2$ 0.87).

## Version 1.0.0

First version: OLS of the monthly change of Bitcoin on changes of gold, the S&P 500, the dollar index, the CPI-U and
the federal funds rate, with Gauss–Markov tests, White and Newey–West standard errors, a random forest with
partial dependence plots, correlations and Granger causality tests of Bitcoin and S&P 500 returns.
