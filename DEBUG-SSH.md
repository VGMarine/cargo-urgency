# Почему GitHub пишет "Permission denied", хотя ключ добавлен

Если ключ точно добавлен в https://github.com/settings/keys, но `ssh -T git@github.com`
всё равно отвечает `Permission denied (publickey)` — причина почти всегда одна из трёх:

## Диагностика (выполнить на вашей машине)

```bash
ssh -vT git@github.com 2>&1 | grep -E "Offering|identity file|Authenticating|permission"
```

Смотрим, какие ключи SSH вообще предлагает:

- Если в выводе **нет** строки `Offering public key: ...id_ed25519_github` —
  SSH не видит ваш ключ (проблема №1 или №2).
- Если ключ предлагается, но ответа `Hi VGMarine!` нет — проблема №3.

## Причина 1. В ~/.ssh/config другой ключ указан для github.com

```bash
cat ~/.ssh/config
```

Если там есть блок вида:
```
Host github.com
    IdentityFile ~/.ssh/id_ed25519        # <- этот ключ НЕ добавлен в GitHub
```
исправьте на тот публичный ключ, который реально лежит в аккаунте:
```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github
    IdentitiesOnly yes
```

## Причина 2. Ключ не добавлен в ssh-agent / права

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_github
chmod 600 ~/.ssh/id_ed25519_github
```

## Причина 3. Ключ добавлен к ДРУГОМУ аккаунту GitHub

Сравните отпечатки:
```bash
ssh-keygen -lf ~/.ssh/id_ed25519_github.pub
```
и откройте https://github.com/settings/keys — fingerprint должен совпасть
один-в-один с одной из записей. Также проверьте, что вы залогинены на github.com
под тем же логином VGMarine, под которым создан репозиторий.

---

## Самый быстрый обходной путь (без починки SSH)

Использовать HTTPS + Personal Access Token — описано в ACCESS-TOKEN.md, 2 минуты:

```bash
cd ~/cargo
git remote set-url origin https://x-access-token:ghp_ВАШ_ТОКЕН@github.com/VGMarine/Draugt-survey-Pyton.git
git push -u origin main
```
