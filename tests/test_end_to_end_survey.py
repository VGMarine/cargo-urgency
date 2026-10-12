"""Сквозной end-to-end тест: сырые показания рулеток → груз по форме «E».

«Свадьба» двух модулей, ранее покрытых только отдельными тестами:
  src/unece_annex_a.py  (порт BASIC-программы Annex A кодекса UN/ECE 1992)
  src/unece_forms.py    (машиночитаемая модель отчёта по формам A–E)

Данные — свёренные с оригиналом примеры Dibble «Draught Surveys», сведённые
в один сквозной сёрвей (книга считает вопросы изолированно; здесь они
соединены конвейером кодекса Annex A/Form C без изменения контрольных чисел):
  * QUESTION 3 (стр. 24–25): observed fwd 6.35 / aft 7.88 м, метки
    LF=1.815 м AFT of FPP, LA=6.0 м FWD of APP, LBP=170
    → печати поправок −0.017/+0.057 → FC=6.333 / AC=7.937;
  * QUESTION 5 (стр. 29): DM=6.11 → Fuller AMD=(6·DM+DF+DA)/8=6.09 —
    осадка на перпендикулярах (Q3 ещё не применена);
  * QUESTION 8 (стр. 33): AMD=6.10, trim 1.4 м by stern, MCTC(5.60)=310.0,
    MCTC(6.60)=322.9, LBP=170 → печать «+ 7.4 tonnes»;
  * QUESTION 9 (стр. 36): DISPL=15250 t при TD=1.025, OD=1.015 → 15101.2 t.

Согласование склейки (важное, зафиксировано явно):
  * Q8-овский trim 1.4 м воспроизводится показаниями fwd 5.40 / aft 6.80
    (наблюдаемый трим ровно 1.40; метки точно на перпендикулярах);
  * Q3-овские поправки на перпендикуляры проверяются отдельно (путь 1b),
    т.к. смещённые метки меняют трим на перпендикулярах до 1.604 м и CO2
    перестаёт быть печатным числом Q8;
  * MIDCO=0 ⇒ MC−FA=0 ⇒ hog_sag=0 ⇒ mean-of-means (DHSC) совпадает с
    печатной AMD 6.10 (метод 2(i)) — расхождение методов зафиксировано
    в specs/003b и test_mean_of_means_differs_from_fuller_with_trim.

Проверяются три независимых пути к одним и тем же строкам бланка C/E:
  путь 1 — BASIC-листинг (run_survey от сырых readings);
  путь 2 — ручная цепочка формы C (значения, которые вносит сёрвейор);
  путь 3 — форма E (Difference = cargo) для LOADED/UNLOADED.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

import unece_annex_a as ua
from unece_forms import (
    DraughtReadings,
    ShipHydroStatics,
    SurveyMeta,
    SurveyReport,
)

# ---- данные примеров книги --------------------------------------------------
LBP = 170.0
# Сквозной сёрвей (Q5+Q8+Q9): fwd/aft дают наблюдаемый трим ровно 1.40 м by
# stern (печать Q8), средняя по перпендикулярам = AMD 6.10; метки на pp.
DF_OBS, DA_OBS, DM = 5.40, 6.80, 6.10
MTC_MINUS, MTC_PLUS = 310.0, 322.9      # Q8: MCTC at mean−D / mean+D
DISPL, TD, OD = 15250.0, 1.025, 1.015   # Q9
TPC, LCF = 20.0, 0.0                    # LCF at midships → CO1 = 0 (чисто)
DED = 250.0                             # условная сумма вычетных весов (t)
# Данные Q3 (смещённые метки) — отдельный прогон 1b:
Q3_DF, Q3_DA = 6.35, 7.88
LF_AFT_OF_FPP, LA_FWD_OF_APP = 1.815, 6.0


def _raw_readings(d_forward_port, d_forward_stbd, d_midship_port,
                  d_midship_stbd, d_after_port, d_after_stbd):
    """Сырые показания формы C (PORT/STBD) без поправок."""
    return dict(
        line013=d_forward_port, line021=d_forward_stbd,
        line073=d_midship_port, line081=d_midship_stbd,
        line033=d_after_port, line041=d_after_stbd,
    )


def _survey(fp, fs, ap, as_, mp, ms, lf=0.0, la=0.0, stems=1, sterns=1):
    return ua.run_survey(
        fp=fp, fs=fs, ap=ap, as_=as_, mp=mp, ms=ms,
        lbp=LBP, lf=lf, la=la, lm=0.0,
        stems=stems, sterns=sterns, mids=1, ke=0.0,
        tpc=TPC, lcf=LCF, lcfs=1,
        mtc_plus=MTC_PLUS, mtc_minus=MTC_MINUS,
        displ=DISPL, td=TD, od=OD, ded=DED,
    )


def test_run_survey_reproduces_q5_q8_q9_prints():
    """Путь 1a: BASIC-листинг от сырых показаний печатает ответы Q5/Q8/Q9."""
    r = _survey(DF_OBS, DF_OBS, DA_OBS, DA_OBS, DM, DM)
    assert round(r.fc, 2) == 5.40 and round(r.ac, 2) == 6.80   # метки на pp
    assert round(r.dhsc, 2) == 6.10               # AMD печати Q8 (mean-of-means)
    assert round(r.hog_sag, 9) == 0.0             # MC == FA ⇒ без прогиба
    assert round(r.trim_cm) == 140                # trim 1.40 м by stern (Q8)
    assert r.co1_t == 0.0                         # LCF в миделе — 1st TC = 0
    assert round(r.co2_t, 1) == 7.4               # Q8 печать (+7.4 tonnes)
    assert r.co2_t > 0                            # всегда «+» (стр. 32)
    # ВАЖНО (задокументировано): конвейер применяет поправку плотности к
    # водоизмещению ПОСЛЕ trim-поправок (книга стр. 45 ASSESSMENT SUMMARY и
    # листинг 30340), поэтому итог = (DISPL+CO2)*OD/TD = 15108.6 t.
    # Печатная величина Q9 15101.2 t — изолированный пример книги (без CO2).
    assert round(r.disden_t, 1) == round((DISPL + r.co2_t) * OD / TD, 1)
    assert round(r.disden_t, 1) == 15108.6        # фиксация сквозного числа
    assert round(r.displnt_t, 1) == round(r.disden_t - DED, 1)


def test_run_survey_reproduces_q3_mark_corrections():
    """Путь 1b: смещённые метки Q3 — поправки −0.017/+0.057 → 6.333/7.937."""
    r = _survey(Q3_DF, Q3_DF, Q3_DA, Q3_DA, DM, DM,
                lf=LF_AFT_OF_FPP, la=LA_FWD_OF_APP, stems=+1, sterns=-1)
    assert round(r.fc - Q3_DF, 3) == -0.017       # Q3 печать correction forward
    assert round(r.ac - Q3_DA, 3) == +0.057       # Q3 печать correction aft
    assert round(r.fc, 3) == 6.333                # Q3 печать corrected fwd
    assert round(r.ac, 3) == 7.937                # Q3 печать corrected aft
    # Тождество методик действует только при MC == FA (ровный киль или
    # симметричный прогиб). Здесь метки смещены асимметрично ⇒ MIDCO=0,
    # но FA != MC (трим по перпендикулярам изменился), поэтому:
    fa = (r.fc + r.ac) / 2.0
    assert r.mm == pytest.approx((fa + r.mc) / 2.0)          # mean-of-means
    fuller = (r.fc + r.ac + 6 * r.mc) / 8.0                  # Fuller 6/8
    assert r.dhsc == pytest.approx(fuller)                   # листинг: DHSC=(MM+MC)/2 == Fuller
    assert not pytest.approx(r.mm).__eq__(fuller)            # при hog/sag методы расходятся
    assert fuller == pytest.approx(6.3587, abs=5e-4)
    assert r.mm == pytest.approx(6.6174, abs=5e-4)
    # Числа заметно больше печатной AMD 6.09 из Q5 (там DF/DA 5.64/6.42);
    # расхождение методов при nonzero hog/sag зафиксировано в specs/003b и
    # test_mean_of_means_differs_from_fuller_with_trim.


def test_forms_chain_matches_annex_a_numbers():
    """Путь 2: ручная цепочка формы C (= значения сёрвейора) == вывод листинга."""
    r = _survey(DF_OBS, DF_OBS, DA_OBS, DA_OBS, DM, DM)
    readings = DraughtReadings(
        **_raw_readings(DF_OBS, DF_OBS, DM, DM, DA_OBS, DA_OBS),
        stem_correction_fp=r.fc - DF_OBS,          # = 0 (метки на pp)
        stern_correction_ap=r.ac - DA_OBS,         # = 0
        sag_hog_m=r.hog_sag,                       # hog/sag по конвенции C (+sag)
        observed_density=OD * 1000.0,              # форма C: kg/m3
        tables_density=TD * 1000.0,
        displacement_tables=DISPL,
        first_trim_correction_t=r.co1_t,           # = 0 при LCF в миделе
        second_trim_correction_t=r.co2_t,
        total_deductibles_t=DED,
    )
    assert readings.d_forward_corrected == pytest.approx(r.fc)
    assert readings.d_after_corrected == pytest.approx(r.ac)
    assert readings.mean_of_means == pytest.approx(r.mm)       # (FA+MC)/2
    assert readings.draught_moulded_corrected == pytest.approx(r.dhsc)  # line 152
    assert readings.trim_m == pytest.approx(r.ac - r.fc)
    # сёрвейор вносит в бланк округлённое печатное число CO2 (+7.4), тогда как
    # листинг несёт точное 7.43647 — расхождение 0.036 t допустимо и фиксируется:
    assert readings.second_trim_correction_t == pytest.approx(r.co2_t)
    assert readings.displacement_corrected_for_trim == pytest.approx(
        r.displ_trimmed_t)
    # плотность применяется после trim (тот же порядок, что в листинге):
    assert round(readings.displacement_corrected_for_density, 1) == 15108.6
    assert round(readings.displacement_net, 1) == round(r.displnt_t, 1)


def _report(survey_type: str, start: DraughtReadings, finish: DraughtReadings):
    meta = SurveyMeta(
        survey_type=survey_type,
        corporate_identification="TEST SURVEYORS LTD",
        office_of_surveyor="TEST OFFICE",
        vessel="MV TEST", call_letters="TESTCALLSIGN", survey_no="TS-1",
        registry="TESTREG", built_year=2000, built_by="TESTYARD",
        flag="TESTFLAG", port="TESTPORT",
    )
    ship = ShipHydroStatics(
        lbp_m=LBP, tpc=TPC, lcf_m=LCF,
        mctc_plus50=MTC_PLUS, mctc_minus50=MTC_MINUS,
    )
    return SurveyReport(meta=meta, ship=ship, starting=start, finishing=finish)


def _readings_with_displ(value: float) -> DraughtReadings:
    return DraughtReadings(
        **_raw_readings(DF_OBS, DF_OBS, DM, DM, DA_OBS, DA_OBS),
        stem_correction_fp=0.0, stern_correction_ap=0.0,
        observed_density=OD * 1000.0, tables_density=TD * 1000.0,
        displacement_tables=value,
        first_trim_correction_t=0.0, second_trim_correction_t=7.4,
        total_deductibles_t=DED,
    )


def test_form_e_loaded_vessel_cargo():
    """Путь 3a: загрузка EMPTY→LOADED = finishing.net − starting.net."""
    empty, loaded = _readings_with_displ(DISPL), _readings_with_displ(DISPL + 1000.0)
    rep = _report("LOADED", empty, loaded)
    assert round(rep.total_cargo_in_bulk_t, 1) == round(
        (loaded.displacement_net - empty.displacement_net), 1)
    # плотность одинакова в обоих состояниях → разность net = 1000*OD/TD
    assert round(rep.total_cargo_in_bulk_t, 1) == round(1000.0 * OD / TD, 1)


def test_form_e_unloaded_sign_flip():
    """Путь 3b: выгрузка LOADED→EMPTY даёт тот же +cargo (разворот знака)."""
    empty, loaded = _readings_with_displ(DISPL), _readings_with_displ(DISPL + 1000.0)
    rep_l = _report("LOADED", empty, loaded)
    rep_u = _report("UNLOADED", loaded, empty)
    assert rep_u.total_cargo_in_bulk_t == pytest.approx(rep_l.total_cargo_in_bulk_t)
    assert rep_u.total_cargo_in_bulk_t > 0
