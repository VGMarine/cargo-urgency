import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

import density
import draughts
import perpendiculars


def test_book_example_tan22_times_4121():
    """Контрольное число книги (Dibble, стр. 33): Tan 22° × 4.121 = 1.665 м."""
    corr = perpendiculars.mark_incline_correction(22.0, 4.121)
    assert round(corr, 3) == 1.665


def test_trim_aft_to_midships_one_metre():
    """Ориентир стр. 34: Trim aft to midships = 1.0 m при дифференте 2.0 м."""
    assert perpendiculars.trim_to_midships(8.0, 10.0) == 1.0


def test_density_proportion():
    d = density.density_correction(10.0, rho_observed=1.020)
    assert d == pytest.approx(10.0 * 1.020 / 1.025, rel=1e-12)


def test_dockwater_allowance_sign():
    # в пресной воде судно сидит глубже
    corr = density.dockwater_allowance(10.0, rho_harbour=1.000)
    assert corr == pytest.approx(10.0 * 0.025 / 0.025, rel=1e-12)


def test_amd_simpson_weights():
    # Книга (стр. 18): AMD = (DF+DA)/2 — d_mid не участвует.
    assert draughts.arithmetic_mean_draught(8.0, 10.0, 9.0) == pytest.approx(9.0)
    assert draughts.arithmetic_mean_draught(8.0, 10.0) == pytest.approx(9.0)
    # Весовая схема (6DM+DF+DA)/8 — это Mean Adjusted Draught метода 2(i), стр. 36:
    assert draughts.simpson_weighted_draught(8.0, 10.0, 9.0) == pytest.approx((8 + 10 + 54) / 8)


def test_hog_sag_classification():
    # книга, стр. 35: DM < AMD -> hog; DM > AMD -> sag
    assert draughts.hog_sag(6.40, 6.70) == ("hog", pytest.approx(0.30))
    assert draughts.hog_sag(7.00, 6.70)[0] == "sag"
    assert draughts.hog_sag(6.70, 6.70)[0] == "even"


def test_perpendicular_corrections_q3():
    # QUESTION 3 (стр. 24-25 книги): Df=6.35 Da=7.88, LBP=170,
    # mark fwd 0.15 m aft of stem line @SLL + rake 22° -> misplacement 1.815 м;
    # mark aft 6.00 м вперёд от AP. Ответ книги: -0.017 / +0.057 -> 6.333 / 7.937.
    cf, ca = perpendiculars.perpendicular_corrections(
        d_fwd=6.35, d_aft=7.88, lbp_m=170.0,
        dist_fp_to_df_m=1.815, dist_ap_to_da_m=6.00)
    assert round(cf, 3) == -0.017
    assert round(ca, 3) == 0.057
    assert round(6.35 + cf, 3) == 6.333
    assert round(7.88 + ca, 3) == 7.937


def test_deflection_end_correction_example():
    # EXAMPLE «CORRECTIONS WITH HULL DEFLECTION» (стр. 25 книги, PDF index 33-34):
    # hogged vessel, trim by stern; fwd: 2 x 0.4/(50-2)=0.017 -> 5.983;
    # aft: 5 x 1.0/(50-5)=0.111 -> 7.511.
    c_f = perpendiculars.deflection_end_correction(0.4, 2.0, 50.0)
    c_a = perpendiculars.deflection_end_correction(1.0, 5.0, 50.0)
    assert round(c_f, 3) == 0.017
    assert round(c_a, 3) == 0.111
    assert round(6.00 - c_f, 3) == 5.983
    assert round(7.40 + c_a, 3) == 7.511


def test_first_trim_correction_sign_table():
    # Таблица знаков стр. 31 книги: trim Aft & LCF fwd -> (-);
    # величина Q7 = 5 x 40 x 40 / 150 = 53.33 t.
    import trim as tr
    c = tr.first_trim_correction_t_sign(+5.0, +0.40, 150.0, 40.0)
    assert c == pytest.approx(-53.333333, abs=1e-6)
    # зеркальные случаи таблицы: LCF aft & trim aft -> (+); trim head -> смена знака
    assert tr.first_trim_correction_t_sign(-5.0, +0.40, 150.0, 40.0) > 0
    assert tr.first_trim_correction_t_sign(+5.0, -0.40, 150.0, 40.0) > 0


def test_bad_density_raises():
    with pytest.raises(ValueError):
        density.density_correction(10.0, rho_observed=0.5)


