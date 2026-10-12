# 005 — Формы «A»–«E» кодекса UN/ECE (1992)

## 1. Источник
- Книга / документ: UN/ECE Code of Uniform Standards and Procedures for the
  Performance of Draught Surveys of Coal Cargoes (ECE/ENERGY/19, January 1992).
- Раздел, страницы: Part 1, Forms «A», «B», «C», «D/1», «D/2», «D/3», «E»
  (PDF index 13–19 = печатные стр. 3–9; Section B — инструкции по заполнению,
  PDF index 26+).
- Файл оригинала: `sources/originals/survey-book/E_ECE_ENERGY_19.pdf`
  (sha256 `3153fb77e140a0895d980373883156e167c2c9f1c2ad58c49f6044051ac065e8`;
  идентичен `1992_UNECE_Draught_Survey_Code_January_1992_E.pdf`).
- Извлечение текста: OCR (tesseract 5.3.0, рендер 200 dpi) →
  `sources/text/unece1992_ocr.txt` (полные 150 стр., 2026-10-12). Текстового
  слоя в PDF нет — все цитаты ниже помечены как OCR-считанные.

## 2. Состав форм (назначение, цитата PDF index 12)
> "The UN/ECE Draught Survey Code Forms "A", "B", "C", "D/1", "D/2", "D/3" and
> "E", constitute the formats for such a report."
Цели форм (OCR): единообразие отчётов; облегчение аудита; совместимость с
любыми инструментами (от карандаша до компьютера); полные данные для баз данных.

| Форма | PDF index | Содержание (по заголовкам OCR) |
|---|---|---|
| A | 13 (стр. 3) | Tитульный лист отчёта: идентификация фирмы/сюрвейера, судно (call letters, registry, built year, flag), кто запросил/на чей счёт, участие master/chief officer/chief engineer, witness draughts/tank soundings, ship's location, weather temperature, sea condition, heading, direction wind, stream speed, tide, ice, cargo handling equipment, missing ship's equipment. Чекбоксы LOADED/UNLOADED. |
| B | 14 (стр. 4) | General remarks: способ получения поправок (calculation/tables) для stem/stern, trim(1), trim(2), liquid corrections; источник hydrostatic tables; степень калибровки танков [yes/no]; range of trim correction tables; размерения (LOA, LBP, extreme breadth, moulded breadth, moulded depth, summer draught/freeboard); константы и lightship (declared/calculated, light displacement, summer DWT, GRT/NRT); для STARTING и FINISHING survey: TPC, LCF, distance marks fwd/aft/mid pp (forward − aft +), MTC +50/−50, vessel list, accessibility of sounding pipes, working order of gauges, legibility of draught marks. |
| C | 15 (стр. 5) | DRAUGHT STATEMENT — основной расчётный лист, строки 001… (левые номера линий): readings port/stbd/mean по носу/корме/миделю, stem/stern/midship correction, corrected to pp, FA, MC, Sag (+) Hog (−), mean of means, draught extreme corrected for hog/sag, keel thickness, draught moulded corrected (line 152 или 154), trim fwd(−) aft(+), observed density, ship's tables density + hydrometer no., displacement, first/second/total trim correction, displacement corr'd for trim, correction for density average, corr'd for density, total deductibles, corr'd for deductibles. Подпись: осадки/плотность/FW/балласт witnessed Chief Officer, FO — Chief Engineer. |
| D/1 | 16 (стр. 6) | SOUNDINGS STARTING SURVEY: A-BALLAST, B-FRESH WATER — tank no., sounding/ullage measured (m), volume corrected for trim/list (m³), density (kg/m³), weight in air (metric tonnes); (*) statement of obstructions in sounding tubes. |
| D/2 | 17 (стр. 7) | То же для FINISHING SURVEY (From Hours To Hours Date Term; два столбца fullage/ullage). |
| D/3 | 18 (стр. 8) | SUMMARY OF DEDUCTIBLES: ballast water, fresh water, fuel oil, diesel oil, slops, lubricating oil, swimming pool water, anchor & chain, others; Total Deductibles, отдельно STARTING/FINISHING (metric tonnes). |
| E | 19 (стр. 9) | CARGO STATEMENT: Starting/Finishing Displacement Corrected, Difference = TOTAL CARGO IN BULK; shore scale quantity; observations; constant block: corrected light displacement − deductables = lightship; constant; mean of previous constants; Constant Certificate endorsement; Bona Fide без-преюдициальная формулировка; подписи сюрвейера и капитана ("have participated in all stages..."). |

## 3. Ключевые правила заполнения (Section B, PDF index 26+, OCR)
- Знак distance marks: «Distance marks forward pp. (forward − aft +)» — т.е.
  положительное значение когда метки смещены к корме относительно FP… (сверка
  со spec 002 при переносе в код).
- Line numbers слева форм A–E соответствуют нумерации строк вычислений
  («the Line Numbers on the left hand border of the sample Forms "A" through "E"»,
  PDF index 26) — используются программой Annex A (см. spec 006).
- Примечание формы C: utilize line 152 or line 154 (draught moulded corrected).

## 4. Статус
- [x] Скан доступен в бинарном виде; OCR выполнен полностью (150 стр.).
- [x] Поля всех форм извлечены и систематизированы (таблица §2).
- [x] Перенос в машиночитаемый формат (JSON/pydantic-модель отчёта) — ЗАКРЫТО
      (2026-10-13): `src/unece_forms.py` — pydantic v2 модели SurveyMeta (форма A),
      ShipHydroStatics (форма B, включая distance marks «forward − aft +»),
      DraughtReadings (форма C: поля с alias по номерам линий бланка, цепочка
      mean→corrected→FA/MC→mean of means→moulded corr (line 152/154 note)→trim
      fwd(−)aft(+)→1st/2nd trim→density→deductibles), SurveyReport (форма E:
      Difference = TOTAL CARGO IN BULK, LOADED/UNLOADED). Формы D/1–D/3 покрыты
      полем total_deductibles_t (сводка) + src/soundings.py (детали танков).
      Тесты `tests/test_unece_forms.py` (12 шт.): Q3 6.333/7.937, тождество
      MoM==Fuller только при нулевом триме (+ зафиксировано различие при триме —
      согласуется с specs/003b), Q9 15101.2 t, порядок вычетов, валидация alias
      и знаков. При сомнении сверять каждое поле с high-res кропом стр. 13–19
      (OCR мелкого типографского текста местами шумен).

СВЕРЕНО с оригиналом (через OCR; sha256 источника зафиксирован в §1).
