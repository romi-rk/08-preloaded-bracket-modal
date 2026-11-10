"""Plot the Abaqus shock results: permanent joint slip and peak tip acceleration against shock level."""
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("data/abaqus/abaqus_shock_results.csv")))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
styles = {3000: ("#1f77b4", "o", "3 kN per bolt"), 500: ("#d95f02", "s", "0.5 kN per bolt")}
for P, (c, mk, lab) in styles.items():
    sel = sorted([r for r in rows if float(r["preload_per_bolt_N"]) == P and float(r["mu"]) == 0.2],
                 key=lambda r: float(r["shock_g"]))
    g = np.array([float(r["shock_g"]) for r in sel])
    slip = np.array([abs(float(r["final_joint_U3_mm"])) for r in sel])
    acc = np.array([float(r["peak_tip_accel_g"]) for r in sel])
    ax1.loglog(g, slip, marker=mk, color=c, label=lab)
    ax2.loglog(g, acc, marker=mk, color=c, label=lab)
ax1.set_xlabel("shock level (g)")
ax1.set_ylabel("permanent joint slip (mm)")
ax1.set_title("Permanent slip at the joint centre")
ax1.axhline(0.003, color="grey", lw=0.8, ls=":")
ax1.text(60, 0.0035, "below about 0.003 mm: no slip", fontsize=8, color="grey")
ax1.legend(loc="lower right")
g_line = np.array([2.0, 400.0])
ax2.loglog(g_line, g_line, color="grey", lw=0.8, ls="--", label="equal to the input")
ax2.set_xlabel("shock level (g)")
ax2.set_ylabel("peak tip acceleration relative to the base (g)")
ax2.set_title("Peak tip acceleration against the input")
ax2.legend(loc="upper left")
for ax in (ax1, ax2):
    ax.grid(True, which="both", alpha=0.25)
fig.tight_layout()
fig.savefig("figures/fig_abaqus_shock.png", dpi=200)
