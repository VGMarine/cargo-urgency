"""Машиночитаемая модель отчёта дорафт-сёрвея по формам «A»–«E» кодекса UN/ECE 1992.

Источник: ECE/ENERGY/19 (January 1992), Part 1, Forms A–E (PDF index 13–19),
OCR-расшифровка `sources/text/unece1992_ocr.txt` (sha256 оригинала зафиксирован
в specs/007_unece_forms_A-E.md §1). спецификация: specs/007 (UNECE forms), §4 — перенос в
машиночитаемый формат (pydantic-модель отчёта).

Конвенции знаков строго по кодексу:
- Distance marks: «forward - aft +» (Form B, PDF index 14) — смещение метки к
  корме относительно перпендикуляра даёт положительное число;
- Trim: «fwd (-) aft (+)» (Form C, PDF index 15);
- Hog/Sag: «Sag (+) Hog (-)» (Form C, PDF index 15).

Поля названы по строкам формы C с номерами линий из левого поля бланков
(line numbers «соответствуют нумерации строк вычислений», Section B, PDF
index 26) и совпадают с идентификаторами порта Annex A BASIC
(src/unece_annex_a.py): DF/D_MID/DA, STEMCO/STERNCO/MIDCO, DHSC, TRIM, OD,
DCO, AR/LCFTPC/TMTR (1st trim), DMDZ (2nd trim), DED (deductibles), DISPLNT.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class SurveyMeta(BaseModel):
    """Форма «A» (PDF index 13): титульные данные отчёта и условия съёмки."""

    model_config = ConfigDict(extra="forbid")

    survey_type: Literal["LOADED", "UNLOADED"]
    corporate_identification: str
    office_of_surveyor: str
    vessel: str = Field(description="MV name")
    call_letters: str
    survey_no: str
    registry: str
    built_year: int
    built_by: str
    flag: str
    port: str
    # Наблюдаемые условия (Form A): weather temperature, sea condition, heading,
    # direction wind, stream speed km/h, tide, ice — все свободным текстом/числом.
    weather_temperature: Optional[str] = None
    sea_condition: Optional[str] = None
    heading_of_ship: Optional[str] = None
    direction_wind: Optional[str] = None
    stream_speed_kmh: Optional[float] = None
    tide: Optional[str] = None
    ice: Optional[str] = None
    witness_draughts: bool = False
    witness_tank_soundings: bool = False


class ShipHydroStatics(BaseModel):
    """Форма «B» (PDF index 14): размерения и гидро статика судна.

    Значения TPC/LCF/MCTC задаются отдельно для STARTING и FINISHING survey —
    как в бланке (две колонки).
    """

    model_config = ConfigDict(extra="forbid")

    lbp_m: float = Field(gt=0, description="Length between perpendiculars")
    loa_m: Optional[float] = None
    extreme_breadth_m: Optional[float] = None
    moulded_depth_m: Optional[float] = None
    tpc: float = Field(gt=0, description="Tonnes per centimetre immersion")
    lcf_m: float = Field(
        description="Longitudinal centre of flotation; знак по конвенции "
        "гидростатических таблиц (см. spec 004: fwd LCF & aft trim -> 1st TC −)"
    )
    mctc_plus50: float = Field(gt=0, description="Moment to trim 1 cm, +50 cm range")
    mctc_minus50: float = Field(gt=0, description="Moment to trim 1 cm, -50 cm range")
    distance_marks_forward_pp_m: float = Field(
        default=0.0, description="Метка FP относительно форпика; forward −, aft +"
    )
    distance_marks_after_pp_m: float = Field(
        default=0.0, description="Метка AP относительно ахтерпика; forward −, aft +"
    )
    distance_marks_midship_pp_m: float = Field(
        default=0.0, description="Смещение мидель-шпангоута от LBP/2; forward −, aft +"
    )
    vessel_list: Optional[float] = None


class DraughtReadings(BaseModel):
    """Форма «C» (PDF index 15): блок осадок одного сёрвея (STARTING/FINISHING).

    Имена полей = строки формы C с номерами линий (line numbers) из кодекса.
    """

    model_config = ConfigDict(extra="forbid")

    d_forward_port: float = Field(alias="line013", description="Draught forward port")
    d_forward_stbd: float = Field(alias="line021", description="Draught forward stbd")
    d_after_port: float = Field(alias="line033", description="Draught after port")
    d_after_stbd: float = Field(alias="line041", description="Draught after stbd")
    d_midship_port: float = Field(alias="line073", description="Draught midships port")
    d_midship_stbd: float = Field(alias="line081", description="Draught midships stbd")

    stem_correction_fp: float = Field(
        default=0.0, description="Stem correction (misplacement of mark at FP)"
    )
    stern_correction_ap: float = Field(
        default=0.0, description="Stern correction (misplacement of mark at AP)"
    )
    midship_correction: float = Field(
        default=0.0, description="Midship correction (mark vs midship pp)"
    )

    sag_hog_m: float = Field(
        default=0.0, description="Hull deflection: Sag (+), Hog (−) — Form C"
    )
    keel_thickness_m: float = Field(
        default=0.0, ge=0.0, description="Correction (−) for keel thickness, line ~153"
    )

    observed_density: float = Field(gt=0, description="Observed density, kg/m3")
    tables_density: float = Field(
        gt=0, description="Ship's tables density, kg/m3 (Form C 'Ship's tables density')"
    )
    displacement_tables: float = Field(
        gt=0, description="Displacement read from tables at tables_density, tonnes"
    )
    first_trim_correction_t: float = Field(
        default=0.0, description="First trim correction, tonnes (знак по spec 004)"
    )
    second_trim_correction_t: float = Field(
        default=0.0, description="Second trim correction, tonnes (always sign by trim)"
    )
    total_deductibles_t: float = Field(
        default=0.0, ge=0.0, description="Total deductibles (Form D/3 summary)"
    )

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    # ---- производные величины (строки формы C) -------------------------------

    @property
    def d_forward_mean(self) -> float:
        """Draught forward mean."""
        return (self.d_forward_port + self.d_forward_stbd) / 2

    @property
    def d_after_mean(self) -> float:
        """Draught after mean."""
        return (self.d_after_port + self.d_after_stbd) / 2

    @property
    def d_forward_corrected(self) -> float:
        """Draught forward corrected to fore pp."""
        return self.d_forward_mean + self.stem_correction_fp

    @property
    def d_after_corrected(self) -> float:
        """Draught after corrected to after pp."""
        return self.d_after_mean + self.stern_correction_ap

    @property
    def fa_mean(self) -> float:
        """Draught fore & after mean (line ~061)."""
        return (self.d_forward_corrected + self.d_after_corrected) / 2

    @property
    def d_midship_mean(self) -> float:
        return (self.d_midship_port + self.d_midship_stbd) / 2

    @property
    def d_midship_corrected(self) -> float:
        """Draught midship corrected to midship pp (line ~085)."""
        return self.d_midship_mean + self.midship_correction

    @property
    def mean_of_means(self) -> float:
        """Mean of means (line ~101): (FA + MC)/2 — метод hog/sag кодекса."""
        return (self.fa_mean + self.d_midship_corrected) / 2

    @property
    def draught_moulded_corrected(self) -> float:
        """Draught moulded corrected for hog/sag (line 152 или 154, Note формы C).

        Кодекс допускает два варианта ('Utilize line 152 or line 154'):
        152 = mean of means + sag/hog; здесь реализован этот вариант, минус
        толщина киля (moulded поправка).
        """
        return self.mean_of_means + self.sag_hog_m - self.keel_thickness_m

    @property
    def trim_m(self) -> float:
        """Trim: fwd (−) aft (+) — конвенция формы C."""
        return self.d_after_corrected - self.d_forward_corrected

    @property
    def displacement_corrected_for_trim(self) -> float:
        return self.displacement_tables + self.first_trim_correction_t + (
            self.second_trim_correction_t
        )

    @property
    def density_correction_t(self) -> float:
        """Correction for density average (линейная поправка водоизмещения)."""
        return self.displacement_corrected_for_trim * (
            self.observed_density / self.tables_density - 1
        )

    @property
    def displacement_corrected_for_density(self) -> float:
        return self.displacement_corrected_for_trim + self.density_correction_t

    @property
    def displacement_net(self) -> float:
        """Displacement corrected for deductibles (последняя строка формы C)."""
        return self.displacement_corrected_for_density - self.total_deductibles_t


class SurveyReport(BaseModel):
    """Полный отчёт: формы A + B + C(start/finish) + D/3 + E (cargo statement)."""

    model_config = ConfigDict(extra="forbid")

    meta: SurveyMeta
    ship: ShipHydroStatics
    starting: DraughtReadings
    finishing: DraughtReadings

    @property
    def total_cargo_in_bulk_t(self) -> float:
        """Форма «E»: Difference = TOTAL CARGO IN BULK (загрузка).

        Для выгрузки (UNLOADED) знак разности меняется местами; здесь —
        absolute difference как в бланке E ('Starting ... Finishing ...
        Difference'), порядок выбирается вызывающей стороной по survey_type.
        """
        start = self.starting.displacement_net
        finish = self.finishing.displacement_net
        if self.meta.survey_type == "LOADED":
            return finish - start
        return start - finish
