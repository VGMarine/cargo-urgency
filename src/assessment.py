"""Сквозная цепочка ASSESSMENT SUMMARY (spec 006, книга стр. 45 и 51).

Цитата CORRECTIONS CHECK LIST (стр. 51 книги, PDF index 59), по порядку:
    OBSERVED DRAUGHTS (P&S fwd/aft/mid) -> mean values at centreline
    Correct from marks to perpendicular and midships positions
        (misplacement opposite to trim -> (+); same as trim -> (-))
    Hog/sag correction (mean of mean of means, or similar)
        (negative for hog; positive for sag)   [в книге это часть шага "to
        enter hydrostatic tables" — см. метод 2, стр. 36]
    CORRECTED MEAN DRAUGHT ... to enter hydrostatic tables
    Displacement from displacement table
    First trim correction (tonnes): LCF same as trim -> (+), opposite -> (-)
    Second trim correction (tonnes): always (+)
    List correction (tonnes): always (+)
    Correction for density: less than salt water density -> (-)
    CORRECTED DISPLACEMENT

Примечание метода (стр. 45): часть попрак лучше считать в тоннах, а не в
метрах — тоннажные поправки применяются к водоизмещению из гидростатики.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AssessmentInputs:
    # --- осадки у марок (средние P&S, метры) ---
    d_fwd_mark: float
    d_aft_mark: float
    lbp_m: float
    # misplacement marks -> perpendiculars (метры, неотрицательные как в книге)
    dist_fp_to_df_m: float = 0.0
    dist_ap_to_da_m: float = 0.0
    # --- прогиб (метод 3 alternative 1, стр. 30) или None ---
    deflection_factor: float | None = None
    d_mid_corrected: float | None = None
    # --- гидростатика на MAD ---
    tpc: float = 0.0
    mctc1: float | None = None   # MCTC на MAD
    mctc2: float | None = None   # MCTC на MAD + 50 cm
    disp_at_mad_t: float = 0.0   # водоизмещение из таблицы на MAD
    # --- дифферент / LCF / крен / плотность ---
    lcf_fwd_of_mid_m: float = 0.0   # знак: + = LCF forward of midships
    trim_by_stern_m: float = 0.0    # знак: + = by the stern
    list_corr_t: float = 0.0        # уже вычисленная (+) поправка на крен
    rho_observed: float = 1.025
    rho_table: float = 1.025


@dataclass
class AssessmentResult:
    d_fwd_perp: float
    d_aft_perp: float
    amd: float
    mad: float
    corr_1st_trim_t: float
    corr_2nd_trim_t: float
    corr_list_t: float
    corr_density_t: float
    deflection_corr_t: float
    corrected_displacement_t: float


def corrected_displacement(i: AssessmentInputs) -> AssessmentResult:
    """Полный проход чек-листа стр. 51. Все тоннажные поправки — со своим знаком."""
    from draughts import arithmetic_mean_draught, deflection_correction_t
    from perpendiculars import perpendicular_corrections, trim_of
    from trim import first_trim_correction_t_sign, second_trim_correction_t

    cf, ca = perpendicular_corrections(
        i.d_fwd_mark, i.d_aft_mark, i.lbp_m,
        i.dist_fp_to_df_m, i.dist_ap_to_da_m)
    d_fp = i.d_fwd_mark + cf
    d_ap = i.d_aft_mark + ca
    amd = arithmetic_mean_draught(d_fp, d_ap)

    # hog/sag (поправка на прогиб) — в тоннах, знак формулы сам (hog -, sag +)
    defl_t = 0.0
    if i.deflection_factor is not None and i.d_mid_corrected is not None:
        defl_t = deflection_correction_t(i.d_mid_corrected, amd,
                                         i.deflection_factor, i.tpc)

    # в цепочке "тоннами" MAD остаётся табличной точкой входа (AMD),
    # прогиб применяется тоннажной поправкой (предпочтение стр. 45)
    mad = amd

    trim = trim_of(i.d_fwd_mark, i.d_aft_mark)
    c1 = first_trim_correction_t_sign(i.lcf_fwd_of_mid_m, trim, i.lbp_m, i.tpc)
    c2 = 0.0
    if i.mctc1 is not None and i.mctc2 is not None:
        c2 = second_trim_correction_t(abs(trim), i.mctc2, i.mctc1, i.lbp_m)

    disp = i.disp_at_mad_t + c1 + c2 + i.list_corr_t + defl_t
    cd = disp * i.rho_observed / i.rho_table - disp  # поправка плотности в тоннах
    return AssessmentResult(
        d_fwd_perp=d_fp, d_aft_perp=d_ap, amd=amd, mad=mad,
        corr_1st_trim_t=c1, corr_2nd_trim_t=c2, corr_list_t=i.list_corr_t,
        corr_density_t=cd, deflection_corr_t=defl_t,
        corrected_displacement_t=disp + cd)
