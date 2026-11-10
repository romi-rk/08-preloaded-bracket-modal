"""Plot the harmonic response of the R9 model at the bracket tip.

Input:  data/harmonic/R9_vertical_response.csv  (Y direction, drives f1)
        data/harmonic/R9_lateral_response.csv   (Z direction, drives f2)
        Exported from Ansys: 1 g base acceleration (9806.65 mm/s2) in Y and Z,
        2% constant modal damping, mode superposition, 0.5 to 500 Hz in 0.5 Hz steps.
Output: figures/fig_harmonic_response.png
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
G = 9806.65     # mm/s2, 1 g, the applied base acceleration
ZETA = 0.02

CASES = [("vertical, Y axis", "R9_vertical_response.csv", 78.31),
         ("lateral, Z axis", "R9_lateral_response.csv", 321.30)]


def load(name):
    rows = list(csv.DictReader(open(ROOT / "data/harmonic" / name, newline="")))
    f = np.array([float(r["freq_Hz"]) for r in rows])
    u = np.array([float(r["tip_disp_mm"]) for r in rows])
    acc = np.array([float(r["tip_acc_mm_s2"]) for r in rows])
    ph = np.deg2rad([float(r["tip_acc_phase_deg"]) for r in rows])
    # absolute tip acceleration over base acceleration = |1 + relative acceleration / base acceleration|
    T = np.abs(1.0 + acc * np.exp(1j * ph) / G)
    return f, u, T


fig, ax = plt.subplots(2, 2, figsize=(10, 7))
for col, (label, name, f_modal) in enumerate(CASES):
    f, u, T = load(name)
    hand = G / (2 * np.pi * f_modal) ** 2 / (2 * ZETA)
    ax[0, col].semilogy(f, u)
    ax[0, col].axvline(f_modal, color="grey", linestyle="--", label=f"modal f = {f_modal:.1f} Hz")
    ax[0, col].axhline(hand, color="lightgrey", linestyle=":", label=f"hand check {hand:.3f} mm")
    ax[0, col].set_title(f"Relative tip displacement, {label}")
    ax[0, col].set_ylabel("Displacement [mm]")
    ax[0, col].legend(fontsize=8, loc="upper right")
    ax[1, col].semilogy(f, T)
    ax[1, col].axhline(1.0, color="red", linestyle="--", label="transmissibility 1")
    ax[1, col].axvline(f_modal, color="grey", linestyle="--")
    ax[1, col].set_title(f"Absolute transmissibility, {label}")
    ax[1, col].set_ylabel("Tip acceleration / base acceleration [1]")
    ax[1, col].legend(fontsize=8, loc="upper right")
    for r in (0, 1):
        ax[r, col].set_xlabel("Frequency [Hz]")
        ax[r, col].grid(True, alpha=0.3, which="both")
    print(label, "peak displacement", round(u.max(), 4), "mm at", f[u.argmax()], "Hz;",
          "peak transmissibility", round(T.max(), 1))
fig.suptitle("Harmonic response of the R9 model, 1 g base acceleration, 2% damping (assumed)")
fig.tight_layout()
fig.savefig(ROOT / "figures" / "fig_harmonic_response.png", dpi=200)
print("saved fig_harmonic_response.png")
