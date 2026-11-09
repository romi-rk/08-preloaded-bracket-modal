import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.7, 8.3), gridspec_kw={"height_ratios": [1.15, 1]})
LW = 1.4

def dim_h(ax, x1, x2, y, text, off=0, fs=9):
    ax.annotate("", xy=(x1, y), xytext=(x2, y), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text((x1 + x2) / 2, y + off, text, ha="center", va="bottom", fontsize=fs)
    for x in (x1, x2):
        ax.plot([x, x], [y - 2, y + 2], lw=0.6, color="k")

def dim_v(ax, y1, y2, x, text, fs=9):
    ax.annotate("", xy=(x, y1), xytext=(x, y2), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(x + 2, (y1 + y2) / 2, text, ha="left", va="center", fontsize=fs)

# ---------------- TOP VIEW ----------------
ax = ax1
ax.set_title("TOP VIEW (looking down on the bracket)", fontsize=11, loc="left")
# base block outline (dashed, below the bracket)
ax.add_patch(Rectangle((-10, -30), 50, 60, fill=False, ls="--", lw=1.0, ec="grey"))
ax.text(-9, -34, "base block (hidden), x = -10 to 40", fontsize=8, color="grey")
# bracket
ax.add_patch(Rectangle((0, -20), 140, 40, fill=False, lw=LW))
# clamped region hatch
ax.add_patch(Rectangle((0, -20), 40, 40, fill=False, hatch="///", lw=0, ec="#888"))
ax.plot([40, 40], [-26, 26], ls="-.", lw=1.0, color="r")
ax.text(41, 22, "clamp edge x = 40", color="r", fontsize=9)
# bolt holes
for xb in (10, 30):
    ax.add_patch(Circle((xb, 0), 3.3, fill=False, lw=LW))
    ax.plot([xb - 6, xb + 6], [0, 0], lw=0.6, color="k")
    ax.plot([xb, xb], [-6, 6], lw=0.6, color="k")
ax.text(10, -9.5, "B1", ha="center", fontsize=9)
ax.text(30, -9.5, "B2", ha="center", fontsize=9)
ax.text(20, 10, "2 x M6 x 16", ha="center", fontsize=9)
# tip mass
ax.add_patch(Circle((140, 0), 4, fc="k"))
ax.annotate("0.5 kg point mass\n(remote point at end face centre)", xy=(140, 0), xytext=(100, 12),
            fontsize=9, ha="center", arrowprops=dict(arrowstyle="->", lw=0.8))
# axes
ax.plot([10, 10], [-27, 30], ls="-.", lw=0.9, color="g")
ax.text(10, 31.5, "A", ha="center", color="g", fontsize=10)
ax.text(10, -33.5, "A", ha="center", color="g", fontsize=10)
ax.text(14, -26, "section A A (view 3)", color="g", fontsize=8)
ax.annotate("", xy=(-20, -42), xytext=(-40, -42), arrowprops=dict(arrowstyle="->", lw=1.1))
ax.text(-19, -43, "x", fontsize=10)
ax.annotate("", xy=(-40, -22), xytext=(-40, -42), arrowprops=dict(arrowstyle="->", lw=1.1))
ax.text(-42, -21, "y", fontsize=10, ha="right")
# dimensions
dim_h(ax, 0, 140, -37, "140 total length", 1)
dim_h(ax, 40, 140, -47, "100 free length L (to the tip mass)", 1)
dim_h(ax, 0, 10, 27, "10", 1)
dim_h(ax, 10, 30, 27, "20", 1)
dim_h(ax, 30, 40, 27, "10", 1)
ax.text(60, 5, "holes dia 6.6 (study: 6.0, 6.2, 6.6)", fontsize=9)
dim_v(ax, -20, 20, 148, "40 width")
ax.set_xlim(-50, 185)
ax.set_ylim(-58, 45)
ax.set_aspect("equal")
ax.axis("off")

# ---------------- SIDE VIEW ----------------
ax = ax2
ax.set_title("SIDE VIEW (section along the centre line, z is the bending and excitation direction)", fontsize=11, loc="left")
# base block, thickness 10, top at z=0
ax.add_patch(Rectangle((-10, -10), 50, 10, fc="#dddddd", ec="k", lw=LW))
ax.text(-8, -5.8, "base 10", ha="left", fontsize=7, color="#555")
# fixed support symbol
for xs in range(-10, 41, 5):
    ax.plot([xs, xs - 4], [-10, -14], lw=0.8, color="k")
ax.plot([-10, 40], [-10, -10], lw=1.4, color="k")
ax.text(-10, -17, "FIXED SUPPORT (bottom face)", ha="left", fontsize=9, color="r")
# bracket thickness 6 from z=0 to 6
ax.add_patch(Rectangle((0, 0), 140, 6, fc="#bcd4f0", ec="k", lw=LW))
# bolts: shank through bracket and into base (M6 x 16)
for xb in (10, 30):
    ax.add_patch(Rectangle((xb - 3, -10), 6, 16, fc="#999999", ec="k", lw=1.0))
    ax.add_patch(Rectangle((xb - 5, 6), 10, 6, fc="#777777", ec="k", lw=1.0))
    ax.text(xb, 13.5, "B1" if xb == 10 else "B2", ha="center", fontsize=8)
ax.text(20, 24, "M6 x 16 socket head bolts", ha="center", fontsize=9)
ax.text(20, 20.5, "preload 1 to 8 kN each", ha="center", fontsize=8, color="b")
# contact markers
ax.annotate("frictional contact\nbracket / base", xy=(25, 0), xytext=(52, -14), fontsize=8, ha="left",
            arrowprops=dict(arrowstyle="->", lw=0.7))
ax.annotate("frictional contact\nbolt head / bracket", xy=(15, 9), xytext=(52, 16), fontsize=8, ha="left",
            arrowprops=dict(arrowstyle="->", lw=0.7))
# tip mass
ax.add_patch(Circle((140, 3), 4, fc="k"))
ax.text(140, 12, "0.5 kg", ha="center", fontsize=9)
# clamp edge
ax.plot([40, 40], [-28, 24], ls="-.", lw=1.0, color="r")
# excitation arrow
ax.annotate("", xy=(100, 28), xytext=(100, 8), arrowprops=dict(arrowstyle="<->", lw=1.3, color="b"))
ax.text(103, 20, "z : first bending mode and\nbase excitation direction", fontsize=9, color="b", va="center")
# dimensions
dim_h(ax, 40, 140, -27, "L = 100", 1)
dim_h(ax, 0, 40, -27, "40 clamped", 1)
dim_v(ax, 0, 6, 145, "t = 6")
ax.set_xlim(-50, 185)
ax.set_ylim(-31, 40)
ax.set_aspect("equal")
ax.axis("off")

fig.text(0.02, 0.01,
    "Bracket: aluminium 6061, E = 69 GPa, density 2700 kg/m3.  Dimensions in mm.  Origin x = 0 at the clamped end of the bracket, y on the centre line.",
    fontsize=8, ha="left")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("bracket_drawing.png", dpi=170)
fig.savefig("bracket_drawing.pdf")
print("ok")
