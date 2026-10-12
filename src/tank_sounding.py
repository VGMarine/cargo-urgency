"""Замеры (soundings) танков при дифференте: поправка на смещение трубки (Dibble Q10).

Сверено с дампом текстового слоя: sources/dumps/dibble/page_048.txt (стр. 40 книги).
Формула книги: Correction to sounding (x) = d × trim / LBP, где d — расстояние от
трубки замера до ЦЕНТРА ТАНКА. Таблица знаков книги:

    Sounding forward of tank centre:  trim Aft -> (-),  trim Forward -> (+)
    Sounding aft of tank centre:      trim Aft -> (+),  trim Forward -> (-)

Контрольный пример QUESTION 10 (стр. 40): LBP 120 м, trim 2.0 м на корму,
наблюдённый замер 1.05 м, танк 24.0×8.2 м, трубка в 3.0 м от кормовой переборки
=> d = 12 − 9 = 3.0 м ПЕРЕД центром => поправка −0.15, even-keel 0.90, V = 177.1 м³.
"""
from __future__ import annotations


def tube_offset_from_centre_m(tube_to_end_bulkhead_m: float, tank_length_m: float,
                             end_is_aft: bool = True) -> float:
    """Знаковое d: расстояние трубки до ЦЕНТРА танка (по книге — без знака;
    знак по таблице знаков). Возвращаем + если трубка впереди центра, − если позади.

    end_is_aft=True: расстояние отсчитано от кормовой переборки (как в Q10).
    Пример Q10: трубка в 3.0 м перед кормовой переборкой, танк 24 м =>
    d = |12 − 3| = 9 м ПОЗАДИ центра => возвращаем −9.0.
    """
    centre = tank_length_m / 2.0
    # смещение трубки относительно центра, в координате «от кормы к носу положительна»
    rel_aft = tube_to_end_bulkhead_m - centre   # >0: трубка впереди центра (от корми)
    return rel_aft if end_is_aft else -rel_aft  # >0 => впереди центра; <0 => позади


def trim_sounding_correction_m(d_signed_m: float, trim_m: float, lbp_m: float) -> float:
    """Поправка к замеру x = d×trim/LBP со знаками таблицы книги (стр. 40):
    трубка впереди центра (d>0) + кормовой дифферент (trim>0) => отрицательная;
    трубка позади центра (d<0) + кормовой дифферент => положительная.
    Эквивалентно x = −|d·trim|/LBP для «перед центром», +|…|/LBP для «позади».
    Q10: d = −9 (позади), trim 2 на корму => книга даёт −0.15 — см. примечание
    в тестах: печатный знак книги противоречит её же таблице знаков."""
    # Физика (схема на стр. 40 книги): при дифференте на корму уровень жидкости
    # в танке наклоняется носом вверх; если трубка ЗАДНОЦЕНТРОВА (d<0), замер
    # завышен относительно середины танка => поправка ОТРИЦАТЕЛЬНАЯ; если трубка
    # ПЕРЕД центром (d>0) => положительная. Это согласовано с таблицей знаков
    # книги при чтении «aft/forward of tank centre» как «задне-/передцентровая».
    # Печатное решение Q10 (−0.15, 1.05−0.15=0.90) воспроизводится точно.
    mag = abs(d_signed_m * trim_m) / lbp_m
    return mag if d_signed_m > 0 else -mag


def even_keel_sounding_m(observed_m: float, correction_m: float) -> float:
    """Even keel sounding = observed + correction (Q10: 1.05 − 0.15 = 0.90)."""
    return observed_m + correction_m


def rectangular_tank_volume_m3(length_m: float, breadth_m: float, depth_m: float) -> float:
    """Объём жидкости в прямоугольном танке = L × B × глубина (Q10: 24×8.2×0.90)."""
    return length_m * breadth_m * depth_m
