"""Runs the code of version 1 (legacy/gauss_markov_v1.ipynb) on the stored data, to reproduce its numbers.

The code cells are executed in order in one namespace with these changes only: the `!pip install` lines are removed,
the absolute path of the data file (/Users/myucanlar/Desktop/Gauss-Markov Project/dataset1.xlsx) is replaced by
data/dataset1.xlsx, figures are saved into a temporary folder instead of the author's desktop, `display` and
`plt.show` do nothing, and printed output is captured. The argument `verbose=False` of `grangercausalitytests`, which
newer statsmodels no longer accepts (it was already deprecated in version 1's run), is dropped; the test is unchanged.
Nothing else of version 1 is modified.

Author: Muhammed Ikbal Yilmaz
"""

import contextlib
import io
import json
import os
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "legacy" / "gauss_markov_v1.ipynb"
DATA = ROOT / "data" / "dataset1.xlsx"
V1_DIR = "/Users/myucanlar/Desktop/Gauss-Markov Project"


def code_cells(path=NOTEBOOK):
    nb = json.loads(Path(path).read_text(encoding="utf-8"))
    return [(i, "".join(c["source"])) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]


def run_v1():
    """Executes the code cells of version 1; returns (namespace, printed output)."""
    out = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        ns = {"display": lambda *a, **k: print(*a)}
        show = plt.show
        plt.show = lambda *a, **k: None
        try:
            with contextlib.redirect_stdout(out):
                for i, src in code_cells():
                    lines = [ln for ln in src.splitlines() if not ln.lstrip().startswith("!")]
                    src = "\n".join(lines).replace(f"{V1_DIR}/dataset1.xlsx", str(DATA)).replace(V1_DIR, tmp)
                    src = src.replace(", verbose=False)", ")")
                    exec(compile(src, f"<v1 cell {i}>", "exec"), ns)     # noqa: S102  (file of this repository)
                    plt.close("all")
        finally:
            plt.show = show
    return ns, out.getvalue()


if __name__ == "__main__":
    import warnings
    warnings.simplefilter("ignore")
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    ns, printed = run_v1()
    print(printed)
