"""Поправки замеров (soundings) на дифферент и объём клина (spec 006).

Сверено с оригиналом (текстовый слой PDF): Dibble, стр. 40-42 книги
(PDF index 48-50). Контрольные примеры: QUESTION 10 (стр. 40), QUESTION 11 (стр. 42).
"""
from __future__ import annotations


def sounding_correction_m(d_m: float, trim_m: float, lbp_m: float) -> float:
    """Correction to sounding x = d * trim / LBP (книга, стр. 40).

    d_m — расстояние от трубки замера до центра танка (знак задаёт вызывающий):
    таблица знаков книги: trim Aft & sounding forward of centre -> negative;
    trim Aft & sounding aft of centre -> positive. Т.е. знак = sign(d_от_центра к носу?)
    Здесь возвращаем ВЕЛИЧИНУ со знаком для переданного d_m со знаком
    (+ = трубка впереди центра танка) при дифференте на корму (trim_m > 0):
    по книге такой случай даёт отрицательную поправку.
    """
    return -(d_m * trim_m) / lbp_m


def even_keel_sounding_m(observed_m: float, correction_m: float) -> float:
    """Even keel sounding = observed + correction (книга, пример Q10: 1.05 - 0.15 = 0.90)."""
    return observed_m + correction_m


def rectangular_tank_volume_m3(length_m: float, breadth_m: float, depth_m: float) -> float:
    """Объём прямоугольного танка = L * B * глубина жидкости (Q10: 24*8.2*0.90=177.12)."""
    return length_m * breadth_m * depth_m


def corrected_sounding_for_wedge_m(observed_m: float, y_to_end_bulkhead_m: float,
                                   trim_m: float, lbp_m: float) -> float:
    """Corrected sounding (P) = observed + y * trim / LBP (книга, стр. 42, перед Q11).

    y — расстояние от позиции замера до end bulkhead (кормовой, при trim by stern).
    Пример Q11 (стр. 42): решение книги подставляет y = 6 м, хотя в условии
    напечатано 5.0 м; дамп текстового слоя (page_050.txt) подтверждает: только
    y=6 воспроизводит печатный ответ 0.28. Приоритет — числам решения книги.
    """
    return observed_m + y_to_end_bulkhead_m * trim_m / lbp_m


def wedge_volume_m3(lbp_m: float, breadth_m: float, corrected_sounding_m: float,
                    trim_m: float) -> float:
    """Wedge volume = LBP * breadth * P^2 / (2 * trim) (книга, стр. 41).

    Ограничение применимости (книга): прямоугольный танк, свободная поверхность,
    дно покрыто жидкостью; малые количества (slop).
    """
    if trim_m <= 0:
        raise ValueError("wedge требует ненулевой дифферент (trim > 0)")
    return lbp_m * breadth_m * corrected_sounding_m ** 2 / (2.0 * trim_m)
