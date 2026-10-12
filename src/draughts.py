"""Средняя осадка AMD (spec 003). Черновик: Dibble, стр. 18."""
from __future__ import annotations


def arithmetic_mean_draught(d_fwd: float, d_aft: float, d_mid: float) -> float:
    """AMD = (dF + dA + 6*dM) / 8 — весовая схема Simpson 1-6-1."""
    return (d_fwd + d_aft + 6.0 * d_mid) / 8.0


def mean_of_sides(d_port: float, d_stbd: float) -> float:
    return (d_port + d_stbd) / 2.0


def wave_rejected_mean_m(readings_m: list[float], reject: list[float]) -> float:
    """QUESTION 1 (Dibble, стр. 17 книги, PDF page_025): средняя осадка по волне.

    Метод книги: из цикла отсчётов «на глаз» отвергаются явно выбивающиеся
    крайние значения (в примере — 11.40 и 9.60), остальные суммируются и делятся
    на их число. Список отвергаемых задаёт наблюдатель (книга не даёт формального
    критерия) — поэтому reject передаётся аргументом.
    Эталон книги (стр. 17): "Reject 11.40 and 9.60 m. Add remainder = 105.
    Estimated draught reading = 105/10 = 10.50 m".
    КОНСОЛИДАЦИЯ с дампом page_025.txt: по распознанным 12 значениям сумма
    после отбрасывания = 104.90 (среднее 10.49), т.е. ровно на 0.1 меньше
    печатной суммы; перебор всех одиночных замен показывает неединственность
    «виновника» — вывод: в скане потеряна одна десятая внутри списка отсчётов
    (метод и ответ книги 10.50 при этом верны). Тест фиксирует метод + допуск.
    """
    kept = [r for r in readings_m if r not in reject]
    return sum(kept) / len(kept)


def centreline_draught_from_manometer_m(port_m: float, diff_full_beam_m: float,
                                        half_reading_dist_m: float,
                                        beam_m: float) -> float:
    """QUESTION 2 (Dibble, стр. 20 книги, PDF page_028): осадка на ДП по манометру.

    Отсчёты сняты на расстояниях ±half_reading_dist_m от ДП. По подобию
    треугольников книга сначала находит разницу на полном наборе (full beam):
        d_full = beam * diff_readings / (2 * half_reading_dist)
    затем половину этой разницы прибавляет к одному из отсчётов (со знаком —
    если на противоположной стороне отсчёт БОЛЬШЕ, вода ниже у данной стороны,
    осадка на ДП больше). Эталон: 8.00 + 0.153 = 8.153 м.
    """
    d_full = beam_m * diff_full_beam_m / (2.0 * half_reading_dist_m)
    return port_m + d_full / 2.0


def amd_finer_form(d_fwd: float, d_aft: float, d_mid: float) -> float:
    """Mean adjusted draught, finer-lined vessel (книга, Q5, стр. 29).

    AMD = (6*DM + DF + DA)/8. Выверено по печатному ответу книги 6.03:
    единственное DM, воспроизводящее ответ — 6.03 (OCR 'G.ll' консолидировано).
    """
    return (6.0 * d_mid + d_fwd + d_aft) / 8.0


def amd_fuller_form(d_fwd: float, d_aft: float) -> float:
    """A.M.D., fuller-form vessel (книга, Q6, стр. 29-30): (DF+DA)/2."""
    return (d_fwd + d_aft) / 2.0


def mad_from_factor(amd: float, d_mid: float, factor: float) -> float:
    """Method 3 (книга, стр. 29-30): MAD = AMD + factor*(DM - AMD).

    factor считывается из графика по коэффициенте полноты ватерлинии
    (Cw): для Cw=0.60 книга даёт factor=0.76 (Q6).
    """
    return amd + factor * (d_mid - amd)
