"""Обработка отсчётов осадок на волнении (spec 005, книга стр. 16–17, PDF index 24–25).

СВЕРЕНО с текстовым слоем: Dibble, «Measuring the draughts in a swell» и QUESTION 1/2.
"""
from __future__ import annotations


def wave_cycle_mean(readings: list[float]) -> float:
    """Среднее по методу книги (стр. 16): из серии средних отсчётов за цикл
    волны отбрасываем самый высокий и самый низкий, усредняем остальные.

    Цитата: "A total of 12 mean readings should be obtained. The highest and
    lowest means should be rejected and then the average of the remaining ten
    will give the most accurate reading possible."
    Печатный контроль Q1: сумма оставшихся 105.0 / 10 = 10.50 м.
    """
    if len(readings) < 3:
        raise ValueError("нужно минимум 3 отсчёта")
    rs = sorted(readings)
    kept = rs[1:-1]
    return sum(kept) / len(kept)


def manometer_centreline_draught(d_port: float, d_starboard: float,
                                 read_offset_m: float, beam_m: float) -> float:
    """Осадка на ДП по двум манометровым отсчётам (книга, Q2, стр. 20).

    Подобные треугольники: разность осадок на полном ширине
        dm_full = beam * |diff| / (2 * offset)
    Осадка на ДП = меньший отсчёт + dm_full / 2 (ДП лежит между точками съёма;
    больший отсчёт — та сторона, что ниже ватерлинии при диффере/наклоне).
    Проверено Q2: port=8.00, stbd=8.25, offset=8.5м, beam=20.85м:
        dm_full = 20.85*0.25/(2*8.5) = 0.3066; 8.00 + 0.153 = 8.153 м ✔.
    """
    if read_offset_m <= 0 or beam_m <= 0:
        raise ValueError("offset и beam должны быть > 0")
    diff = abs(d_starboard - d_port)
    dm_full = beam_m * diff / (2.0 * read_offset_m)
    return min(d_port, d_starboard) + dm_full / 2.0
