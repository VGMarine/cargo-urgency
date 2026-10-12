# SSH есть, доступа нет — починить за 3 минуты

## Почему так происходит (диагноз по вашему выводу)

`ssh -vT git@github.com` показал:
```
Offering public key: ~/.ssh/id_ed25519 ... SHA256:ftRSNgrG8gustOLtMvJuqviaOcTrdmMPj01GEx16sfE
```
SSH предлагает **только один ключ** — `id_ed25519`. Ключ `id_ed25519_github.pub` он не пробует вообще,
потому что в `~/.ssh/config` нет секции для github.com. GitHub отвечает «Permission denied»,
если предложенный ключ не привязан к аккаунту. То есть: либо на GitHub добавлен
`id_ed25519_github.pub`, а предлагается другой ключ; либо на GitHub добавлен ключ с другой машины.
Ключи «есть», но тот, который реально отправляется, аккаунту неизвестен.

## Шаг 1. Узнаем, какой ключ реально добавлен на GitHub

В браузере: https://github.com/settings/keys — посмотрите **fingerprint** каждого добавленного ключа.

В терминале — отпечатки ваших ключей:
```bash
ssh-keygen -lf ~/.ssh/id_ed25519.pub
ssh-keygen -lf ~/.ssh/id_ed25519_github.pub
```
Совпадения нет? Значит нужный ключ просто не добавлен. Продолжаем — добавим.

## Шаг 2. Добавляем правильный публичный ключ на GitHub

```bash
cat ~/.ssh/id_ed25519_github.pub
```
Скопируйте ВЕСЬ вывод (одна строка, начинается с `ssh-ed25519`).
https://github.com/settings/keys → **New SSH key** → Title: `pelecus` →
Key: вставка → **Add SSH key**.

## Шаг 3. Заставим SSH предлагать именно этот ключ для GitHub

Одна команда (дописывает нужную секцию в config):
```bash
printf 'Host github.com\n    HostName github.com\n    User git\n    IdentityFile ~/.ssh/id_ed25519_github\n    IdentitiesOnly yes\n' >> ~/.ssh/config
```

## Шаг 4. Проверяем

```bash
ssh -T git@github.com
```
Ожидаемый ответ: `Hi VGMarine! You've successfully authenticated...`

## Шаг 5. Пуш

```bash
cd ~/cargo && git push -u origin main
```

## Если всё равно не пускает — обходной путь без SSH (2 минуты)

HTTPS + Personal Access Token работает всегда и не зависит от ключей:

1. https://github.com/settings/tokens → **Generate new token (classic)** → scope `repo` → скопировать токен (`ghp_...`).
2. ```bash
   cd ~/cargo
   git remote set-url origin https://x-access-token:ВАШ_ТОКЕН@github.com/VGMarine/Draugt-survey-Pyton.git
   git push -u origin main
   ```

После успешного пуша — присылайте ссылку на репозиторий (или read-only токен), начинаем этап 1: разбор контрольных примеров survey.
