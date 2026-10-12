"""Поправки осадок на перпендикуляры и мидель (spec 002).

СВЕРЕНО с оригиналом (текстовый слой PDF): Dibble, стр. 29–34 книги
(PDF index 32–37). Контрольные примеры: QUESTION 3 (стр. 32–33) и
EXAMPLE «CORRECTIONS WITH HULL DEFLECTION» (стр. 33–34).
"""
from __future__ import annotations

import math


def mark_incline_correction(angle_deg: float, distance_m: float) -> float:
    """Линейная поправка осадки из-за наклона маркерной линии.

    corr = tan(alpha) * x   (альфа в градусах, x в метрах, результат в метрах)
    Сверено: книга, стр. 33 (PDF index 36): "By simple trigonometry
    Tan 22° x 4.121 = 1.665 m" — расстояние от FP до носовой марки при
    завале форштевня (rake of stern 22°, SLL-draught 10.471 м).
    Знак здесь не трактуется — вызывающий код решает +/− по правилу
    misplacement (см. perpendicular_corrections).
    """
    return math.tan(math.radians(angle_deg)) * distance_m


def trim_of(d_fwd: float, d_aft: float) -> float:
    """Apparent trim = Da - Df (книга, стр. 32: 7.88 - 6.35 = 1.53 м).

    Соглашение знака: положительный = дифферент на корму (trim by the stern),
    как в примерах книги (Q3, EXAMPLE).
    """
    return d_aft - d_fwd


def perpendicular_corrections(d_fwd: float, d_aft: float, lbp_m: float,
                              dist_fp_to_df_m: float, dist_ap_to_da_m: float):
    """Поправки «misplacement of marks» к перпендикулярам (книга, стр. 32).

    Формулы книги (буквы рис. стр. 29: Df/Da — осадки у марок, D FP/D AP —
    у перпендикуляров; apparent trim = Da - Df):

        Correction forward = apparent_trim x distance(D FP to Df) / distance(Da to Df)
        Midships correction = apparent_trim x distance(D M to Dm) / distance(Da to Df)
        Correction aft      = apparent_trim x distance(D AP to Da) / distance(Da to Df)

    Возвращает кортеж (corr_fwd, corr_aft) В МЕТРАХ, уже со знаками примера
    Q3 (trim on stern): смещение марки назад от FP (D FP to Df > 0) даёт
    отрицательную поправку носовой осадки; смещение марки вперёд от AP
    (D AP to Da > 0) — положительную поправку кормовой.
    Знак общего правила (стр. 32): «если направление смещения марки СОВПАДАЕТ
    с направлением дифферента — поправка отрицательная».
    Расстояния передаются неотрицательными величинами (как в книге); для
    случая trim by the head знаки меняются местами (проверяется тестом).
    """
    at = trim_of(d_fwd, d_aft)
    denom = lbp_m - dist_ap_to_da_m - dist_fp_to_df_m  # distance Da to Df
    if denom <= 0:
        raise ValueError("distance Da to Df должен быть > 0")
    corr_fwd = -at * dist_fp_to_df_m / denom
    corr_aft = +at * dist_ap_to_da_m / denom
    return corr_fwd, corr_aft


def deflection_end_correction(trim_half_m: float, misplacement_m: float,
                              half_length_m: float) -> float:
    """Поправка конца при hog/sag — метод книги (стр. 33–34, EXAMPLE).

    «use the trim between the midships mark and the particular end draught,
    then calculate using this half length trim, the half length and the
    distance of misplacement»:

        corr = misplacement x trim(half) / (half_length - misplacement)

    Проверено печатным ответом книги (hogged vessel, trim by stern):
      forward: 2 x 0.4/(50-2) = 0.017 -> Df = 6.00 - 0.017 = 5.983 м
      aft:     5 x 1.0/(50-5) = 0.111 -> Da = 7.40 + 0.111 = 7.511 м
    """
    denom = half_length_m - misplacement_m
    if denom <= 0:
        raise ValueError("half_length должна превышать misplacement")
    return misplacement_m * trim_half_m / denom


def trim_to_midships(draft_fwd: float, draft_aft: float) -> float:
    """Поправка от конца к миделю при линейном изменении осадки по дифференту:
    половина дифферента. Ориентир книги (стр. 34): Trim aft to midships = 1.0 m
    при fwd 6.00 / mid 6.40 / aft 7.40 (носовая половина 0.40 м — отдельный
    трим, см. EXAMPLE стр. 33).
    """
    return abs(draft_aft - draft_fwd) / 2.0
