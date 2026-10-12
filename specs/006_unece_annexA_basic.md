# 006 — Annex «A» кодекса UN/ECE: программа BASIC (Sharp PC-1248)

## 1. Источник
- Документ: ECE/ENERGY/19 (1992), Annex "A" — Automatic Calculation Program
  Connected with the Draught Survey, печатные стр. 110–119 (PDF index 119–129).
- Файл оригинала: `sources/originals/survey-book/E_ECE_ENERGY_19.pdf`
  (sha256 `3153fb77…ac065e8`). Текст извлечён OCR → `sources/text/unece1992_ocr.txt`.
- Издание программы в тексте кодекса: "DRAUGHT SURVEY ed. October 1991 - 1.8"
  (строка 70 листинга).

## 2. Алгоритм (раздел 2 документа, OCR-цитаты формул)
Точка C — средние по бортам (line 131/147/138):
```
FORE = (FP + FS)/2   MID = (MP + MS)/2   AFT = (AP + AS)/2
```
Точка D — поправки на перпендикуляры (Lf/La/Lm — расстояния меток от pp;
LBD = LBP − La + Lf в записи источника, в коде знаменатель `(LBP-P)` где
`P=ABS(LF+LA)`, line 133/140/148):
```
STEM correction  = Lf * (FORE - AFT)/(LBP-P)
STERN correction = La * (AFT - FORE)/(LBP-P)
MIDSHIP corr     = Lm * (AFT - FORE)/(LBP-P)
```
Знаки задаются флагами STEMS/STERNS/MIDS (aft=1, fwd=−1); правило знаков —
цитата spec 002/004 (trimmed by stern: FORE −, AFT +; MID зависит от стороны).

Точки G–H (line 134/141/149): `FC=FORE+STEMCO`, `AC=AFT+STERNCO`, `MC=MID+MIDCO`.

Точка H — hog/sag, «mean of means» (line 143/151/152):
```
FA   = (FC + AC)/2
MM   = (FA + MC)/2
DHSC = (MM + MC)/2      # draught extreme corrected for hog or sag
MMCO = DHSC - KE        # минус толщина киля → применимая осадка для таблиц
```
⚠️ Это метод 2(i)-подобная схема (веса через двойное усреднение), НЕ Fullersley;
сверено с AMD/MAD из Dibble (specs 003/003b) — согласуется: DHSC=(DF'+DA'+6·DM')/8?
Нет: (FA+MC)/2 затем (MM+MC)/2 даёт веса FC,AC по 1/8 и MC по 6/8 — да, это
и есть Fuller 6/8 midship при FC/AC как DF/DA. Зафиксировать в тестах.

Точка I — истинный дифферент: `AR = ABS((AC - FC)*100)` (см, line 155).

Точка L — first trim correction (line 162):
```
CO1 = AR * LCF * TPC * 100 / LBP    # знак "+": LCF и trim по одну сторону миделя
```
(в коде: `CO1=ABS(AR*TPC*LCF/LBP)*S2*LCFS`; ⚠️ OCR строки 30240 читается
`IF AC<FC THEN S2=1 ELSE S2=1` — явный артефакт скана, один флаг потерян;
при реализации вывести из правила знаков spec 004 и закрыть тестом.)

Точка M — second trim correction (line 163):
```
DMDZ = MTC1 - MTC2      # MTC1 при mean+50cm, MTC2 при mean−50cm
CO2  = AR^2 * 50 * DMDZ / LBP     # знак всегда "+"
```
(в дюймовом режиме — отдельные ветки line 30290/30300.)

Точки N–Q:
```
DCO    = DISPL + CO1 + CO2                     (line 166)
SD     = DCO*(OD/TD − 1);  DISDEN = DCO + SD   (line 167/168)
DISPLNT = DISDEN − (BA+FW+FO+DO+LO+SL+SP+AC+MIS) (line 169/170)
```

## 3. Листинг BASIC
Полный листинг (секции 10…, 10000 INPUT, 20000 REVIEW, 30000 CALC, 40000
PRINT, 50000 LPRINT) находится в `sources/text/unece1992_ocr.txt`, PDF index
125–128. OCR номерной колонки местами шумен (строки без номеров слиты) —
для переноса листинга дословно нужен кроп-ререндер этих страниц в 300 dpi.

## 4. Статус
- [x] Annex A полностью оцифрован OCR; алгоритм §2 восстановлен и сверен с
      формулами specs 002/003/003b/004 (знаки, mean-of-means = Fuller 6/8).
- [ ] Реализация `src/unece_annex_a.py` (порт алгоритма §2 на Python) + тесты
      против контрольных чисел Dibble Q3/Q5/Q7/Q8/Q9 — следующая задача.
- [ ] Дословный листинг BASIC — требует high-res кропа стр. 116–118.

СВЕРЕНО с оригиналом (OCR; sha256 источника зафиксирован).
