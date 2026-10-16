"""Поправка водоизмещения на крен (spec 005a).

Сверено с оригиналом: Dibble, стр. 26 книги (PDF index 34):
Correction for list = 6 * (TPC2 - TPC1) * (d2 - d1) tonnes, sign always positive.
Контрольный пример QUESTION 4: 6*(34-32)*(8.00-6.00) = 24 tonnes (+).
"""
from __future__ import annotations


def list_correction_t(tpc1: float, tpc2: float, d1_m: float, d2_m: float) -> float:
    """Поправка на крен в тоннах; всегда положительная (по модулям разностей)."""
    return 6.0 * abs(tpc2 - tpc1) * abs(d2_m - d1_m)
