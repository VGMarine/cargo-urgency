"""Поправки на дифферент: 1st trim (layer) и 2nd trim (spec 004).

Сверено с оригиналом (текстовый слой PDF): Dibble, стр. 31-33 книги
(индексы страниц PDF 38-39). Контрольные примеры: QUESTION 7 (стр. 32),
QUESTION 8 (стр. 33).
"""
from __future__ import annotations


def layer_correction_m(lcf_to_midships_m: float, trim_m: float, lbp_m: float) -> float:
    """Layer correction (м) = (расстояние LCF до мидля) * trim / LBP.

    Знак по книге (стр. 31): LCF forward of midships -> отрицательный при
    дифференте на корму; здесь возвращаем величину со знаком для случая
    "trim by the stern": знак минус если LCF впереди мидля (+5 м fwd => -).
    Соглашение: передавайте lcf_to_midships_m со знаком (+ = LCF forward of midships),
    trim_m — со знаком (+ = by the stern); тогда TMD = AMD + corr.
    """
    # книга: Layer correction = distance LCF to midships x trim / LBP,
    # sign: trim Aft & LCF fwd of midships => negative (-)
    return -(lcf_to_midships_m * trim_m) / lbp_m


def first_trim_correction_t(layer_m: float, tpc: float) -> float:
    """1st trim correction (тонны) = layer correction (м) * TPC * 100."""
    return layer_m * tpc * 100.0


def second_trim_correction_t(trim_m: float, mctc2: float, mctc1: float,
                             lbp_m: float) -> float:
    """2nd trim correction (тонны) = 50 * trim^2 * (MCTC2 - MCTC1) / LBP.

    MCTC1 = MCTC на mean adjusted draught; MCTC2 = MCTC на MAD + 50 см.
    Знак: всегда положительный (книга, стр. 32).
    """
    return 50.0 * trim_m ** 2 * (mctc2 - mctc1) / lbp_m


def first_trim_correction_t_sign(lcf_to_midships_m: float, trim_m: float,
                                 lbp_m: float, tpc: float) -> float:
    """Метрическая форма книги (стр. 31, PDF index 39) — без шага в метрах:

    1st trim correction (tonnes) = dist(LCF to midships) x TPC x trim(cm) / LBP

    Знак по таблице книги (стр. 31):
        trim Aft:     LCF forward of midships -> negative (-)
                      LCF aft of midships     -> positive (+)
        trim Forward: LCF forward of midships -> positive (+)
                      LCF aft of midships     -> negative (-)
    Т.е. результат знаку произведения (lcf_signed * trim_signed) противоположен.
    Соглашение: lcf_to_midships_m со знаком (+ = fwd of midships),
    trim_m (+ = by the stern).
    Контроль Q7: -(5 x 40 x 40 / 150) = -53.33 t; величина совпадает с
    печатным решением книги «5 x 40 x 0.40 x 100 / 150» (напечатанный знак
    ответа — OCR-обломок, таблица знаков даёт минус: LCF fwd & trim aft;
    TODO(scan) стр. 32/PDF index 40).
    """
    return -(lcf_to_midships_m * tpc * trim_m * 100.0) / lbp_m
