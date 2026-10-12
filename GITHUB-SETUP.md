# Пошаговая загрузка книг: GitHub (основной путь) и локальный терминал

Проверено: в этом окружении есть `git`, но нет `gh` — поэтому репозиторий на GitHub
создаём один раз через веб-интерфейс, дальше всё делаем командами.

---

## Путь A. Через GitHub (рекомендую)

### Шаг 1. Создать репозиторий на сайте (это единственный «клик» в браузере)

1. Зайти на https://github.com/new
2. Repository name: `cargo-urgency` (или любое)
3. Visibility: **Private** (книги кодекса — ваш рабочий материал)
4. Галочки «Add a README» / «Add .gitignore» **не ставить** — репозиторий пустой
5. Нажать **Create repository**

GitHub покажет страницу с командами — их ниже и не нужно повторять дословно,
у нас свой порядок.

### Шаг 2. Настроить git один раз (в терминале вашей машины)

```bash
git config --global user.name  "Ваше Имя"
git config --global user.email "ваш@email.com"
```

### Шаг 3. Положить файлы книг в папку

Допустим, сканы лежат где-то в «Загрузках». Создаём структуру и переносим:

```bash
mkdir -p ~/cargo/sources/originals/imo-code            # кодекс ООН (BASIC, формы A–E)
mkdir -p ~/cargo/sources/originals/survey-book         # книга по survey грузов

mv ~/Downloads/*.pdf  ~/cargo/sources/originals/imo-code/     # поправьте имя папки под факт
mv ~/Downloads/*.png  ~/cargo/sources/originals/survey-book/
```

Для больших сканов (>100 МБ) включаем git-lfs один раз:

```bash
git lfs install
cd ~/cargo
git lfs track "*.pdf" "*.png" "*.jpg" "*.tif"
git add .gitattributes
```

### Шаг 4. Первый коммит и push

```bash
cd ~/cargo
git init -b main
git add .
git commit -m "sources: оригиналы книг для расчётов по осадке"
git remote add origin https://github.com/ВАШ_ЛОГИН/cargo-urgency.git
git push -u origin main
```

Если просит пароль: обычный пароль аккаунта GitHub **не принимается** — нужен
Personal Access Token (см. Шаг 6) или вход через SSH/браузер-менеджер.

### Шаг 5. Дальше — только три команды на каждую новую пачку файлов

```bash
git add sources/originals/ && git commit -m "sources: глава 3, таблицы поправок" && git push
```

### Шаг 6. Токен для push (если аутентификация ещё не настроена)

1. https://github.com/settings/tokens → **Generate new token (classic)**
2. Scope: `repo` (галочка целиком)
3. Скопировать токен (показывается один раз)
4. Спрятать его от лишних глаз:

```bash
echo "https://ВАШ_ЛОГИН:ТОКЕН@github.com/ВАШ_ЛОГИН/cargo-urgency.git" > ~/.gitremote
cd ~/cargo && git remote set-url origin "$(cat ~/.gitremote)"
```

(Ещё красивее — `gh auth login` или SSH-ключ, но это по желанию.)

### Шаг 7. Дать доступ мне

На странице репозитория: **Settings → Collaborators → Add people**, либо пришлите
read-only токен. После этого я клонирую оригиналы к себе в `sources/originals/`,
и мы начинаем этап 1 (контрольный набор из четырёх типов материала).

---

## Путь B. Совсем без GitHub (локально)

Если возиться с сайтом сейчас не хочется, можно передать файлы напрямую в чат:

**Мелкие текстовые файлы (BASIC, формулы) — лучше всего живым текстом**, просто скопируйте в сообщение.

**Файлы через base64.** На вашей машине:

```bash
base64 -w0 page-scan.png > page.b64      # Linux
base64 page-scan.png | pbcopy            # macOS (копирует в буфер обмена)
```

Вставляете содержимое `page.b64` в чат одним сообщением (начните строкой
`FILE: imo-code/page-scan.png`, чтобы я знал имя). Я декодирую:

```bash
base64 -d <<< "...ваш текст..." > sources/originals/page-scan.png
sha256sum sources/originals/page-scan.png   # фиксируем хэш в карточке спецификации
```

Ограничение: base64 увеличивает размер ~на 33%, так что этот способ честен для
файлов примерно до 1–2 МБ. Для целых PDF книг — Path A или ссылка на облако.

---

## Что выбрать

- Есть аккаунт GitHub и терминал → **Путь A**, шаги 1→7. Один клик в браузере,
  остальное команды; зато книги будут под версионным контролем вместе с кодом.
- Нужно передать 2–4 страницы прямо сейчас для экзамена моделей → **Путь B**
  (текст/BASIC в чат, картинки через base64), а полный архив доедет потом через A.
