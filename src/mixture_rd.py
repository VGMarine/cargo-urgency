"""RD смеси bunkers (Dibble, стр. 42 книги, раздел MIXTURES, дампы page_050/051).

Формула книги:
  RD mixture = (V_orig × RD_orig + V_loaded × RD_loaded) / (V_orig + V_loaded)
Контрольный пример (стр. 42): 100 м³ @ 0.960 + 50 м³ @ 0.990 → 0.970.
"""
from __future__ import annotations


def mixture_rd(v1_m3: float, rd1: float, v2_m3: float, rd2: float) -> float:
    total = v1_m3 + v2_m3
    if total <= 0:
        raise ValueError("объёмы должны быть положительными")
    return (v1_m3 * rd1 + v2_m3 * rd2) / total
