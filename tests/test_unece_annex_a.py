"""Тесты порта Annex A (UN/ECE 1992 BASIC) — src/unece_annex_a.py (spec 006).

Контрольные числа — сверенные с оригиналом примеры Dibble:
Q3 (perpendicular corrections), Q5 (Fuller 6/8 = DHSC), Q7 (CO1, знак по
таблице стр. 31), Q8 (CO2 = +7.4 t), Q9 (поправка плотности DISDEN).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

import unece_annex_a as ua


# ---- 30080–30120 vs Dibble QUESTION 3 (стр. 24-25 книги) ----
def test_q3_perpendicular_corrections():
    # observed: fwd 6.35, aft 7.88 (trim by stern); marks: LF=1.815 AFT of FP,
    # LA=6.0 FWD of AP; LBP=170
    stemco, sternco = ua.perpendicular_corrections(
        fore=6.35, aft=7.88, lbp=170.0, lf=1.815, la=6.0,
        stems=+1,   # forward mark misplaced AFT of FPP => STEMS=+1 (aft)
        sterns=-1)  # aft mark misplaced FWD of APP => STERNS=-1 (fwd)
    assert round(stemco, 3) == -0.017     # книга: Correction forward = -0.017 m
    assert round(sternco, 3) == +0.057    # книга: Correction aft = +0.057 m
    assert round(6.35 + stemco, 3) == 6.333
    assert round(7.88 + sternco, 3) == 7.937


# ---- mean-of-means (30170–30200) == Fuller 6/8 (Dibble метод 2(i)) ----
def test_dhsc_equals_fuller_six_eighths():
    fc, ac, mc = 5.64, 6.42, 6.11
    fa = (fc + ac) / 2.0
    mm = (fa + mc) / 2.0
    dhsc = (mm + mc) / 2.0
    assert dhsc == pytest.approx((fc + ac + 6.0 * mc) / 8.0)
    # печатный ответ Dibble Q5: MAD = 6.09 м при DM=6.11, DF=5.64, DA=6.42
    assert round(dhsc, 2) == 6.09


def test_run_survey_q5_pipeline():
    # ровный корпус (FC==FA), метки точно на перпендикулярах
    r = ua.run_survey(fp=5.64, fs=5.64, ap=6.42, as_=6.42, mp=6.11, ms=6.11,
                      lbp=100.0, lf=0.0, la=0.0, lm=0.0,
                      stems=1, sterns=1, mids=1, ke=0.0,
                      tpc=40.0, lcf=0.0, lcfs=1,
                      mtc_plus=322.9, mtc_minus=310.0,
                      displ=15250.0, td=1.025, od=1.025)
    assert r.dhsc == pytest.approx(6.09)
    assert r.hog_sag == pytest.approx(6.11 - (5.64 + 6.42) / 2.0)  # = 0 (even)
    assert r.trim_cm == pytest.approx(78.0)


# ---- first trim correction (30250) vs Dibble QUESTION 7 (+53 t по таблице знаков) ----
def test_q7_first_trim_correction_sign_rule():
    # LBP 150, fwd 6.85 aft 7.25 -> AR=40 см; LCF 5 м FWD of mid (LCFS=-1); TPC 40
    r = ua.run_survey(fp=6.85, fs=6.85, ap=7.25, as_=7.25, mp=7.05, ms=7.05,
                      lbp=150.0, lf=0.0, la=0.0, lm=0.0,
                      stems=1, sterns=1, mids=1, ke=0.0,
                      tpc=40.0, lcf=5.0, lcfs=-1,
                      mtc_plus=0.0, mtc_minus=0.0,
                      displ=0.0, td=1.0, od=1.0)
    # величина: 40*40*5/150 = 53.33 → печать книги «+ 5~ tonnes» (OCR-обломок);
    # таблица знаков стр. 31: trim AFT & LCF fwd of midships => NEGATIVE.
    assert r.co1_t == pytest.approx(-53.333333, rel=1e-6)
    assert abs(round(r.co1_t)) == 53.0 or abs(round(r.co1_t, 1)) == 53.3


def test_co1_reconstructed_s2_from_print_statement():
    # 30240 OCR-артефакт закрыт: S2 восстановлен из строки принта 50220
    # ("Trim fwd(-) aft(+)") и сверяется со знаком CO1 для trim by head:
    r = ua.run_survey(fp=7.25, fs=7.25, ap=6.85, as_=6.85, mp=7.05, ms=7.05,
                      lbp=150.0, lf=0.0, la=0.0, lm=0.0,
                      stems=1, sterns=1, mids=1, ke=0.0,
                      tpc=40.0, lcf=5.0, lcfs=-1,
                      mtc_plus=0.0, mtc_minus=0.0,
                      displ=0.0, td=1.0, od=1.0)
    # trim by the head & LCF fwd => positive (книга, таблица стр. 31)
    assert r.co1_t == pytest.approx(+53.333333, rel=1e-6)


# ---- second trim correction (30290) vs Dibble QUESTION 8 (= +7.4 t) ----
def test_q8_second_trim_correction():
    # AR = 140 см (trim 1.4 м), MTC1(mean+50cm)=322.9, MTC2(mean−50cm)=310.0,
    # LBP=170 — ровно как в портируемой строке: CO2=AR*AR*5*DMDZ/(LBP*1000)
    r = ua.run_survey(fp=5.40, fs=5.40, ap=6.80, as_=6.80, mp=6.10, ms=6.10,
                      lbp=170.0, lf=0.0, la=0.0, lm=0.0,
                      stems=1, sterns=1, mids=1, ke=0.0,
                      tpc=40.0, lcf=0.0, lcfs=1,
                      mtc_plus=322.9, mtc_minus=310.0,
                      displ=0.0, td=1.0, od=1.0)
    assert r.co2_t == pytest.approx(7.436470588, rel=1e-9)
    assert round(r.co2_t, 1) == 7.4          # печать книги Q8
    assert r.co2_t > 0                        # всегда "+" (книга, стр. 32)
    # эквивалентность формуле Dibble 50*t^2*(MCTC2-MCTC1)/LBP:
    assert r.co2_t == pytest.approx(50.0 * 1.4 ** 2 * 12.9 / 170.0)


# ---- плотность (30340–30350) vs QUESTION 9 ----
def test_q9_density_disden():
    # DCO=15250 (CO=0), OD=1.015, TD=1.025 -> DISDEN = 15250*1.015/1.025
    r = ua.run_survey(fp=6.0, fs=6.0, ap=6.0, as_=6.0, mp=6.0, ms=6.0,
                      lbp=100.0, lf=0.0, la=0.0, lm=0.0,
                      stems=1, sterns=1, mids=1, ke=0.0,
                      tpc=40.0, lcf=0.0, lcfs=1,
                      mtc_plus=0.0, mtc_minus=0.0,
                      displ=15250.0, td=1.025, od=1.015)
    assert r.disden_t == pytest.approx(15101.219512, rel=1e-9)
    assert round(r.disden_t, 1) == 15101.2   # ответ книги
    assert r.sd_t < 0                        # в более лёгкой воде — вычет

    # вычетные веса: DISPLNT = DISDEN − DED
    r2 = ua.run_survey(fp=6.0, fs=6.0, ap=6.0, as_=6.0, mp=6.0, ms=6.0,
                       lbp=100.0, lf=0.0, la=0.0, lm=0.0,
                       stems=1, sterns=1, mids=1, ke=0.0,
                       tpc=40.0, lcf=0.0, lcfs=1,
                       mtc_plus=0.0, mtc_minus=0.0,
                       displ=15250.0, td=1.025, od=1.015, ded=300.0)
    assert r2.displnt_t == pytest.approx(r2.disden_t - 300.0)


# ---- киль (MMCO) и полный трим-пайплайн: sanity ----
def test_mmco_keel_and_chain():
    r = ua.run_survey(fp=6.0, fs=6.0, ap=6.0, as_=6.0, mp=6.0, ms=6.0,
                      lbp=100.0, lf=0.0, la=0.0, lm=0.0,
                      stems=1, sterns=1, mids=1, ke=0.15,
                      tpc=40.0, lcf=0.0, lcfs=1,
                      mtc_plus=0.0, mtc_minus=0.0,
                      displ=10000.0, td=1.025, od=1.025)
    assert r.dhsc == pytest.approx(6.0)
    assert r.mmco == pytest.approx(5.85)     # 30210 MMCO=DHSC-KE
    assert r.displ_trimmed_t == pytest.approx(10000.0)  # CO1=CO2=0, ровный киль
    assert r.sd_t == pytest.approx(0.0)


def test_midco_full_trim_quirk_recorded():
    """Листинг считает MIDCO полным тримом J (30130), тогда как Dibble
    EXAMPLE стр. 33–34 для hogged-корпуса использует ПОЛОВИННЫЙ трим конца
    до миделя. Для ровного корпуса (MC==FA) расхождения нет; здесь фиксируем
    поведение источника, чтобы не «улучшить» его молча."""
    # марк мидшафта смещён на 2 м; полный J даёт MIDCO = J*LM/(LBP-P)*S1
    r = ua.run_survey(fp=6.0, fs=6.0, ap=7.4, as_=7.4, mp=6.7, ms=6.7,
                      lbp=100.0, lf=0.0, la=0.0, lm=2.0,
                      stems=1, sterns=1, mids=-1,  # mark 2 m AFT? флаг fwd=-1
                      ke=0.0, tpc=40.0, lcf=0.0, lcfs=1,
                      mtc_plus=0.0, mtc_minus=0.0,
                      displ=0.0, td=1.0, od=1.0)
    j = 7.4 - 6.0
    expected_midco = j * 2.0 / 100.0 * (-1) * (-1)  # S1=-1 (by stern), MIDS=-1
    assert r.mc == pytest.approx(6.7 + expected_midco)
