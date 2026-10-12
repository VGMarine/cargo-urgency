# SSH: Permission denied (publickey) — что делать по шагам

## Шаг 1. Диагностика (2 команды, скопировать целиком)

```bash
cat ~/.ssh/config
ssh -T git@github.com -o IdentitiesOnly=yes
```

`ssh -T git@github.com` должен ответить:
`Hi VGMarine! You've successfully authenticated...`
Если снова `Permission denied (publickey)` — ключ на машине не тот, что добавлен в GitHub.

## Шаг 2. Посмотреть отпечатки локальных ключей

```bash
ssh-keygen -lf ~/.ssh/id_ed25519.pub
ssh-keygen -lf ~/.ssh/id_ed25519_github.pub
```

## Шаг 3. Открыть GitHub → Settings → SSH and GPG keys

https://github.com/settings/keys

Сравнить fingerprint там с тем, что напечатал Шаг 2. Совпадений нет? Значит этот ключ в GitHub не добавлен (или добавлен к другому аккаунту).

## Шаг 4. Добавить правильный ключ

```bash
cat ~/.ssh/id_ed25519_github.pub
```

Скопировать ВЕСЬ вывод (строка начинается с `ssh-ed25519 ...`) и
вставить в https://github.com/settings/keys → **New SSH key** → Add SSH key.

## Шаг 5. Проверить ещё раз

```bash
ssh -T git@github.com
```

После успешного ответа — пуш:

```bash
cd ~/cargo
git push -u origin main
```

---

## Если не хотите возиться с SSH — решение за 2 минуты (HTTPS + токен)

1. https://github.com/settings/tokens → **Generate new token (classic)**
   → note: `cargo-push`, scope: `repo` → Generate → скопировать токен (вида `ghp_...`).
2. В терминале:

```bash
cd ~/cargo
git remote set-url origin https://x-access-token:ВАШ_ТОКЕН@github.com/VGMarine/Draugt-survey-Pyton.git
git push -u origin main
```

Ничего вводить не будет — токен уже в URL.

⚠️ Токен секретный: не вставлять в чат и не коммитить. Когда пришлёте мне доступ к репо (Settings → Collaborators), этот удалённый URL лучше заменить на обычный, а токен отозвать.
