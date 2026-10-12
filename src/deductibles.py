"""DEDUCTIBLES: вычеты из водоизмещения и константа судна (spec 007).

Сверено с оригиналом (текстовый слой PDF): Dibble, стр. 38/46-44 книги
(PDF index 46-52 в дампе sources/text/dibble.txt), SUMMARY OF DEDUCTIBLES
(форма «D» UN/ECE, PAGE 70 дампа) и форма «E» (PAGE 71 дампа).
Дополнительно: Britannia Loss Prevention Guidance (sources/text/guidance.txt,
раздел CONSTANT) — перекрёстное подтверждение определения константы.

Цитата (стр. 46 книги, начало главы DEDUCTIBLES):
    "The deductibles are the components of the ship's total weight, which must
     be deducted from the calculated displacement in order to determine the
     weight of cargo on board."
Состав полного веса (там же): Light displacement; Cargo; Ballast; Fuel and
fresh water; Swimming pool water and other easily forgotten weights; Stores
and Provisions; Crew and effects.Stores/provisions/crew могут быть добавлены к
light displacement (обычно входят в константу).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Deductibles:
    """SUMMARY OF DEDUCTIBLES (книга, форма «D», PAGE 70 дампа) — тонны.

    Anchor & Chain: вес якорей/цепей, ВЫНЕСЕННЫХ за борт (на грунте) —
    они уже НЕ включены в lightship, поэтому это НЕ вычет, а прибавка
    к количеству груза (см. anchor_and_cable_credit_t / cargo_on_board).
    """
    ballast_water: float = 0.0
    fresh_water: float = 0.0
    fuel_oil: float = 0.0
    diesel_oil: float = 0.0
    slops: float = 0.0
    lubricating_oil: float = 0.0
    swimming_pool_water: float = 0.0
    others: float = 0.0  # stores, provisions, crew and effects и т.п.

    def total(self) -> float:
        """Total Deductibles (тонны), без якорей/цепей."""
        return (self.ballast_water + self.fresh_water + self.fuel_oil +
                self.diesel_oil + self.slops + self.lubricating_oil +
                self.swimming_pool_water + self.others)


def cargo_on_board(corrected_displacement_t: float,
                   light_displacement_t: float,
                   deductibles: Deductibles,
                   anchor_and_cable_outboard_t: float = 0.0) -> float:
    """Груз на борту (тонны).

    Книга, стр. 46: deductibles вычитаются из вычисленного водоизмещения;
    стр. 43 (ANCHORS AND CABLES): "The loss of weight due to its removal is
    weight taken from the light displacement, this amount should therefore be
    added to the quantity of cargo" — вынесенные якорь/цепь ПРИБАВЛЯЮТСЯ.

        Cargo = Corrected Displacement − Light Displacement − ΣDeductibles
                + Anchor & Cable (outboard)
    """
    return (corrected_displacement_t - light_displacement_t
            - deductibles.total() + anchor_and_cable_outboard_t)


def constant(corrected_light_displacement_t: float,
             lightship_t: float) -> float:
    """Lightship Constant (тонны).

    Книга, стр. 22-23 (PDF index 22-23): расчётный лёгкий вес (водоизмещение
    порожнем по замерам минус все deductibles) минус табличный lightship из
    stability information book. Форма «E»: Constant = Corrected light
    displacement − Lightship; сверяется с declared constant и
    mean of previous constants.

    Britannia Guidance (CONSTANT): "difference in weight of the calculated
    lightship (by draft survey without the cargo) and it's tabular figures".
    Константа НЕ постоянна (growth of lightship ~0.2%/год, стр. 22).
    """
    return corrected_light_displacement_t - lightship_t


def corrected_light_displacement(corrected_displacement_t: float,
                                 cargo_t: float,
                                 deductibles: Deductibles,
                                 anchor_and_cable_outboard_t: float = 0.0) -> float:
    """Corrected light displacement для формы «E» (PAGE 71 дампа).

    = Corrected Displacement − Cargo − ΣDeductibles + Anchor&Cable(outboard).
    Инверсия cargo_on_board: при непротиворечивых входах даёт тот же результат.
    """
    return (corrected_displacement_t - cargo_t - deductibles.total()
            + anchor_and_cable_outboard_t)


def chain_weight_per_shackle_t(link_diameter_cm: float) -> float:
    """Weight per shackle (tonne) = 15 x (link diameter in cm)^2 x 3.87 / 1000

    Книга, стр. 43 (PDF index 51): "Weight per shackle (tonne) = 15 x (link
    diameter in cm)^2 x 3.87 / 1000". Реализовано ПОСЛОВНО по текстовому слою.

    ВНИМАНИЕ (конфликт с независимой сверкой): книжный коэффициент даёт
    C = 15*3.87/1000 = 0.05805 t/cm^2, т.е. 0.423 t/шакл при d = 2.7 см.
    Физическая оценка массы шакла (сталь 7.85 t/m3, металл ~15 м длины):
    W = pi/4 * d_cm^2 * 15м * ... ≈ 0.00926 t/cm^2 — книжное значение
    завышено ~в 6 раз; классические справочные формулы дают W(t/шакл) ≈
    0.07..0.08 * d_cm^2 (d в мм: W = d^2 * L / константа). Вероятная OCR-
    неоднозначность: «x 3.87 / 1000» может читаться как «x 387 / 10000» или
    иная расстановка десятичного разделителя. Числовой пример в книге
    отсутствует (контроля нет). РЕАЛИЗОВАНО ПОСЛОВНО + TODO(scan): сверить
    множителb со сканом стр. 43 до практического применения.
    """
    return 15.0 * link_diameter_cm ** 2 * 3.87 / 1000.0


def chain_cable_weight_t(link_diameter_cm: float, shackles: float) -> float:
    """Вес вынесенной цепи = shackle_weight x число шаклонов (книга, стр. 43)."""
    return chain_weight_per_shackle_t(link_diameter_cm) * shackles
