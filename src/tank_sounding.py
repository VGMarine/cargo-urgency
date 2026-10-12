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
    """Знаковое d: + если трубка впереди центра танка, − если позади.

    end_is_aft=True: расстояние отсчитано от кормовой переборки (как в Q10).
    """
    centre = tank_length_m / 2.0
    # d_нос = L − a: расстояние трубки до НОСОВОЙ переборки; если > центра — трубка впереди центра
    fwd_pos = (tank_length_m - tube_to_end_bulkhead_m) - centre
    return fwd_pos if end_is_aft else -fwd_pos


def trim_sounding_correction_m(d_signed_m: float, trim_m: float, lbp_m: float) -> float:
    """Поправка к замеру x = −d×trim/LBP при дифференте на корму (trim>0),
    знак по таблице книги (см. модуль docstring)."""
    return -(d_signed_m * trim_m) / lbp_m


def even_keel_sounding_m(observed_m: float, correction_m: float) -> float:
    """Even keel sounding = observed + correction (Q10: 1.05 − 0.15 = 0.90)."""
    return observed_m + correction_m


def rectangular_tank_volume_m3(length_m: float, breadth_m: float, depth_m: float) -> float:
    """Объём жидкости в прямоугольном танке = L × B × глубина (Q10: 24×8.2×0.90)."""
    return length_m * breadth_m * depth_m
