"""DEDUCTIBLES: вычеты из водоизмещения и константа судна (spec 007).

Сверено с оригиналом (текстовый слой PDF): Dibble, гл. DEDUCTIBLES — стр. 38
по оглавлению книги (дамп sources/text/dibble.txt, строка 1456; книжная
нумерация напечатана в конце каждой страницы — глава начинается с «38»),
ANCHORS AND CABLES — стр. 42-43 (дамп строки 1662-1678), Lightship Constant —
стр. 22-23 (дамп строки 670-690), SUMMARY OF DEDUCTIBLES (форма «D» UN/ECE,
PAGE 70 дампа) и форма «E» (PAGE 71 дампа).
Дополнительно: Britannia Loss Prevention Guidance (sources/text/guidance.txt,
раздел CONSTANT, строки 27-35) — перекрёстное подтверждение определения
константы («difference in weight of the calculated lightship ... and it's
tabular figures»; «never constant and can vary»).

Цитата (начало главы DEDUCTIBLES):
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


# Коэффициент книжной формулы: 15 x 3.87 / 1000 = 0.05805 (при d в см).
CHAIN_BOOK_COEFF = 15.0 * 3.87 / 1000.0


def chain_weight_per_shackle_t(link_diameter_cm: float) -> float:
    """Weight per shackle (tonne) = 15 x (link diameter in cm)^2 x 3.87 / 1000

    Книга, стр. 43 (дамп dibble.txt, строки 1674-1675):
        "Weight per shackle (tonne) = 15 x (link diameter in cm)2 x 3.87
         ... ----------------------- 1000"
    Реализовано ПОСЛОВНО по текстовому слою: C = 15*3.87/1000 = 0.05805 t/cm^2.

    СВЕРКА С ФИЗИКОЙ (независимая оценка, без контроля в книге): шакл = 15
    фатомов = 27.432 м длины; металл круглого сечения d при плотности стали
    7.85 t/m3 даёт W ≈ 7.85*(pi/4)*(d/100 m)^2*27.432 ≈ 0.0169*d_cm^2 т для
    ПРЯМОЙ прутковой длины цепи. Книжный коэффициент 0.05805 примерно в 3.4
    раза выше — правдоподобно с учётом того, что металл звена длиннее прямой
    оси цепи (полная геометрия звена даёт ~2.26x), плюс шаклы/коуши и
    справочный запас. Порядок величины ПОДТВЕРЖДЁН; точный множитель без
    скана не устанавливается (15 и 3.87 могут быть искажены OCR). Числовой
    пример в книге ОТСУТСТВУЕТ (контроля нет). См.
    test_chain_weight_physical_sanity_check.
    TODO(scan): сверить расстановку десятичного разделителя в «3.87» и «/1000»
    со сканом стр. 43 (git lfs pull) — OCR может исказить множитель.
    """
    return CHAIN_BOOK_COEFF * link_diameter_cm ** 2


def chain_cable_weight_t(link_diameter_cm: float, shackles: float) -> float:
    """Вес вынесенной цепи = shackle_weight x число шаклонов (книга, стр. 43)."""
    return chain_weight_per_shackle_t(link_diameter_cm) * shackles


def round_to_half_tonne(w_t: float) -> float:
    """Округление веса якоря до ближайшей половины тонны (книга, стр. 43):
    'This anchor weight should be rounded to the nearest half tonne'."""
    return round(w_t * 2.0) / 2.0
