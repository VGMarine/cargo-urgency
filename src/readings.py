"""Обработка отсчётов осадок на волнении (spec 005, книга стр. 16–17).

СВЕРЕНО с текстовым слоем PDF: Dibble, «Measuring the draughts in a swell»
(стр. 16 книги, PDF index 24) и QUESTION 1 (стр. 17, PDF index 25).
"""
from __future__ import annotations


def wave_cycle_mean(readings: list[float], n_keep: int = 10) -> float:
    """Среднее по методу книги: из серии средних отсчётов за цикл волны
    ОТБРАСЫВАЕМ самый высокий и самый низкий, усредняем остальные.

    Цитата стр. 16: "A total of 12 mean readings should be obtained. The
    highest and lowest means should be rejected and then the average of the
    remaining ten will give the most accurate reading possible."
    n_keep=10 — печатный контроль Q1: сумма оставшихся 105.0 / 10 = 10.50 м.
    """
    if len(readings) < 3:
        raise ValueError("нужно минимум 3 отсчёта")
    rs = sorted(readings)
    kept = rs[1:-1] if n_keep == len(rs) - 2 else rs[:n_keep]
    # при стандартном вызове (12 значений) kept = 10 средних
    return sum(kept) / len(kept)


def manometer_centreline_draught(d_port: float, diff_m: float,
                                 read_offset_m: float, beam_m: float,
                                 higher_side_is_starboard: bool = True) -> float:
    """Осадка на ДП по двум манометровым отсчётам (книга, Q2, стр. 20).

    Подобные треугольники (цитата): d = beam x (diff / (2*offset)) — разность
    осадок на полном ширине; половина разности добавляется к стороне с
    МЕНЬШИМ отсчётом? Нет — к отсчёту низкой стороны прибавляем половину
    перепада в направлении ДП, если ДП лежит между точками съёма:
        full-beam difference dm = beam * diff / (2 * offset)
        centreline draught = d_low + dm/2   (низкая сторона — левый борт,
        когда starboard reading higher)
    Проверено Q2: 8.00 + (20.85*0.25/17)/2 = 8.00 + 0.153 = 8.153 м ✔.
    """
    if read_offset_m <= 0 or beam_m <= 0:
        raise ValueError("offset и beam должны быть > 0")
    dm_full = beam_m * diff_m / (2.0 * read_offset_m)
    # d_port трактуется как отсчёт ЛЕВОГО борта (как в Q2: port = 8.00).
    # ДП лежит между точками съёма => к МЕНЬШЕМУ отсчёту прибавляем
    # половину перепада на полную ширину (к большему — вычитаем):
    #   starboard выше => port = меньший => +dm/2;  port выше => −dm/2.
    return d_port + dm_full / 2.0 if higher_side_is_starboard else d_port - dm_full / 2.0
