# Русские переводы (OCR-слой)

Файлы: `Draught-survey-a-guide-to-good-practice_RU.pdf` и
`1992_UNECE_Draught_Survey_Code_January_1992_E_RU.pdf`.

**Статус:** не найдены ни в репозитории (`git log --all`, working tree), ни в
/workspace. Предыдущая загрузка через веб, вероятно, не завершилась.

**Как добавить (на машине valentyn@pelecus):**
```bash
cd ~/cargo-urgency   # или ваш путь к клону
mkdir -p sources/originals/russian
cp "$HOME/Рабочий стол/Новая папка/"*_RU.pdf sources/originals/russian/
git add sources/originals/russian && git commit -m "docs: RU-переводы" && git push
```
Или просто перетащить оба файла на GitHub Web UI в папку `sources/originals/russian/` (Create file → Upload files).