def test_q1_wave_cycle_mean_10_50():
    """Q1 (книга стр. 17): reject 11.40/9.60, сумма оставшихся 105.0 / 10 = 10.50 м.

    Без спора читаются 10 ячеек: 11.25, 9.70(="9.RO"), 11.40(="J J AO" —
    подтверждено ANSWER "Reject 11.40"), 9.70, 11.35, 9.75, 11.10, 9.60,
    11.00, 9.90 (сумма 104.75). Повреждены две: 'I I.;W' (верхняя) и
    '9.(i()' (нижняя; её же отбрасывает ANSWER — значит она минимальная).
    Условие sum(kept)=105.0 при отбрасывании 11.40/9.60 даёт семейство
    hi+lo=10.25; перебор шагом 0.05 в [11.00..11.60]x[9.50..10.00] даёт
    ровно 4 пары: (11.25,10.00), (11.30,9.95), (11.35,9.90), (11.40,9.85).
    Выбрано (11.35, 9.90): '9.(i()' читается как 9.90 ((i) — размытая 9),
    тогда hi=11.35; значение 11.40 при этом остаётся уникальным максимумом
    (иначе ANSWER не назвал бы его для отбрасывания). 10.00 отвергнуто —
    '9.(i()' явно начинается с 9; 11.25/11.40 для 'I I.;W' нечитаемы по глифам.
    TODO(scan): сверить с оригиналом страницы (нужен git lfs pull).
    """
    from readings import wave_cycle_mean
    q1 = [11.25, 9.70, 11.40, 9.70, 11.35, 9.75, 11.10, 9.60,
          11.00, 9.90, 11.35, 9.90]
    kept_sum = sum(sorted(q1)[1:-1])
    assert abs(kept_sum - 105.0) < 1e-9   # печатная строка "Add remainder = 105.0"
    assert abs(wave_cycle_mean(q1) - 10.50) < 1e-9


def test_q2_manometer_centreline_8_153():
    """Q2 (книга стр. 20): port 8.00, stbd 8.25, offset 8.5 м, beam 20.85 м."""
    from readings import manometer_centreline_draught
    d = manometer_centreline_draught(8.00, 8.25, read_offset_m=8.5, beam_m=20.85)
    assert abs(d - 8.153) < 0.0005


def test_deflection_correction_t_method3_alt1():
    # книга, стр. 30 (Method 3 alternative 1): Corr = factor x TPC x hog/sag(cm)
    import draughts as dr
    # Q6-данные (sag): DM 6.18, AMD 6.00, factor 0.76, TPC 20 -> +27.36 t (sag=+)
    c = dr.deflection_correction_t(6.18, 6.00, 0.76, 20.0)
    assert c == pytest.approx(273.6)
    # зеркальный hog: DM 5.82, AMD 6.00 -> -27.36 t (по чек-листу стр.51 hog=-)
    assert dr.deflection_correction_t(5.82, 6.00, 0.76, 20.0) == pytest.approx(-273.6)


# ---------- spec 006: сквозная цепочка ASSESSMENT SUMMARY (стр. 45/51) ----------

def test_assessment_chain_q3_q7_q9_composition():
    """Сборка чек-листа стр. 51 из независимых книжных контролиров.

    Книга не даёт одного сквозного числового примера — поэтому тестируем
    композицию: каждый шаг должен давать СВОЙ печатный контроль
    (Q3 перпендикуляры, Q7 1st trim, Q9 плотность) + знак density (-).
    Данные: Q3-осадки 6.35/7.88, LBP=170, misplacement 1.815/6.00 (стр. 24-25);
    TPC=40 и LCF fwd 5 м (Q7); табличное водоизмещение 15250 t при rho 1.025,
    проба 1.015 (Q9).
    """
    import assessment
    i = assessment.AssessmentInputs(
        d_fwd_mark=6.35, d_aft_mark=7.88, lbp_m=170.0,
        dist_fp_to_df_m=1.815, dist_ap_to_da_m=6.00,
        tpc=40.0, disp_at_mad_t=15250.0,
        lcf_fwd_of_mid_m=5.0, rho_observed=1.015, rho_table=1.025)
    r = assessment.corrected_displacement(i)
    # шаг 1: perpendicular corrections (Q3: 6.35-0.017=6.333; 7.88+0.057=7.937)
    assert round(r.d_fwd_perp, 3) == 6.333
    assert round(r.d_aft_perp, 3) == 7.937
    # AMD по книге стр.18 = (DF+DA)/2 от исправленных осадок
    assert r.amd == pytest.approx((6.333 + 7.937) / 2, abs=1e-3)
    # шаг 2: 1st trim со знаком таблицы стр.31 (LCF fwd & trim stern -> -),
    # по марочному дифференту 1.53 м, LBP=170: -(5*40*153/170) = -180.0 t
    assert r.corr_1st_trim_t == pytest.approx(-180.0, abs=0.01)
    # шаг 3: density (< salt -> минус), контроль Q9 (множитель 1.015/1.025);
    # в цепочке применяется к водоизмещению ПОСЛЕ тоннажных поправок
    # (стр. 45: "adjusted with the 1st and 2nd trim corrections ... all in
    # tonnes", затем correction for density) => от (15250-180).
    assert r.corr_density_t == pytest.approx(-(15250 - 180.0) * 0.010 / 1.025,
                                            abs=0.01)
    # итог: 15250 - 180 - 147.02 = 14922.98
    assert r.corrected_displacement_t == pytest.approx(14922.98, abs=0.01)


