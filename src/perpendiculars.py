"""Поправки осадок на перпендикуляры (spec 002).

Черновик до сверки с оригиналом: Dibble, стр. 29–34.
Контрольное число из книги (стр. 33): tan(22°) * 4.121 = 1.665 м.
"""
from __future__ import annotations

import math


def mark_incline_correction(angle_deg: float, distance_m: float) -> float:
    """Линейная поправка осадки из-за наклона маркерной линии.

    corr = tan(alpha) * x   (альфа в градусах, x в метрах, результат в метрах)
    Знак здесь не трактуется — вызывающий код решает +/− по направлению
    наклона (см. spec 002, шаг 3; требует сверки со сканом).
    """
    return math.tan(math.radians(angle_deg)) * distance_m


def trim_to_midships(draft_fwd: float, draft_aft: float) -> float:
    """Поправка от конца к миделю при линейном изменении осадки по дифференту:
    половина дифферента. Ориентир книги (стр. 34): Trim aft to midships = 1.0 m.
    """
    return abs(draft_aft - draft_fwd) / 2.0
