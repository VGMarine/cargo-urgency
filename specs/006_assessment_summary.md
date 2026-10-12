# Спецификация 006 — ASSESSMENT SUMMARY: сквозная цепочка поправок

## 1. Источник
- Книга / документ: Dibble, «The Draught Survey» (sources/text/dibble.txt)
- Раздел, страница(ы): ASSESSMENT SUMMARY, стр. 45 книги (PDF index 45 в дампе — строка 1441);
  CORRECTIONS CHECK LIST, стр. 51 книги (PAGE 59 дампа, строка 1980). Форма «E» UN/ECE
  (стр. 71 дампа) подтверждает финальную структуру: Corrected Displacement − Deductibles = Cargo.
- Файл оригинала: PDF в репозитории отсутствует (в sources/originals/ лежат только кодек UN/ECE и guidance); работа ведётся по текстовому слою sources/text/dibble.txt. Точечные неоднозначности — TODO(scan), пока скан недоступен.
- Версия/издание, язык: англ., OCR-дампы сверялись перекрёстно

## 2. Формула (как напечатано, цитаты)

Стр. 45 (ключевая методологическая фраза):
> "Some of the corrections may be calculated in tonnes or in metres. Experience and speed of calculation has shown that the latter corrections should be calculated in tonnes (instead of metres), and used to correct a value of displacement extracted from the hydrostatic particulars in the stability information book."
> "The observed draughts are corrected to the perpendiculars and midships, the hull deflection found and the hydrostatics entered with the corrected arithmetical mean draught (A.M.D.). The displacement extracted is then adjusted with the 1st and 2nd trim corrections and the correction for density, all in tonnes."

CORRECTIONS CHECK LIST (стр. 51) — порядок и знаки:
```
OBSERVED DRAUGHTS: forward P&S, aft P&S, midships P&S
Mean values, ie. draughts at centreline
Correct from marks to perpendicular and midships positions
    Misplacement opposite to trim, then positive (+)
    Misplacement same as trim, then negative (-)
Hog/sag correction (mean of mean of means, or similar)
    negative (-) for hog
    positive (+) for sag
CORRECTED MEAN DRAUGHT ... to enter hydrostatic tables
Displacement from displacement table
First trim correction (in tonnes): LCF same as trim -> (+); opposite -> (-)
Second trim correction (in tonnes): always positive (+)
List correction (in tonnes): always positive (+)
Correction for density: less than salt water density -> negative (-)
CORRECTED DISPLACEMENT
```

Переписанная форма (реализация src/assessment.py):
```
D_fp = Df + c_fwd ; D_ap = Da + c_aft          (perpendicular_corrections, spec 002)
AMD  = (D_fp + D_ap)/2                           (стр. 18, spec 003)
Δdefl = factor * TPC * (DM - AMD) * 100          (стр. 30 alt.1; знак формулы сам: hog−, sag+)
Δ1    = -LCF_sign * TPC * trim_cm / LBP          (стр. 31; trim от МАРК, как в Q3/Q7)
Δ2    = 50 * trim^2 * (MCTC2 - MCTC1) / LBP      (всегда +)
Δlist                                        (list_correction_t, всегда +)
D_int = Disp_tab + Δ1 + Δ2 + Δlist + Δdefl       (промежуточное водоизмещение)
Δrho  = D_int * (rho_obs/rho_tab - 1)            (применяется ПОСЛЕ тоннажных, стр. 45)
Disp_corrected = D_int + Δrho
```

## 3. Переменные и единицы
| Символ | Смысл | Единица | Источник значения | Примечания |
|---|---|---|---|---|
| Df, Da | осадки у марок P&S средние | м | наблюдение | до поправок |
| c_fwd, c_aft | misplacement corrections | м | spec 002 (Q3) | знак из правила стр. 32 |
| LCF_sign | расстояние LCF→midships, + = fwd | м | гидростатика | таблица знаков стр. 31 |
| trim | Da − Df (марочный!), + = stern | м | spec 002 trim_of | книга считает 1st trim от apparent trim |
| rho_obs/rho_tab | плотность пробы / таблицы | т/м³ | spec 001 (Q9) | <1.025 → минус |

