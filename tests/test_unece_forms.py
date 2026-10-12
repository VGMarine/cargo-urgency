"""Тесты машиночитаемой модели форм A–E (src/unece_forms.py).

Сверка цепочки вычислений формы «C» кодекса UN/ECE 1992 против контрольных
чисел книги Dibble (те же данные, что в tests/test_book_verified_examples.py
и tests/test_unece_annex_a.py): Q3 (perpendiculars), Q5 (mean of means =
Fuller), Q9 (плотность 15101.2 t), форма E (Difference = cargo).
"""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from unece_forms import (  # noqa: E402
    DraughtReadings,
    ShipHydroStatics,
    SurveyMeta,
    SurveyReport,
)


def _readings(**kw) -> DraughtReadings:
    base = dict(
        d_forward_port=6.35, d_forward_stbd=6.35,
        d_after_port=7.88, d_after_stbd=7.90,
        d_midship_port=7.10, d_midship_stbd=7.12,
        observed_density=1015.0, tables_density=1025.0,
        displacement_tables=15250.0,
    )
    base.update(kw)
    return DraughtReadings(**base)


class TestQ3Perpendiculars:
    """Dibble Q3: stem/stern corrections −0.017/+0.057 → 6.333/7.937 м."""

    def test_corrected_draughts(self):
        d = _readings(stem_correction_fp=-0.017, stern_correction_ap=0.057)
        assert round(d.d_forward_corrected, 3) == pytest.approx(6.333, abs=5e-4)
        # Книга печатает 7.937 при AP mean 7.88? — нет: port/stbd 7.88/7.90 →
        # mean 7.89 + 0.057 = 7.947; печать 7.937 соответствует mean 7.88
        # (одностороннее чтение). Проверяем оба варианта согласованности формулы:
        d2 = _readings(d_after_port=7.88, d_after_stbd=7.88,
                       stem_correction_fp=-0.017, stern_correction_ap=0.057)
        assert round(d2.d_after_corrected, 3) == pytest.approx(7.937, abs=5e-4)

    def test_trim_sign_convention(self):
        """Форма C: Trim fwd(−) aft(+); trim by aft положительный."""
        d = _readings(stem_correction_fp=-0.017, stern_correction_ap=0.057)
        assert d.trim_m > 0  # trim by aft


class TestQ5MeanOfMeans:
    """Dibble Q5: mean-of-means кодекса тождественна Fuller 6/8 при нулевом midship corr."""

    def test_mean_of_means_equals_fuller_at_even_keel(self):
        """Тождество MoM == Fuller верно при нулевом триме (FA == MC)."""
        d = _readings(d_forward_port=7.0, d_forward_stbd=7.0,
                      d_after_port=7.0, d_after_stbd=7.0,
                      d_midship_port=7.0, d_midship_stbd=7.0)
        assert d.trim_m == 0.0
        fuller = (d.d_forward_corrected + d.d_after_corrected + 6 * d.d_midship_mean) / 8
        assert d.mean_of_means == pytest.approx(fuller, abs=1e-12)

    def test_mean_of_means_differs_from_fuller_with_trim(self):
        """При триме MoM != Fuller — это разные методы (см. specs/003b)."""
        d = _readings()
        fuller = (d.d_forward_corrected + d.d_after_corrected + 6 * d.d_midship_mean) / 8
        assert d.mean_of_means != pytest.approx(fuller, abs=1e-6)

    def test_sag_hog_and_keel(self):
        """Sag (+) Hog (−) по форме C; keel thickness вычитается (moulded)."""
        d = _readings(sag_hog_m=0.05, keel_thickness_m=0.10)
        expected = d.mean_of_means + 0.05 - 0.10
        assert d.draught_moulded_corrected == pytest.approx(expected)


class TestQ9Density:
    """Dibble Q9: 15250 × 1.015/1.025 = 15101.2 t (цепочка формы C)."""

    def test_density_chain(self):
        d = _readings()
        assert d.displacement_corrected_for_density == pytest.approx(15101.22, abs=0.05)
        assert round(d.displacement_corrected_for_density, 1) == pytest.approx(15101.2, abs=0.05)

    def test_deductibles_subtracted_last(self):
        d = _readings(total_deductibles_t=500.0)
        assert d.displacement_net == pytest.approx(
            d.displacement_corrected_for_density - 500.0
        )


class TestFormValidation:
    def test_extra_field_forbidden(self):
        with pytest.raises(ValidationError):
            DraughtReadings(nonexistent_field=1.0)

    def test_line_aliases_populate(self):
        """Номера линий бланка C работают как alias (line numbers Section B)."""
        d = DraughtReadings.model_validate(dict(
            line013=6.35, line021=6.35, line033=7.88, line041=7.90,
            line073=7.10, line081=7.12,
            observed_density=1015, tables_density=1025, displacement_tables=15250,
        ))
        assert d.d_forward_port == 6.35 and d.d_after_stbd == 7.90

    def test_negative_density_rejected(self):
        with pytest.raises(ValidationError):
            _readings(observed_density=-1015)


class TestFormESummary:
    """Форма E: Difference между скорректированными водоизмещениями = cargo."""

    def _report(self, survey_type="LOADED"):
        meta = SurveyMeta(
            survey_type=survey_type,
            corporate_identification="ABC Surveyors",
            office_of_surveyor="Port X",
            vessel="MV TEST", call_letters="LAAA", survey_no="1",
            registry="PAN", built_year=2010, built_by="Yard", flag="PA",
            port="Port X",
        )
        ship = ShipHydroStatics(
            lbp_m=170.0, tpc=25.0, lcf_m=2.0,
            mctc_plus50=310.0, mctc_minus50=322.9,
        )
        start = _readings(displacement_tables=25250.0, total_deductibles_t=1000.0)
        finish = _readings(displacement_tables=15250.0, total_deductibles_t=1000.0)
        return SurveyReport(meta=meta, ship=ship, starting=start, finishing=finish)

    def test_loaded_difference_positive(self):
        r = self._report("LOADED")
        # для LOADED ожидаем finishing > starting — разворачиваем данные
        r.starting, r.finishing = r.finishing, r.starting
        cargo = r.total_cargo_in_bulk_t
        assert cargo == pytest.approx(
            r.finishing.displacement_net - r.starting.displacement_net
        )
        assert cargo > 0

    def test_unloaded_flips_order(self):
        r = self._report("UNLOADED")
        assert r.total_cargo_in_bulk_t > 0
        # для UNLOADED starting > finishing
        assert r.starting.displacement_net > r.finishing.displacement_net
