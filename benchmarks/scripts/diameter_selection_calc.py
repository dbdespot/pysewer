# SPDX-FileCopyrightText: 2023 Helmholtz Centre for Environmental Research (UFZ)
# SPDX-License-Identifier: GPL-3.0-only

"""Standalone worked computation behind pysewer's diameter selection.

Reproduces the two tables in docs/butler_conformity_assessment.md §6 from
first principles (Manning, exact wetted-angle geometry), so the "why are the
pipes this size" story is self-contained and checkable:

  1. proportional depth d/D  ->  flow ratio Q/Q_full  (geometry only)
  2. the Wasweta II trunk worked example: which DN a given design flow selects
     at each candidate fill target, and the resulting reserve

    python benchmarks/scripts/diameter_selection_calc.py

Pure standard library; no pysewer import needed (mirrors optimization.py's
_partial_flow_capacity / _proportional_depth so it can be read on its own).
"""

import math

N = 0.013  # Manning's n (concrete sewer)


def q_full(d, s):
    """Full-bore Manning discharge [m3/s] for diameter d [m], slope s [m/m]."""
    area = math.pi * (d / 2) ** 2
    rh = d / 4
    return area * (1 / N) * rh ** (2 / 3) * s**0.5


def q_at_depth(d, s, depth_ratio):
    """Discharge at proportional depth d/D via exact wetted-angle geometry."""
    r = d / 2
    theta = 2 * math.acos(1 - 2 * depth_ratio)
    area = r * r * (theta - math.sin(theta)) / 2
    rh = area / (r * theta)
    return area * (1 / N) * rh ** (2 / 3) * s**0.5


def depth_for_flow(d, s, q):
    """Invert: the proportional depth d/D that conveys q (bisection)."""
    if q >= q_full(d, s):
        return 1.0
    r = d / 2

    def qf(theta):
        area = r * r * (theta - math.sin(theta)) / 2
        rh = area / (r * theta)
        return area * (1 / N) * rh ** (2 / 3) * s**0.5

    lo, hi = 1e-6, 2 * math.pi
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if qf(mid) < q else (lo, mid)
    theta = (lo + hi) / 2
    return (r * (1 - math.cos(theta / 2))) / d


def table_depth_vs_flow():
    print("proportional depth d/D  ->  flow ratio Q/Q_full (geometry only)")
    print(f"  {'d/D':>6} {'Q/Q_full':>10}")
    for dd in (0.25, 0.5, 0.646, 0.70, 0.75, 1.0):
        ratio = q_at_depth(0.3, 0.01, dd) / q_full(0.3, 0.01)
        print(f"  {dd:>6.3f} {ratio:>10.3f}")
    print("  d/D 0.5 => exactly half of full bore; d/D 0.646 => Q/Q_full 0.75")
    print("  (v0.1.20's 'flow ratio <= 0.75' is identically d/D = 0.646).")


def worked_example(q=0.0298, s=0.01):
    print(f"\nWasweta II trunk: Q = {q * 1000:.1f} L/s, slope = {s * 100:.1f}%, "
          f"n = {N}")
    print(f"  {'DN':>4} {'Q_full':>8} {'d/D@Q':>7} "
          f"{'cap@0.75':>9} {'cap@0.70':>9} {'cap@0.646':>10}")
    for d in (0.2, 0.25, 0.3):
        print(f"  {d * 1000:>3.0f} {q_full(d, s) * 1000:>7.1f}L "
              f"{depth_for_flow(d, s, q):>7.3f} "
              f"{q_at_depth(d, s, 0.75) * 1000:>8.1f}L "
              f"{q_at_depth(d, s, 0.70) * 1000:>8.1f}L "
              f"{q_at_depth(d, s, 0.646) * 1000:>9.1f}L")
    print("  selection = smallest DN whose capacity at the target d/D >= Q")
    print("  (standard diameter list has no DN250, so 0.70 tips DN200 -> DN300)")
    for target in (0.75, 0.70):
        for d in (0.2, 0.3):  # standard commercial list, no DN250
            if q <= q_at_depth(d, s, target):
                print(f"    target d/D {target:.2f} -> DN{d * 1000:.0f} "
                      f"(actual d/D {depth_for_flow(d, s, q):.3f})")
                break


if __name__ == "__main__":
    table_depth_vs_flow()
    worked_example()
