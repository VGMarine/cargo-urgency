"""Поправки ареометра и плотность (Dibble, стр. 33 книги + Appendix «Alternative Hydrometers», стр. 53).

Сверено с дампом текстового слоя: sources/dumps/dibble/page_041.txt (DENSITY,
CORRECTION FOR DENSITY) и page_061.txt (ALTERNATIVE HYDROMETERS):
  True Density (in vacuo)        -> apparent density = true - 0.0011 g/ml
  RD (15°C/4°C)                  -> apparent density = RD - 0.0011
  RD (15°C/15°C)                 -> apparent density = RD - 0.002
Примечание книги: g/ml = kg/l = t/m3.
Поправка водоизмещения за плотность (стр. 33):
  Actual displacement = tabulated displacement x density1 / density2
  (density1 — проба забортной воды; density2 — плотность гидростатических таблиц).
"""
from __future__ import annotations

# Константы по книге (стр. 53):
TRUE_DENSITY_OFFSET = 0.0011   # вычитается из истинной плотности (vacuo)
RD_15_4_OFFSET = 0.0011        # вычитается из RD(15°C/4°C)
RD_15_15_OFFSET = 0.002        # вычитается из RD(15°C/15°C)


def apparent_density(scale_value: float, scale: str) -> float:
    """Перевести показание нестандартного ареометра в apparent density (г/мл).

    scale: "true" | "rd_15_4" | "rd_15_15" | "apparent" (без поправки).
    """
    s = scale.lower()
    if s == "true":
        return scale_value - TRUE_DENSITY_OFFSET
    if s in ("rd_15_4", "rd15/4"):
        return scale_value - RD_15_4_OFFSET
    if s in ("rd_15_15", "rd15/15"):
        return scale_value - RD_15_15_OFFSET
    if s == "apparent":
        return scale_value
    raise ValueError(f"неизвестная шкала ареометра: {scale}")


def displacement_for_density(tabulated_t: float, rho_sample: float,
                              rho_tables: float) -> float:
    """Фактическое водоизмещение = табличное × ρ1/ρ2 (книга, стр. 33)."""
    if rho_tables <= 0:
        raise ValueError("rho_tables должен быть > 0")
    return tabulated_t * rho_sample / rho_tables
