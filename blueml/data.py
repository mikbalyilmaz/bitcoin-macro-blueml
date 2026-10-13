"""Data: the monthly dataset of version 1 and the two transformations used for the regressions.

File (data/): dataset1.xlsx, the file of version 1, unchanged: 127 months, January 2015 to July 2025, columns
CPI-U (index, 1982-84 = 100, not seasonally adjusted), DXY (US dollar index), BTC/USD, SPX (S&P 500), FEDFUNDS
(effective federal funds rate, %), XAU/USD (gold, US dollars per troy ounce). Sources stated by version 1:
Investing.com (BTC, gold, S&P 500, DXY) and FRED (FEDFUNDS); for CPI-U the notebook names FRED, the README BLS.
Which daily value stands for a month (for example the last close) was not recorded.

Author: Muhammed Ikbal Yilmaz
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
COLUMNS = ["BTC/USD", "XAU/USD", "SPX", "DXY", "CPI-U", "FEDFUNDS"]
REGRESSORS = ["gold", "spx", "dxy", "inflation", "fedfunds"]
LABELS = {"btc": "Bitcoin", "gold": "Gold", "spx": "S&P 500", "dxy": "Dollar index", "inflation": "Inflation",
          "fedfunds": "Fed funds rate"}


def load(path=None):
    """The dataset of version 1 with a monthly index. Its first date is stored as 2015-01-01 04:50:10 (a typing
    slip); every date is set to the first day of its month."""
    d = pd.read_excel(path or DATA / "dataset1.xlsx")
    d["date"] = pd.to_datetime(d["date"]).dt.to_period("M").dt.to_timestamp()
    d = d.set_index("date")[COLUMNS]
    if d.index.duplicated().any() or d.isna().any().any():
        raise ValueError("duplicate months or missing values in dataset1.xlsx")
    return d.asfreq("MS")


def v1_differences(d):
    """Version 1's variables: first differences of the levels (Bitcoin in US dollars, CPI in index points, the
    rate in percentage points)."""
    out = d.diff().dropna()
    return out.rename(columns={"BTC/USD": "btc", "XAU/USD": "gold", "SPX": "spx", "DXY": "dxy",
                               "CPI-U": "inflation", "FEDFUNDS": "fedfunds"})


def v2_returns(d):
    """Version 2's variables: monthly log returns in per cent, 100 (ln P_t - ln P_{t-1}), for Bitcoin, gold, the
    S&P 500 and the dollar index; monthly inflation 100 (ln CPI_t - ln CPI_{t-1}); the change of the federal funds
    rate in percentage points."""
    lg = 100 * np.log(d[["BTC/USD", "XAU/USD", "SPX", "DXY", "CPI-U"]]).diff()
    out = pd.DataFrame({"btc": lg["BTC/USD"], "gold": lg["XAU/USD"], "spx": lg["SPX"], "dxy": lg["DXY"],
                        "inflation": lg["CPI-U"], "fedfunds": d["FEDFUNDS"].diff()})
    return out.dropna()
