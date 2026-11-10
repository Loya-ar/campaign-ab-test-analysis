"""Figures for the README: treatment effects with CIs, and the peeking simulation.

Writes figures/lifts.png and figures/peeking.png. Uses the same functions and seeds as the
report scripts, so the numbers match reports/04_main_results.md and reports/06a_peeking.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from abtest.inference import two_proportion_test, welch_test  # noqa: E402
from abtest.sequential import aa_peeking_false_positive_rate, obrien_fleming_boundaries  # noqa: E402

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"  # validated categorical slots 1 and 2
EMAILS = [("Men's email", "Mens E-Mail", BLUE), ("Women's email", "Womens E-Mail", ORANGE)]
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
})
out_dir = ROOT / "figures"
out_dir.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / "data" / "raw" / "hillstrom.csv")
ctrl = df[df.segment == "No E-Mail"]

# --- Figure 1: absolute lift vs no email, 95% CI, one panel per metric ---------------
panels = [("Conversion", "conversion", "pp"), ("Visit", "visit", "pp"), ("Spend per customer", "spend", "$")]
fig, axes = plt.subplots(1, 3, figsize=(10, 2.8))
for ax, (title, col, unit) in zip(axes, panels):
    for i, (label, seg, color) in enumerate(EMAILS):
        t = df[df.segment == seg]
        if unit == "pp":
            r = two_proportion_test(int(t[col].sum()), len(t), int(ctrl[col].sum()), len(ctrl))
            d, lo, hi = r.diff * 100, r.ci_diff[0] * 100, r.ci_diff[1] * 100
            txt = f"{d:+.2f} pp"
        else:
            r = welch_test(t[col], ctrl[col])
            d, (lo, hi) = r.diff, r.ci_diff
            txt = f"+${d:.2f}"
        y = 1 - i
        ax.plot([lo, hi], [y, y], color=color, lw=2, solid_capstyle="round")
        ax.plot(d, y, "o", ms=8, color=color, mec=SURFACE, mew=2)
        ax.annotate(txt, (hi, y), xytext=(6, 0), textcoords="offset points", va="center", color=INK, fontsize=9)
    ax.axvline(0, color=INK2, lw=1)
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    ax.set_yticks([1, 0], [e[0] for e in EMAILS] if ax is axes[0] else ["", ""])
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, 1.6)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    lo_lim, hi_lim = ax.get_xlim()
    ax.set_xlim(min(lo_lim, -0.05 * hi_lim), hi_lim * 1.35)
    ax.set_xlabel("percentage points" if unit == "pp" else "dollars per customer")
fig.suptitle("Lift vs no email, with 95% confidence intervals", x=0.01, ha="left", fontsize=11)
fig.tight_layout()
fig.savefig(out_dir / "lifts.png", dpi=160)
plt.close(fig)

# --- Figure 2: peeking ------------------------------------------------------------
looks = [1, 2, 5, 10, 20, 50, 100]
y = ctrl.conversion.to_numpy()
naive = [aa_peeking_false_positive_rate(y, k, 2_000, seed=42) for k in looks]
obf = [aa_peeking_false_positive_rate(y, k, 2_000, seed=42, boundaries=obrien_fleming_boundaries(k, seed=42))
       for k in looks]
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.plot([0.8, 100], [5, 5], color=INK2, lw=1, ls=(0, (4, 3)))  # stops before the end labels
ax.annotate("promised 5%", (1, 5), xytext=(0, -12), textcoords="offset points", color=INK2, fontsize=9)
for vals, color, name in [(naive, ORANGE, "Check every time, stop at p < 0.05"),
                          (obf, BLUE, "O'Brien-Fleming boundaries")]:
    pct = [v * 100 for v in vals]
    ax.plot(looks, pct, color=color, lw=2, marker="o", ms=8, mec=SURFACE, mew=2, label=name)
    ax.annotate(f"{pct[-1]:.1f}%", (looks[-1], pct[-1]), xytext=(8, 0), textcoords="offset points",
                va="center", color=INK, fontsize=9)
ax.set_xscale("log")
ax.set_xticks(looks, [str(k) for k in looks])
ax.minorticks_off()
ax.set_xlim(0.8, 160)
ax.set_ylim(0, 40)
ax.set_xlabel("Number of looks at the data during the test")
ax.set_ylabel("False-positive rate (%)")
ax.grid(axis="y", color=GRID, lw=0.8)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.set_title("A/A tests on real no-email customers (conversion, 2,000 simulations each)",
             loc="left", fontsize=10)
fig.tight_layout()
fig.savefig(out_dir / "peeking.png", dpi=160)
plt.close(fig)
print("naive:", [f"{v:.1%}" for v in naive])
print("obf:  ", [f"{v:.1%}" for v in obf])
print("wrote", out_dir / "lifts.png", "and", out_dir / "peeking.png")
