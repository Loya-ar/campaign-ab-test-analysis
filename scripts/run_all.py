"""Run the whole analysis in order: download, design, checks, results, CUPED, pitfalls, figures."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    "download_data.py",
    "design_power.py",
    "sanity_checks.py",
    "main_results.py",
    "cuped_analysis.py",
    "peeking_simulation.py",
    "segments.py",
    "make_figures.py",
]

for step in STEPS:
    start = time.time()
    print(f"==> {step}", flush=True)
    subprocess.run([sys.executable, str(HERE / step)], check=True, stdout=subprocess.DEVNULL)
    print(f"    done in {time.time() - start:.1f} s", flush=True)
print("All steps finished. Reports are in reports/, figures in figures/.")
