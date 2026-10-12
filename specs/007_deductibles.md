# Спецификация 007 — DEDUCTIBLES: вычеты, груз на борту, константа судна

## 1. Источник
- Книга / документ: Dibble, «The Draught Survey» (текстовый слой sources/text/dibble.txt)
- Раздел, страница(ы):
  - DEDUCTIBLES — стр. 45 книги (PAGE 46 дампа, строка 1456; книжная нумерация напечатана в конце страницы);
  - ANCHORS AND CABLES — стр. 43 книги (PAGE 51 дампа, строки 1662–1680);
  - LIGHTSHIP / Growth of lightship / Lightship Constant — стр. 14–15 книги (PAGE 22–23 дампа, строки 661–706);
  - ADDITIONAL FACTORS п.3 (swimming pool) — стр. 52 книги (дамп строка 1697);
  - SUMMARY OF DEDUCTIBLES — форма «D» UN/ECE (PAGE 70 дампа, строки 2708–2723);
  - Форма «E» UN/ECE (PAGE 71 дампа) — Difference in Displacement = TOTAL CARGO IN BULK;
  - Перекрёстный источник: Britannia Loss Prevention Guidance (sources/text/guidance.txt, раздел CONSTANT).
- Файл оригинала: sources/originals/dibble.pdf (LFS-указатель; точечные неоднозначности — TODO(scan))
- Версия/издание, язык: англ., OCR-дампы сверялись перекрёстно

## 2. Формула (как напечатано, цитаты)

DEDUCTIBLES (стр. 45):
> "The deductibles are the components of the ship's total weight, which must be deducted from the calculated displacement in order to determine the weight of cargo on board."

Состав полного веса (там же, список): Light displacement (remember: components may be missing e.g., anchors out); Cargo; Ballast; Fuel and fresh water; Swimming pool water and other easily forgotten weights on board; Stores and Provisions; Crew and effects. Плюс оговорка: stores/provisions/crew обычно постоянны между замерами и могут быть отнесены к light displacement (т.е. жить в константе).

ANCHORS AND CABLES (стр. 43):
> "The loss of weight due to its removal is weight taken from the light displacement, this amount should therefore be added to the quantity of cargo."

Формула цепи (стр. 43, пословная запись дампа):
```
Weight per shackle (tonne) = 15 x (link diameter in cm)^2 x 3.87 / 1000
```
Там же: вес самого якоря берётся со справочных данных судна и округляется до ближайшей половины тонны ("This anchor weight should be rounded to the nearest half tonne").

LIGHTSHIP (стр. 14): lightship включает корпус со снабжением, запасами машинного отделения, воду в котлах до рабочего уровня и смазочное масло в машинах; НЕ включает персонал, груз, топливо, провизию и воду.
Growth of lightship: ~0.2% лёгкого водоизмещения в год; учтён в lightship constant.
Lightship Constant (стр. 14–15): расчётный лёгкий вес отличается от табличного — эта разница и есть константа; она НЕ постоянна, служит гидом по согласованности результатов.

Переписанные формы (реализация src/deductibles.py):
```
Cargo = Corrected Disp − Light Disp − ΣDeductibles + Anchor&Cable(outboard)
ΣDeductibles = ballast + fw + fo + do + slops + lube + pool + others   (без Anchor&Chain!)
Corrected light disp = Corrected Disp − Cargo − ΣDeductibles + Anchor&Cable(outboard)
Constant = Corrected light displacement − Lightship (tabular)
W_shackle [t] = 0.05805 * d_cm^2 ;  W_cable [t] = W_shackle * N_shackles
```

