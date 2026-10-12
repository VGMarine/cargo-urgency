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
    assert draughts.arithmetic_mean_draught(8.0, 10.0, 9.0) == pytest.approx(9.0)


def test_bad_density_raises():
    with pytest.raises(ValueError):
        density.density_correction(10.0, rho_observed=0.5)
