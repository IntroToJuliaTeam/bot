# Тётя Джулия

## Клонирование репозитория

Для запуска в режиме монорепозитория нужно склонировать репозиторий вместе с подмодулями:

```commandline
git clone https://github.com/IntroToJuliaTeam/bot.git --recurse-submodules
```

Для запуска в микросервисном режиме нужно склонировать репозиторий без подмодулей:

```commandline
git clone https://github.com/IntroToJuliaTeam/bot.git
```

И дополнительно нужно склонировать [репозиторий с моделью](https://github.com/IntroToJuliaTeam/gpt).

## Подготовка

Создайте `.env` файл по аналогии с [.env.example](.env.example).

```
BOT_TOKEN=...
BACKEND_URL=http://localhost
BACKEND_PORT=8080

# для монорепозитория:
FOLDER_ID=...
KEY_ID=...
ACCOUNT_ID=...
PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----"
S3_ENDPOINT=https://storage.yandexcloud.net
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=...
S3_PREFIX=""
```

## Запуск локально

```commandline
uv run -m src.main
```

Если вы запускаете в микросервисном режиме, необходимо еще запустить
и [репозиторий с моделью](https://github.com/IntroToJuliaTeam/gpt).

## Для локальной разработки

Перед началом работы рекомендуется прописать 

```commandline
uv run pre-commit install
```

для работы git хука с линтерами.

## Запуск в докере

```commandLine
docker build -t yandex-gpt-bot .
```

```commandline
 docker run --rm -it -p 8080:8080 --env-file .env yandex-gpt-bot
```