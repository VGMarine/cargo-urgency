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


def displacement_density_correction_t(displacement_tabulated_t: float,
                                      rho_observed: float,
                                      rho_table: float) -> float:
    """Поправка ПЛОТНОСТИ применяется к ВОДОИЗМЕЩЕНИЮ, не к осадке.

    Сверено с оригиналом: Dibble, стр. 33 книги (PDF index 41):
      Actual displacement = tabulated displacement x density1 / density2,
      где density1 — средняя плотность пробы, density2 — плотность гидростатики.
    И правило №3/№4 (стр. 36 книги, PDF index 44): "Do not adjust the draught
    for the density, but do correct the displacement instead" и "enter the
    hydrostatic tables with the actual TMD, irrespective of density".
    Контрольный пример QUESTION 9 (стр. 36 книги, PDF index 44):
      15250 x 1.015 / 1.025 = 15101.2 t (OCR "15)01.2" -> консолидировано:
      арифметика даёт ровно 15101.219..., печать книги 15101.2).
    """
    if not (0.98 <= rho_observed <= 1.03):
        raise ValueError(f"подозрительная наблюдаемая плотность {rho_observed}")
    if not (0.98 <= rho_table <= 1.03):
        raise ValueError(f"подозрительная табличная плотность {rho_table}")
    return displacement_tabulated_t * rho_observed / rho_table
