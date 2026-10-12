"""Средняя осадка AMD (spec 003). Черновик: Dibble, стр. 18."""
from __future__ import annotations


def arithmetic_mean_draught(d_fwd: float, d_aft: float, d_mid: float) -> float:
    """AMD = (dF + dA + 6*dM) / 8 — весовая схема Simpson 1-6-1."""
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
    """A.M.D., fuller-form vessel (книга, Q6, стр. 29-30): (DF+DA)/2."""
    return (d_fwd + d_aft) / 2.0


def mad_from_factor(amd: float, d_mid: float, factor: float) -> float:
    """Method 3 (книга, стр. 29-30): MAD = AMD + factor*(DM - AMD).

    factor считывается из графика по коэффициенте полноты ватерлинии
    (Cw): для Cw=0.60 книга даёт factor=0.76 (Q6).
    """
    return amd + factor * (d_mid - amd)