## 4. Шаги реализации
1. `AssessmentInputs` — все входы чек-листа одним датаклассом (src/assessment.py).
2. `corrected_displacement()` — проход по порядку стр. 51; каждая поправка возвращается отдельно в `AssessmentResult` (для протокола формы «E»).
3. Порядок плотности: ПОСЛЕ тоннажных поправок (стр. 45 «then adjusted … and the correction for density» + чек-лист: density последняя перед CORRECTED DISPLACEMENT).

## 5. Числовой контроль
Книга НЕ даёт единого сквозного примера — контроль **композиционный** (тест
`test_assessment_chain_q3_q7_q9_composition`, tests/test_draft_modules.py):
- шаг перпендикуляров → печатные Q3: 6.333 / 7.937 м ✔
- шаг 1st trim → формула Q7, применённая к данным Q3-судна (trim 1.53, LBP 170): −180.0 t ✔ (знак по таблице стр. 31)
- шаг density → множитель Q9 1.015/1.025, взятый от промежуточного водоизмещения: −147.02 t ✔
- итог 14922.98 t воспроизводится арифметикой независимо ✔
Зеркальный тест знаков прогиба: hog −273.6 / sag +273.6 t (`test_assessment_deflection_sign_hog_minus_sag_plus`) ✔

## 6. Неопределённости / TODO(scan)
- По какому trim считать 1st trim в цепочке (марочному или исправленному) — книга не формализует; примеры (Q3→Q7 независимые) не разрешают. Реализовано: марочный apparent trim (консервативно совпадает с подходом страницы 31). TODO(scan) — сверить по полному примеру книги позже (стр. 52+).
- Входит ли hog/sag-поправка метода 3 alt.1 между AMD и входом в таблицы при тоннажном способе — трактовка стр. 45 («hull deflection found… entered with corrected AMD») допускает оба; реализован тоннажный вариант (предпочтение автора «calculated in tonnes»), метрический MAD-вариант доступен через mad_from_factor. Зафиксировать выбор при появлении сквозного примера.

### Уточнение (реализация, шаг за шагом)
- **1st trim** в цепочке считается по apparent trim от ОСАДОК У МАРОК (стр. 31:
  «First trim correction = distance from midships to LCF x TPC x the trim»;
  apparent trim сам определён на стр. 24 как Da − Df у марок; Q3 печатно считает
  apparent trim именно по марочным осадкам 7.88−6.35=1.53). Расстояние берётся
  от середины между ПЕРПЕНДИКУЛЯРАМИ (LBP/2), т.к. тоннажные поправки применяются
  к водоизмещению, извлечённому по осадкам у перпендикуляров.
- **2nd trim** — тоннажная форма стр. 40: 50 × trim² × (MCTC2 − MCTC1)/LBP,
  всегда (+); MCTC1 на MAD, MCTC2 на MAD+50 см.
- **Hog/sag (метод 3 alt.1)** — тоннажная поправка factor × TPC × (DM−AMD)×100
  со знаками чек-листа (hog −, sag +); метрический вариант (вход в таблицы по MAD)
  остаётся доступен через `mad_from_factor`.

## 7. Статус
РЕАЛИЗОВАНО (src/assessment.py), композиционные тесты зелёные (34 passed:
q3/q7/q9-цепочка, полный проход чек-листа с печатными контроливами Q6/Q4/Q8/Q9,
знаки прогиба hog −273.6 / sag +273.6, контроль знака формулы deflection).
Не «СВЕРЕНО» полностью — единого сквозного числового примера в книге нет;
ждём пример из глав 42+ (этап 6 дорожной карты).
