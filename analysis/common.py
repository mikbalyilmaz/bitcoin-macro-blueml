"""Common set-up for the analysis scripts: import path and a CSV writer."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from blueml.style import FIG_DIR  # noqa: E402


def save_table(rows, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(FIG_DIR / f"{name}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows([{k: r.get(k, "") for k in keys} for r in rows])
    print(f"wrote figures/{name}.csv ({len(rows)} rows)")
