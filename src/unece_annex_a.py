"""Annex «A» кодекса UN/ECE 1992 — порт программы BASIC на Python (spec 006).

Источник: ECE/ENERGY/19, Annex A "Automatic Calculation Program Connected
with the Draught Survey" (DRAUGHT SURVEY ed. October 1991 - 1.8), печатные
стр. 110–119; OCR-листинг секции 30000 REM DRAFT CALCULATIONS —
`sources/text/unece1992_ocr.txt`, строки 7200–7250 (PDF index 126–127).

Порт дословный по возможности; спорные OCR-места вынесены в комментарии и
закрыты тестами (tests/test_unece_annex_a.py) против контрольных чисел
Dibble Q3/Q5/Q7/Q8.

Соглашения знака (как в листинге):
  * LF/LA/LM — неотрицательные расстояния меток от перпендикуляров;
    STEMS/STERNS/MIDS ∈ {+1 = aft, −1 = fwd};
  * LCF — расстояние до мидля, LCFS ∈ {+1 = aft, −1 = fwd};
  * MTC1 = MTC при mean+D, MTC2 = MTC при mean−D (D=0.5 м в метрическом
    режиме; вход MTC — т·м на САНТИМЕТР, как в гидро静атике);
  * DISPL — табличное водоизмещение при TD; OD/TD — плотности т/м³.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DraftSurveyResult:
    fc: float          # forward corrected draught at FPP
    ac: float          # aft corrected draught at APP
    mc: float          # midships corrected draught at midship mark→pp
    fa: float          # (FC+AC)/2 — arithmetic mean at pp
    mm: float          # mean of means
    dhsc: float        # draught hog/sag corrected (= Fuller 6/8 AMD)
    mmco: float        # DHSC − KE (применимая осадка для таблиц)
    hog_sag: float     # MC − FA (>0 sag, <0 hog)
    trim_cm: float     # AR = |AC−FC|*100 (см)
    co1_t: float       # first trim correction, tonnes (со знаком)
    co2_t: float       # second trim correction, tonnes (всегда +)
    displ_trimmed_t: float   # DCO = DISPL + CO1 + CO2
    sd_t: float              # density correction SD
    disden_t: float          # DISDEN = DCO + SD
    displnt_t: float         # net after deductibles


def perpendicular_corrections(fore: float, aft: float, lbp: float,
                              lf: float, la: float, stems: int, sterns: int):
    """Строки 30080–30120: поправки misplaced marks к перпендикулярам.

    J = ABS(AFT-FORE); S1=-1 если FORE<AFT (trim by stern) иначе +1
    (30090 — знак дифферента); P = ABS(LF+LA) (30100); знаменатель LBP-P.
    STEMCO = J*LF/(LBP-P)*S1*STEMS; STERNCO = J*LA/(LBP-P)*S1*STERNS.

    Соглашение флагов (выведено и ПРОВЕРЕНО печатью Dibble Q3, стр. 24–25;
    тест test_q3_perpendicular_corrections): флаг = направление СМЕЩЕНИЯ
    МАРКИ от перпендикуляра (aft=+1, fwd=−1 — как в INPUT-строках 20150–
    20170 "Stem aft(1) or fwd(-1)"). При trim by the stern S1=−1:
      forward mark 1.815 м AFT of FPP → STEMS=+1 → STEMCO=-0.017 ✔ (книга −);
      aft mark       6.0 м FWD of AP → STERNS=−1 → STERNCO=+0.057 ✔ (книга +).
    Т.е. знак поправки = S1 * направление смещения метки — совпадает с
    правилом книги стр. 32 «поправка отрицательная, если смещение марки
    совпадает с направлением дифферента» (для кормы: trim sternward, mark
    shifted fwd → не совпадает → «+»).
    """
    j = abs(aft - fore)
    s1 = -1 if fore < aft else 1
    p = abs(lf + la)
    denom = lbp - p
    if denom <= 0:
        raise ValueError("LBP - P должен быть > 0")
    return j * lf / denom * s1 * stems, j * la / denom * s1 * sterns


def run_survey(fp: float, fs: float, ap: float, as_: float, mp: float, ms: float,
               lbp: float, lf: float, la: float, lm: float,
               stems: int, sterns: int, mids: int, ke: float,
               tpc: float, lcf: float, lcfs: int,
               mtc_plus: float, mtc_minus: float,
               displ: float, td: float, od: float, ded: float = 0.0,
               metric: bool = True) -> DraftSurveyResult:
    """Секция 30000 целиком (метрическая ветка; imperial — заготовки ниже).

    Аргументы соответствуют INPUT-переменным листинга (стр. 116):
      FP/FS/AP/AS/MP/MS — шесть observed draughts; LF/LA/LM — расстояния
      меток; STEMS/STERNS/MIDS/LCFS ∈ {±1}; KE — толщина киля; TPC; LCF;
      MTC1=mtc_plus (при mean+D), MTC2=mtc_minus (при mean−D); DISPL;
      TD/OD — плотности; DED — сумма вычетных весов.
    """
    # 30040–30060: средние по борта
    fore = (fp + fs) / 2.0
    aft = (ap + as_) / 2.0
    mid = (mp + ms) / 2.0

    # 30070–30130: поправки на перпендикуляры (+ мидель)
    j = abs(aft - fore)
    s1 = -1 if fore < aft else 1   # 30090: trim by stern -> S1=-1
    p = abs(lf + la)                # 30100
    if lbp - p <= 0:
        raise ValueError("LBP - P должен быть > 0")
    stemco = j * lf / (lbp - p) * s1 * stems     # 30110
    sternco = j * la / (lbp - p) * s1 * sterns   # 30120
    # ⚠️ Артефакт OCR строки 30130 отсутствует; MIDCO читается в §2 спеки
    # как Lm*(AFT-FORE)/(LBP-P)*S1*MIDS — но это НЕ согласуется с примером
    # deflection книги (Dibble стр. 33–34: там носовая поправка считается
    # ПОЛОВИННЫМ тримом forward-to-midships). В листинге MIDCO использует
    # тот же полный J; оставляем как в источнике, расхождение фиксируем
    # тестом test_midco_full_trim_quirk (N/A для ровного корпуса).
    midco = j * lm / (lbp - p) * s1 * mids

    # 30140–30160
    fc, ac, mc = fore + stemco, aft + sternco, mid + midco

    # 30165–30210: hog/sag, mean-of-means
    fa = (fc + ac) / 2.0
    mm = (fa + mc) / 2.0
    hog_sag = mc - fa
    dhsc = (mm + mc) / 2.0          # == (FC + AC + 6*MC)/8 — Fuller 6/8
    mmco = dhsc - ke

    # 30220–30260: first trim correction
    ar = abs((ac - fc) * 100.0)     # см
    # 30240: OCR читается "IF AC<FC THEN S2=1 ELSE S2=1" — явный артефакт
    # скана (оба колена дают 1). По правилу знаков Dibble стр. 31/spec 004
    # (и по строке принта 50220 "Trim fwd(-) aft(+): AR*S2"):
    s2 = 1 if ac > fc else -1       # +1 = trim by the stern
    # 30250 метрически: layer(m) = AR/100 * LCF/LBP; tonnes = layer*TPC*100
    # => CO1 = AR*TPC*LCF/LBP*S2*LCFS (AR в см — степень сокращается)
    co1 = ar * tpc * lcf * lcfs / lbp * s2
    if not metric:
        co1 = co1 / 100.0           # 30260 IF Y=1 THEN CO1=CO1/100

    # 30270–30300: second trim correction
    dmdz = mtc_plus - mtc_minus
    if metric:
        # ⚠️ OCR 30290: "CO2=AR*AR*5*DMDZ/(LBP*1000)". При AR в САНТИМЕТРАХ
        # это в точности формула Dibble (стр. 32): C2 = 50*t^2*(MCTC2-MCTC1)/LBP,
        # t в м: 50*(AR/100)^2 = AR^2*50/10000 = AR^2*5/1000 ✔.
        co2 = ar * ar * 5.0 * dmdz / (lbp * 1000.0)
    else:
        # 30300 (imperial, OCR шумен): CO2=AR/12*AR/12*6*DMDZ/(LBP/.0012)...
        # зафиксировано как есть, вне объёма метрических тестов.
        co2 = (ar / 12.0) * (ar / 12.0) * 6.0 * dmdz / (lbp / 0.0012)

    # 30310–30320
    co = co1 + co2
    dco = displ + co

    # 30330–30360: плотность и вычеты
    disden = dco / td * od          # = DCO * OD/TD (книга: x density1/density2)
    sd = disden - dco
    displnt = disden - ded

    return DraftSurveyResult(fc, ac, mc, fa, mm, dhsc, mmco, hog_sag, ar,
                             co1, co2, dco, sd, disden, displnt)
