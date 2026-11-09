import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

fig, ax = plt.subplots(figsize=(8.3, 8.3))
ax.set_title("SECTION A A through bolt B1 (x = 10), looking along +x", fontsize=11, loc="left")

def dim_h(x1, x2, y, text, off=1.0):
    ax.annotate("", xy=(x1, y), xytext=(x2, y), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text((x1 + x2) / 2, y + off, text, ha="center", va="bottom", fontsize=9)
    for x in (x1, x2):
        ax.plot([x, x], [y - 1.5, y + 1.5], lw=0.6, color="k")

def dim_v(y1, y2, x, text, side="right"):
    ax.annotate("", xy=(x, y1), xytext=(x, y2), arrowprops=dict(arrowstyle="<->", lw=0.9))
    ha = "left" if side == "right" else "right"
    dx = 1.5 if side == "right" else -1.5
    ax.text(x + dx, (y1 + y2) / 2, text, ha=ha, va="center", fontsize=9)

# base block, 60 wide, 10 thick, z from -10 to 0, hole through for the bolt (tapped, bolt bonded)
ax.add_patch(Rectangle((-30, -10), 60, 10, fc="#dddddd", ec="k", lw=1.4))
# bracket 40 wide, 6 thick, z 0 to 6, with the clearance hole dia 6.6 (drawn as a gap beside the shank)
ax.add_patch(Rectangle((-20, 0), 40, 6, fc="#bcd4f0", ec="k", lw=1.4))
ax.add_patch(Rectangle((-3.3, 0), 6.6, 6, fc="white", ec="k", lw=1.0))
# bolt: shank dia 6, length 16 below head (z 6 down to -10), head dia 10 x 6
ax.add_patch(Rectangle((-3, -10), 6, 16, fc="#999999", ec="k", lw=1.0))
ax.add_patch(Rectangle((-5, 6), 10, 6, fc="#777777", ec="k", lw=1.0))
# hex socket in the head
ax.add_patch(Rectangle((-2.5, 8), 5, 4, fc="white", ec="k", lw=0.8))
# thread engagement zone in the base (bolt bonded to the block)
ax.add_patch(Rectangle((-3, -10), 6, 10, fc="none", ec="#aa00aa", lw=1.2, hatch="xxx"))
# fixed support
for xs in range(-30, 31, 5):
    ax.plot([xs, xs - 4], [-10, -14], lw=0.8, color="k")
ax.plot([-30, 30], [-10, -10], lw=1.4, color="k")
ax.text(0, -17.5, "FIXED SUPPORT (bottom face of the base block)", ha="center", fontsize=9, color="r")
# symmetry axis
ax.plot([0, 0], [-13, 15], ls="-.", lw=0.9, color="g")
ax.text(-6, 13.2, "centre line y = 0", color="g", fontsize=8, ha="right")

# labels
ax.annotate("clearance gap (hole dia 6.6,\nbolt dia 6.0, radial clearance 0.3)", xy=(-3.1, 3), xytext=(-47, 9), fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.7))
ax.annotate("frictional contact\nbolt head / bracket", xy=(4.5, 6), xytext=(12, 15), fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.7))
ax.annotate("frictional contact\nbracket / base block", xy=(14, 0), xytext=(12, -6.5), fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.7), color="k")
ax.annotate("thread engagement 10 mm:\nbolt bonded to the base block hole", xy=(0, -6), xytext=(-54, -15), fontsize=8, color="#aa00aa",
            arrowprops=dict(arrowstyle="->", lw=0.7, color="#aa00aa"))
ax.text(-19, 2.2, "bracket", fontsize=8)
ax.text(-29, -5.5, "base block", fontsize=8)

# dimensions
dim_h(-20, 20, 21, "40 bracket width", 0.8)
dim_h(-30, 30, -23, "60 base block width", 0.8)
dim_h(-5, 5, 17.5, "head dia 10", 0.5)
dim_v(0, 6, -26, "t = 6", side="left")
dim_v(-10, 0, 34, "10 base", side="right")
dim_v(6, 12, 8, "head 6", side="right")

ax.set_xlim(-57, 50)
ax.set_ylim(-26, 26)
ax.set_aspect("equal")
ax.axis("off")
fig.text(0.02, 0.02, "Dimensions in mm. Bolt M6 x 16: 6 mm through the bracket plus 10 mm thread in the base block.", fontsize=8)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("bracket_section_view.png", dpi=170)
fig.savefig("bracket_section_view.pdf")
print("ok")
