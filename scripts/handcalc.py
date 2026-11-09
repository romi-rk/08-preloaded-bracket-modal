"""Hand calculation for the bolted aluminium bracket with a tip mass.

Run:  python3 handcalc.py
All inputs are at the top. Change them to match your CAD model exactly.
"""
import math

# Inputs (SI units)
E = 71e9          # Pa, aluminium alloy as in the Ansys model
rho = 2770.0      # kg/m3, as in the Ansys model
b = 0.040         # m, width
t = 0.006         # m, thickness (bending direction)
L = 0.100         # m, free length from clamp edge to the tip mass
m_tip = 0.500     # kg, point mass at the tip

I = b * t**3 / 12.0
m_beam = rho * b * t * L
k = 3.0 * E * I / L**3
m_eff = m_tip + 0.2357 * m_beam           # tip mass plus effective beam mass
f_rigid = math.sqrt(k / m_eff) / (2 * math.pi)

print("Cantilever with tip mass, perfectly rigid clamp")
print(f"  I           = {I*1e12:.0f} mm^4")
print(f"  stiffness k = {k/1000:.1f} N/mm")
print(f"  beam mass   = {m_beam*1000:.1f} g")
print(f"  f1 (rigid)  = {f_rigid:.1f} Hz   <- upper bound for the bolted joint")
print(f"  gate band   = {0.9*f_rigid:.1f} to {1.1*f_rigid:.1f} Hz (rigid clamp FE model)\n")

# A real bolted joint adds a rotational spring at the clamp.
# Tip compliance = beam bending + rotation of the joint times lever arm L.
print("With a rotational joint stiffness k_theta at the clamp:")
print("  k_theta [Nm/rad]   k_eff [N/mm]   f1 [Hz]   f1 / f_rigid")
for k_theta in (1e3, 3e3, 1e4, 3e4, 1e5, 1e6):
    compliance = 1.0 / k + L**2 / k_theta
    k_eff = 1.0 / compliance
    f = math.sqrt(k_eff / m_eff) / (2 * math.pi)
    print(f"  {k_theta:12.0f}   {k_eff/1000:12.1f}   {f:7.1f}   {f/f_rigid:8.2f}")

# Bolt preload guide (simple, check against the VDI 2230 table for your bolt)
As = 20.1e-6       # m2, M6 stress area
Rp = 640e6         # Pa, yield strength class 8.8
axial_limit = 0.9 * Rp * As
print(f"\nM6 8.8 axial limit at 90 percent yield: {axial_limit/1000:.1f} kN")
print("Usable assembly preload is lower because of thread torsion, about 7 to 8.5 kN.")
print("Use 1, 3, 6 and 8 kN per bolt as the study values, and confirm 8 kN in VDI 2230.")