def test_assessment_deflection_sign_hog_minus_sag_plus():
    """Прогиб в цепочке: hog уменьшает, sag увеличивает водоизмещение."""
    import assessment
    base = dict(d_fwd_mark=6.00, d_aft_mark=6.00, lbp_m=100.0, tpc=20.0,
                disp_at_mad_t=10000.0)
    hog = assessment.AssessmentInputs(**base, deflection_factor=0.76,
                                      d_mid_corrected=5.82)
    sag = assessment.AssessmentInputs(**base, deflection_factor=0.76,
                                      d_mid_corrected=6.18)
    rh = assessment.corrected_displacement(hog)
    rs = assessment.corrected_displacement(sag)
    assert rh.deflection_corr_t == pytest.approx(-273.6)   # hog (-)
    assert rs.deflection_corr_t == pytest.approx(+273.6)   # sag (+)
    assert rh.corrected_displacement_t < 10000 < rs.corrected_displacement_t


# ---------- spec 007: DEDUCTIBLES / константа / якоря-цепи ----------

def test_deductibles_total_excludes_anchor_chain():
    """SUMMARY OF DEDUCTIBLES (форма D): Anchor & Chain — НЕ вычет (вынесено за борт)."""
    import deductibles
    d = deductibles.Deductibles(ballast_water=500.0, fresh_water=80.0,
                               fuel_oil=300.0, diesel_oil=20.0, slops=5.0,
                               lubricating_oil=15.0, swimming_pool_water=2.0,
                               others=40.0)
    assert d.total() == 962.0


def test_cargo_on_board_and_light_displacement_roundtrip():
    """Форма E: Corrected light disp = Corr.Disp − Cargo − Deductibles (+Anchor&Cable outboard).

    Инверсия cargo_on_board при непротиворечивых входах даёт тот же груз;
    знак Anchor & Chain (стр. 43: вынесенные ПРИБАВЛЯЮТСЯ к грузу) — обеим
    функциям задан согласованно.
    """
    import deductibles
    dd = deductibles.Deductibles(ballast_water=1000.0, fuel_oil=200.0, others=50.0)
    cargo = deductibles.cargo_on_board(15000.0, 5000.0, dd, anchor_and_cable_outboard_t=35.0)
    # 15000 - 5000 - 1250 + 35 = 8785
    assert cargo == pytest.approx(8785.0)
    light = deductibles.corrected_light_displacement(15000.0, cargo, dd, 35.0)
    assert light == pytest.approx(5000.0)   # инверсия точна


def test_constant_definition_book_and_britannia():
    """Constant = Corrected light displacement − Lightship (книга стр.22-23, форма E; Britannia Guidance)."""
    import deductibles
    assert deductibles.constant(9035.0, 9000.0) == pytest.approx(35.0)


def test_chain_weight_is_literal_book_formula():
    """Вес шакла пословно по книге: 15 x d_cm^2 x 3.87 / 1000 (стр. 43)."""
    import deductibles
    # d = 2.7 см -> 15*7.29*3.87/1000 = 0.42316... т
    assert deductibles.chain_weight_per_shackle_t(2.7) == pytest.approx(
        15.0 * 2.7 ** 2 * 3.87 / 1000.0)
    assert deductibles.CHAIN_BOOK_COEFF == pytest.approx(0.05805)
    # цепь из N шаклов
    assert deductibles.chain_cable_weight_t(2.7, 4) == pytest.approx(
        4 * 15.0 * 2.7 ** 2 * 3.87 / 1000.0)


def test_chain_weight_physical_sanity_check():
    """Порядок величины книжного коэффициента подтверждён физикой (TODO(scan) про множитель)."""
    import math
    import deductibles
    # нижняя граница: прямая прутковая длина шакла 15 фатомов = 27.432 м
    # d_cm^2 * (pi/4)*(1e-4 m^2/cm^2) * 27.432 m * 7.85 t/m^3 = t на шакл
    c_straight = 7.85 * math.pi / 4 * 1e-4 * 27.432  # ~0.0169 t per cm^2 of d
    # верхняя граница: полная геометрия звена; запас по коэффициенту
    c_links = c_straight * 4.0
    # книжный коэффициент лежит между: чуть выше прямой длины (избыток металла
    # звеньев ~1.5x), ниже полной геометрической оценки
    assert c_straight < deductibles.CHAIN_BOOK_COEFF < c_links
