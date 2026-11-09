"""Make all figures of the preloaded bracket study from data/results.csv.

Run from anywhere:  python3 scripts/plot_results.py
Outputs go to figures/.

Columns of results.csv:
  case, preload_kN, mu, f1_Hz, f2_Hz, f3_Hz, max_pressure_MPa,
  hole_mm, nodes, bolt_length_mm, shank_contact, mesh
Rows with an empty f1 are skipped.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

F_HAND = 86.8        # Hz, hand calculation, rigid clamp (scripts/handcalc.py)
F1_BONDED = 83.71    # Hz, FE bonded joint, 3 mm mesh
F2_BONDED = 471.27   # Hz, FE bonded joint, 3 mm mesh
YIELD_AL = 280.0     # MPa, compressive yield of the aluminium alloy
A_RING = 48.0        # mm2, estimated contact ring under the bolt head

rows = []
with open(ROOT / "data" / "results.csv", newline="") as fh:
    for r in csv.DictReader(fh):
        if not r["f1_Hz"]:
            continue
        rows.append({
            "case": r["case"],
            "p": float(r["preload_kN"]),
            "mu": float(r["mu"]),
            "f1": float(r["f1_Hz"]),
            "f2": float(r["f2_Hz"]) if r["f2_Hz"] else None,
            "pmax": float(r["max_pressure_MPa"]) if r["max_pressure_MPa"] else None,
            "hole": float(r["hole_mm"] or 6.0),
            "nodes": int(r["nodes"] or 0),
            "shank": r["shank_contact"] or "active",
            "mesh": r["mesh"] or "hex",
        })

# The main study: 6.0 mm hole, shank contact active, hex plates
main = [r for r in rows if r["hole"] == 6.0 and r["shank"] == "active" and r["mesh"] == "hex"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)
    print("saved", name)


def vs_preload(key, bonded, label, name, ylabel, title, extra=None):
    pts = sorted((r["p"], r[key]) for r in main if r["mu"] == 0.2 and r[key] is not None)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([p for p, _ in pts], [f for _, f in pts], marker="o", label="frictional, mu = 0.2")
    ax.axhline(bonded, color="grey", linestyle="--", label=label)
    if extra is not None:
        ax.axhline(extra, color="lightgrey", linestyle=":", label="hand calculation, rigid clamp")
    ax.set_xlabel("Bolt preload per bolt [kN]")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, name)


vs_preload("f1", F1_BONDED, "FE bonded joint", "fig_f1_vs_preload.png",
           "First bending frequency [Hz]", "Vertical bending f1 versus preload", extra=F_HAND)
vs_preload("f2", F2_BONDED, "FE bonded joint", "fig_f2_vs_preload.png",
           "Lateral bending frequency [Hz]", "Lateral bending f2 versus preload")


def bars(entries, labels, title, name, figsize=(8, 4), xlabel=None, rot=0):
    fig, axs = plt.subplots(1, 2, figsize=figsize)
    for ax, idx, ylab, bonded in ((axs[0], 0, "f1 vertical bending [Hz]", F1_BONDED),
                                  (axs[1], 1, "f2 lateral bending [Hz]", F2_BONDED)):
        vals = [e[idx] for e in entries]
        rects = ax.bar(range(len(vals)), vals)
        for rc, v in zip(rects, vals):
            ax.text(rc.get_x() + rc.get_width() / 2, v, f"{v:.1f}", ha="center", va="bottom", fontsize=8)
        ax.axhline(bonded, color="grey", linestyle="--", label="FE bonded joint")
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(labels, rotation=rot, fontsize=7 if rot or len(labels) > 3 else 9)
        ax.set_ylim(0, bonded * 1.12)
        ax.set_ylabel(ylab)
        if xlabel:
            ax.set_xlabel(xlabel)
        ax.legend(loc="lower right", fontsize=8)
    fig.suptitle(title)
    save(fig, name)


# Friction effect at 3 kN on the main model, axes start at zero
fr = sorted((r["mu"], r["f1"], r["f2"]) for r in main if r["p"] == 3.0 and r["f2"] is not None)
bars([(f1, f2) for _, f1, f2 in fr], [str(m) for m, _, _ in fr],
     "Effect of friction at 3 kN preload", "fig_friction_effect.png", xlabel="Friction coefficient mu")

# Hole size, shank contact and mesh type at 3 kN, mu 0.2
order = ["R2", "R9", "R10", "R7", "R8"]
sel = [next(r for r in rows if r["case"] == c) for c in order if any(r["case"] == c for r in rows)]
labels = [f'{r["case"]}\n{r["hole"]:.1f} mm hole\n{r["mesh"]} plates\nshank {r["shank"]}\n{r["nodes"] // 1000}k nodes'
          for r in sel]
bars([(r["f1"], r["f2"]) for r in sel], labels,
     "Hole size, shank contact and mesh type at 3 kN, mu 0.2", "fig_mesh_and_clearance.png",
     figsize=(11, 4.8))

# Contact pressure: mesh dependent peak versus mean pressure under the head
pts = sorted((r["p"], r["pmax"]) for r in main if r["mu"] == 0.2 and r["pmax"] is not None)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ps = [p for p, _ in pts]
ax.plot(ps, [v for _, v in pts], marker="o", label="peak pressure (mesh dependent)")
ax.plot(ps, [p * 1000.0 / A_RING for p in ps], marker="s", label=f"mean pressure, F / {A_RING:.0f} mm2")
ax.axhline(YIELD_AL, color="red", linestyle="--", label="compressive yield, 280 MPa")
ax.set_xlabel("Bolt preload per bolt [kN]")
ax.set_ylabel("Contact pressure under the head [MPa]")
ax.set_title("Peak and mean contact pressure versus preload")
ax.set_ylim(0, 300)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8, loc="lower right")
save(fig, "fig_pressure_vs_preload.png")