## 3. Переменные и единицы
| Символ | Смысл | Единица | Источник значения | Примечания |
|--------|-------|---------|-------------------|------------|
| Corrected Disp | исправленное водоизмещение | т | spec 006 (цепочка ASSESSMENT SUMMARY) | для замера «before»/«after» — две величины |
| Light Disp | лёгкое водоизмещение (фактическое) | т | расчёт из Corrected Disp минус всё остальное | включает conстанту |
| ΣDeductibles | сумма вычетов | т | замеры танков (soundings/ullages, стр. 45–47) | Anchor & Chain в сумму НЕ входит |
| Anchor&Cable(out) | вес якорей/цепи на грунте | т | формула цепи + данные якоря с окр. до 0.5 т | ПРИБАВКА к грузу (стр. 43) |
| d | диаметр прутка звена цепи | см | чертежи/свидетельства | |
| N shackles | число шаклов вынесенной цепи | шт | запись цепемётной машины | 1 шакл = 15 фатомов ≈ 27.43 м |
| Constant | lightship constant | т | Corrected light − tabular lightship | меняется от замера к замеру |

## 4. Порядок вычислений (шаги)
1. Получить Corrected Displacement по цепочке spec 006 (+/− знаки — по CORRECTIONS CHECK LIST, spec 004).
2. Измерить содержимое всех танков (sounding/ullage → объём по таблицам × плотность с температурной поправкой для бункеров; для балласта темп. поправка не применяется — стр. 47). Массы занести в SUMMARY OF DEDUCTIBLES (форма «D»).
3. Якоря/цепь, вынесенные за борт: посчитать по формуле стр. 43; это НЕ вычет — прибавить к грузу (знак «+» в шаге 4).
4. Cargo = Corrected Disp − Light Disp − ΣDeductibles + Anchor&Cable(out).
5. Для контроля константы: Corrected light disp = Corrected Disp − Cargo − ΣDeductibles + Anchor&Cable(out); Constant = Corrected light − табличный Lightship; сравнить с заявленной константой и средним предыдущих (форма «E», guidance Britannia).

## 5. Контрольный пример из книги
Числового примера с ответом в главе DEDUCTIBLES НЕТ (проверено grep'ом по дампу — после формулы цепи пример отсутствует). Поэтому контроль algebraic:
- Вход: Corrected Disp=15000, Light=5000, deductibles {ballast 1000, fo 200, others 50}, anchor out=35.
- Cargo = 15000−5000−1250+35 = 8785.0 т; инверсия даёт Corrected light = 6250.0 т (test_form_e_inversion_consistency).
- Цепь: d=2.7 см → W_shackle = 0.05805×2.7² = 0.423 t/cm²·см²→ pytest.approx; коэффициент CHAIN_BOOK_COEFF=0.05805 (test_chain_weight_is_literal_book_formula).
Допуск округления: точная арифметика float, abs_tol=1e-9; физического контроля формулы цепи нет — только sanity-тест порядка величины (0.0169…0.058 t/см²).

## 6. Неоднозначности и особые случаи
- Знак Anchor & Chain: в форме «D» он стоит в списке Deductibles, но книга (стр. 43) явно говорит «added to the quantity of cargo». Реализовано по тексту книги (прибавка), расхождение с формой «D» зафиксировано в docstring и тесте test_deductibles_total_excludes_anchor_chain. TODO(scan): посмотреть, как заполнена форма в печатном примере книги (если есть).
- Множитель формулы цепи: пословная читка дампа даёт 15×d²×3.87/1000 = 0.05805·d²; независимая физическая оценка прямой длины шакла ≈0.0169·d² (сталь 7.85, 27.43 м). Расхождение ×3.4 объяснимо геометрией звена (~×2.26) + шаклы/коуши/запас, но без скана точный коэффициент не устанавливается. TODO(scan): десятичные разделители «3.87» и «/1000» на стр. 43.
- Округление веса якоря до 0.5 т — в модуль не внесено (это процедура записи, не формула); зафиксировано здесь.
- «Stores/provisions/crew → добавить к light displacement» — альтернативный учёт; при таком выборе их надо НЕ включать в ΣDeductibles, иначе двойной счёт. Особый случай помечен в docstring Deductibles.others.

## 7. Статус
- [x] Сверено с оригиналом постранично (текстовый слой; цитаты выше)
- [x] Реализовано в src/deductibles.py
- [x] Тест проходит (tests/test_draft_modules.py, 4 теста spec 007; всего 31 passed)
- Открытые TODO(scan): множитель формулы цепи; трактовка Anchor&Chain в форме «D»; возможный печатный пример заполнения форм.
