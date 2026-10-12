# Как дать доступ к репозиторию без SSH (один токен, 2 минуты)

`ssh -T git@github.com` отвечает `Permission denied (publickey)` — значит ни один
ключ с вашей машины не добавлен в аккаунт GitHub. Чинить SSH необязательно:
для push/pull достаточно HTTPS + персонального токена (PAT).

---

## Шаг 1. Создать токен (в браузере)

1. Открыть https://github.com/settings/tokens
2. **Generate new token** → **Generate new token (classic)**
3. Note: `cargo-push`
4. Expiration: 30 days (или дольше)
5. Галки scopes: поставить одну — **`repo`** (вся секция)
6. Внизу нажать **Generate token**
7. Скопировать токен (начинается с `ghp_...`) — GitHub покажет его **только один раз**

## Шаг 2. Подключить токен к локальному репозиторию (в терминале)

Рабочий репозиторий: **VGMarine/cargo-urgency** (книги уже там).

```bash
cd ~/cargo
git remote set-url origin https://x-access-token:ВАШ_ТОКЕН@github.com/VGMarine/cargo-urgency.git
git push -u origin main
```

Замените `ВАШ_ТОКЕН` на скопированную строку `ghp_...` (вместе с префиксом).
Репозиторий `Draugt-survey-Pyton` больше не нужен — чтобы не путаться,
удалите его: страница репо → Settings → Danger Zone → Delete repository.

Проверка, что пуш прошёл: обновите страницу репозитория в браузере — там
должны появиться файлы.

> Токен хранится внутри `.git/config` в открытом виде. Не пересылайте файл
> config и сам токен в публичные чаты. Если токен «засветился» — отзовите его
> на https://github.com/settings/tokens и создайте новый.

## Шаг 3. Дать доступ ассистенту (мне)

Вариант А (правильный): Settings репозитория → **Collaborators and teams** →
Add people → введите логин ассистента (спросите у меня текущий логин) → Add.

Вариант Б (быстрый, менее безопасный): пришлите в чат read-only токен:
снова https://github.com/settings/tokens → Generate new token (classic) →
scopes: только **`repo:status` + `read-repo`**? — нет, для чтения приватного
репо нужен scope **`repo`** целиком; ограничьте срок действия 7 днями и
отзовите после передачи файлов. Формат сообщения в чат:

```
REPO: https://github.com/VGMarine/Draugt-survey-Pyton.git
TOKEN: ghp_....
```

После этого я склонирую оригиналы книг в `/workspace/sources/originals/`.

---

## (Опционально) починить SSH — если хочется без токенов

```bash
cat ~/.ssh/id_ed25519_github.pub        # скопировать ВСЮ строку вывода
```
→ https://github.com/settings/keys → New SSH key → вставить → Add SSH key.

Затем проверить: `ssh -T git@github.com` → должно ответить
`Hi VGMarine! You've successfully authenticated`.

Частая причина отказа: в `~/.ssh/config` прописан `IdentityFile id_ed25519`,
а в GitHub добавлен `id_ed25519_github` (или наоборот). Посмотреть:
`cat ~/.ssh/config` — при двух ключах добавьте блок:

```
Host github.com
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```
