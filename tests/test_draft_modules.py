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
