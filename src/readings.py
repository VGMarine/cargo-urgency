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


def manometer_centreline_draught(d_low: float, d_high: float,
                                 read_offset_m: float, beam_m: float) -> float:
    """Осадка на ДП по двум манометровым отсчётам (книга, Q2, стр. 19–20).

    Аргументы — отсчёт с МЕНЬШЕЙ осадкой и с БОЛЬШЕЙ осадкой (стороны борта
    задаёт вызывающий; в Q2 port=8.00 < stbd=8.25, т.е. d_low — левый борт).
    Подобные треугольники: разность осадок на полном ширине
        dm_full = beam * (d_high - d_low) / (2 * offset)
    Осадка на ДП = d_low + dm_full / 2 (ДП лежит между точками съёма).
    Проверено Q2: port=8.00, stbd=8.25, offset=8.5м, beam=20.85м:
        dm_full = 20.85*0.25/(2*8.5) = 0.3066; 8.00 + 0.153 = 8.153 м ✔.
    """
    if read_offset_m <= 0 or beam_m <= 0:
        raise ValueError("offset и beam должны быть > 0")
    if d_high < d_low:
        d_low, d_high = d_high, d_low
    dm_full = beam_m * (d_high - d_low) / (2.0 * read_offset_m)
    return d_low + dm_full / 2.0
