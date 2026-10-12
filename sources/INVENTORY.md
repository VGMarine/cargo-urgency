# Инвентарь источников (sources/originals/)

Дата проверки: 2026-10-12. Файлы клонированы из git@github.com:VGMarine/cargo-urgency.git (LFS-smudge выполнен).

## 1. pdfcoffee.com_draught-survey-a-guide-to-good-practice-pdf-free.pdf
- Книга: W.J. Dibble, "Draught Surveys — A Guide to Good Practice" (Loss Prevention Guide)
- Страниц: 71; текст извлекается (OCR уже внутри PDF), но с типичными OCR-шумами ("sun'ey", "iorwanl") — цифры и индексы сверять по скану.
- Ключевые страницы для этапа 1:
  - 11–12: плотность воды, поправки осадок (сжатие корпуса), порядок вычислений
  - 18: Arithmetic Mean Draught (AMD)
  - 29–34: CORRECTION OF DRAUGHTS TO PERPENDICULARS AND MIDSHIPS + числовые примеры (стр. 33: Tan 22° × 4.121 = 1.665 м; стр. 34: Trim aft to midships = 1.0 m)
  - 37–41: QUESTION 5/7/8 — контрольные числовые примеры (идеальны для тестов)
  - 45: ASSESSMENT SUMMARY (сводка поправок)
  - 58–59: INFORMATION / CORRECTIONS CHECK LIST (прообраз форм)
- sha256: 6daa238c612825bfd0b5493040b7ec03edc93e9a7e60b176b666e6113bf80467

## 2. E_ECE_ENERGY_19.pdf
- UNECE ECE/ENERGY/19 (статистический документ по энергетике) — НЕ книга по драфт-сюрвею.
- Вероятно, загружен по ошибке (файл из ~/Downloads). Скриншотов нет.
- 150 страниц, текст не извлекается (скан без OCR).
- sha256: 3153fb77e140a0895d980373883156e167c2c9f1c2ad58c49f6044051ac065e8
- Действие: заменить на нужную книгу.

## Чего пока нет (нужно дозагрузить в cargo-urgency)
1. Книга/кодекс ООН с программой BASIC и формами A–E (IMO/FAO "Guidelines on the Sampling, Inspection..."/Code of Practice — та, где листинг BASIC).
2. Таблицы гидростатических характеристик (hydrostatic tables) конкретного судна для примера.
