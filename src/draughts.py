"""Средняя осадка AMD (spec 003).

СВЕРЕНО с оригиналом (текстовый слой PDF): Dibble, стр. 18 книги
(PDF index 21) — определение; стр. 35–36 (PDF index 38–39) — методы hog/sag.
Цитата стр. 18: "The arithmetical mean of the forward draught and the aft
draught will equal the draught midships if there is no hog- or sag, this is
called the arithmetic mean draught." — т.е. в книге AMD = (DF+DA)/2, а не
1-6-1; весовая схема Simpson встречается только как «mean adjusted draught»
метода 2 для finer-lined судов (стр. 36).
"""
from __future__ import annotations


def arithmetic_mean_draught(d_fwd: float, d_aft: float, d_mid: float = None) -> float:
    """AMD по книге (стр. 18): (dF + dA) / 2.

    Аргумент d_mid принят для обратной совместимости и НЕ используется:
    книга определяет AMD как среднее носовой и кормовой осадок; сравнение
    полученного AMD с исправленной миделевой осадкой — отдельный шаг
    («to establish whether the hull is distorted», стр. 35).
    """
    return (d_fwd + d_aft) / 2.0


def simpson_weighted_draught(d_fwd: float, d_aft: float, d_mid: float) -> float:
    """Weighted mean (6*DM + DF + DA)/8 — «mean of mean of means».

    В книге это НЕ AMD: это Mean Adjusted Draught метода 2(i) для
    finer-lined vessels (стр. 36, Q5). Реализовано отдельно, чтобы не
    смешивать определения.
    """
    return (d_fwd + d_aft + 6.0 * d_mid) / 8.0


def mean_of_sides(d_port: float, d_stbd: float) -> float:
    return (d_port + d_stbd) / 2.0


def amd_finer_form(d_fwd: float, d_aft: float, d_mid: float) -> float:
    """Mean adjusted draught, finer-lined vessel (книга, Q5, стр. 29).

    AMD = (6*DM + DF + DA)/8. Выверено по печатному ответу книги 6.03:
    единственное DM, воспроизводящее ответ — 6.03 (OCR 'G.ll' консолидировано).
    """
    return (6.0 * d_mid + d_fwd + d_aft) / 8.0


def amd_fuller_form(d_fwd: float, d_aft: float) -> float:
    """A.M.D., fuller-form vessel (книга, Q6, стр. 29-30): (DF+DA)/2.

    Печатанное решение Q6 явно считает AMD = (5.80 + 6.20)/2 = 6.00 м.
    Примечание (TODO scan): напечатанная формула метода 2(ii) распознана как
    "(4 x DM) + 6 DF + DA" — знаменатель и расстановка скобок нечитаемы из OCR;
    ни одна целочисленная трактовка с DM не воспроизводит 6.00, решение книги
    использует (DF+DA)/2. Сверить по скану PDF index 39 (стр. 36 книги).
    """
    return (d_fwd + d_aft) / 2.0


def hog_sag(d_mid_corrected: float, amd: float) -> tuple[str, float]:
    """Классификация прогиба по книге (стр. 35, PDF index 38).

    "If the actual draught is less than AMD then the vessel is hogged.
     If the actual draught is greater than AMD then the vessel is sagged."
    Возвращает ("hog"/"sag"/"even", величина в метрах).
    """
    diff = d_mid_corrected - amd
    if diff < 0:
        return "hog", -diff
    if diff > 0:
        return "sag", diff
    return "even", 0.0


def mad_from_factor(amd: float, d_mid: float, factor: float) -> float:
    """Method 3 (книга, стр. 29-30): MAD = AMD + factor*(DM - AMD).

    factor считывается из графика по коэффициенте полноты ватерлинии
    (Cw): для Cw=0.60 книга даёт factor=0.76 (Q6).
    """
    return amd + factor * (d_mid - amd)


def deflection_correction_t(d_mid: float, amd: float, factor: float,
                            tpc: float) -> float:
    """Method 3 alternative 1 (книга, стр. 30, PDF index 38) — прогиб сразу в тоннах.

    Цитата: "Correction (tonne) = factor x TPC x hog/sag (cm)"
            "hog/sag (cm) = (DM - AMD) x 100"
    Знак по CORRECTIONS CHECK LIST (стр. 51): hog (-), sag (+); формула с
    знаками сама: DM<AMD (hog) => множитель <1 => водоизмещение уменьшаем.
    Контроль знака: Q6 (sag, DM 6.18 > AMD 6.00) -> поправка положительна.
    """
    return factor * tpc * (d_mid - amd) * 100.0
