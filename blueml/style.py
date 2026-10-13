"""Shared figure style.

Typeface: Latin Modern Roman, the typeface of LaTeX documents, registered from ../fonts. The layout follows the
plain chart style common in macro research notes: no grid, heavy lines, the data series in black and deep blue,
red dotted vertical lines for dates that matter, labels written at the end of the lines instead of a legend where
possible, and the source written inside the chart.

Every figure is saved as PDF (used by the project note) and as PNG (used by the README).

Author: Muhammed Ikbal Yilmaz
"""

import logging
import sys
from pathlib import Path

import matplotlib

if "ipykernel" not in sys.modules:   # scripts and tests draw to files; inside Jupyter the notebook's backend is kept
    matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager, ticker  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
FONT_DIR = ROOT / "fonts"

INK, MUTED, BAND = "#000000", "#7a7a7a", "#c9d4ec"
BLUE, RED = "#0033a0", "#d7191c"          # BLUE is a deep blue; RED marks dates


def num(value, fmt="{:g}"):
    """Format a number for a tick label, with a typographic minus sign."""
    return fmt.format(value).replace("-", "−")


def use_style():
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    for path in FONT_DIR.glob("*.otf"):
        font_manager.fontManager.addfont(str(path))
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8, "axes.titlelocation": "left",
        "axes.titleweight": "bold",
        "axes.edgecolor": INK, "axes.linewidth": 0.7, "axes.labelcolor": INK, "text.color": INK,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
        "xtick.color": INK, "ytick.color": INK, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "xtick.major.width": 0.7, "ytick.major.width": 0.7, "xtick.major.size": 3, "ytick.major.size": 3, "xtick.direction": "out", "ytick.direction": "out",
        "lines.linewidth": 1.4, "lines.solid_capstyle": "butt",
        "legend.frameon": False, "legend.fontsize": 7.5, "legend.handlelength": 1.8,
        "figure.dpi": 110, "savefig.dpi": 300, "savefig.bbox": "tight", "pdf.fonttype": 3,
    })


def decimal_axis(ax, axis="y", fmt="{:g}"):
    """Tick labels with a typographic minus sign."""
    target = ax.yaxis if axis == "y" else ax.xaxis
    target.set_major_formatter(ticker.FuncFormatter(lambda v, _: num(round(v, 10), fmt)))


def event_line(ax, x, label, y=0.98, ha="left"):
    """Red dotted vertical line with a bold red label at the top of the panel."""
    ax.axvline(x, color=RED, ls=(0, (1, 1.4)), lw=1.4, zorder=1)
    ax.annotate(label, xy=(x, y), xycoords=("data", "axes fraction"), xytext=(3 if ha == "left" else -3, 0),
                textcoords="offset points", ha=ha, va="top", color=RED, fontweight="bold", fontsize=7.5)


def end_label(ax, x, y, text, color, dx=4, dy=0, va="center"):
    """Label written at the end of a line, in the colour of the line."""
    ax.annotate(text, xy=(x, y), xytext=(dx, dy), textcoords="offset points", color=color, fontweight="bold",
                fontsize=7.5, va=va, ha="left")


def source_note(ax, text, x=0.01, y=0.02, ha="left", va="bottom"):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=6.6, ha=ha, va=va, color=INK)


def panel_name(ax, text, x=0.97, y=0.06):
    """Large bold name inside a small-multiple panel."""
    ax.text(x, y, text, transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, fontweight="bold")


def save_figure(name, draw, heading=None):
    """`draw()` returns a figure; `heading()` returns its title, which is shown in the PNG only (in the note the
    caption carries the title)."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig = draw()
    fig.savefig(FIG_DIR / f"{name}.pdf")
    if heading is not None:
        fig.suptitle(heading(), x=0.01, ha="left", fontsize=9.5, fontweight="bold")
    fig.savefig(FIG_DIR / f"{name}.png")
    plt.close(fig)
