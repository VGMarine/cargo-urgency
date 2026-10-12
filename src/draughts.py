"""Средняя осадка AMD (spec 003). Черновик: Dibble, стр. 18."""
from __future__ import annotations


def arithmetic_mean_draught(d_fwd: float, d_aft: float, d_mid: float) -> float:
    """AMD = (dF + dA + 6*dM) / 8 — весовая схема Simpson 1-6-1."""
    return (d_fwd + d_aft + 6.0 * d_mid) / 8.0


def mean_of_sides(d_port: float, d_stbd: float) -> float:
    return (d_port + d_stbd) / 2.0
