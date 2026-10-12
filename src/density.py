"""Плотность воды и пересчёт осадки (spec 001). Черновик до сверки с оригиналом."""
from __future__ import annotations

RHO_SEAWATER_DEFAULT = 1.025  # т/м^3, ждёт подтверждения по стр. 11–12 книги


def density_correction(draft_m: float, rho_observed: float,
                       rho_target: float = RHO_SEAWATER_DEFAULT) -> float:
    """Осадка в воде плотности rho_target при измеренной draft_m в rho_observed.

    d1 = d0 * (rho0 / rho1) — масса/водоизмещение постоянно, TPC ~ плотность.
    """
    if not (0.99 <= rho_observed <= 1.03):
        raise ValueError(f"подозрительная плотность {rho_observed} т/м3")
    return draft_m * (rho_observed / rho_target)


def dockwater_allowance(dsw_m: float, rho_harbour: float,
                        rho_sea: float = RHO_SEAWATER_DEFAULT) -> float:
    """Приблизительная линейная поправка (dock water allowance):
    corr = dSW * (rho_sea - rho_harbour) / (rho_sea - 1.000)
    Знак: в более лёгкой воде судно сидит глубже на +corr метров.
    """
    return dsw_m * (rho_sea - rho_harbour) / (rho_sea - 1.000)
