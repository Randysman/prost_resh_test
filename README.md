# Deribit Price Tracker

Сервис для периодического сбора индексных цен BTC/USD и ETH/USD с биржи Deribit и предоставления их через REST API.

## Содержание
- [Стек технологий](#стек-технологий)
- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [API документация](#api-документация)

---

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Web-фреймворк | FastAPI |
| База данных | PostgreSQL 16 |
| ORM | SQLAlchemy 2 (async) |
| HTTP-клиент | aiohttp |
| Очередь задач | Celery + Redis |
| Контейнеризация | Docker + Docker Compose |

---

## Архитектура
```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                  │
│                                                  │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐  │
│  │  app     │    │  worker  │    │   beat    │  │
│  │ FastAPI  │    │  Celery  │◄───│  Celery   │  │
│  └────┬─────┘    └────┬─────┘    └───────────┘  │
│       │               │ каждые 60s               │
│       │               ▼                          │
│       │         ┌───────────┐                    │
│       │         │  Deribit  │                    │
│       │         │   API     │                    │
│       │         └─────┬─────┘                    │
│       ▼               ▼                          │
│  ┌──────────────────────────┐  ┌──────────────┐  │
│  │        PostgreSQL        │  │    Redis     │  │
│  └──────────────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────┘
```

Celery Beat каждые 60 секунд запускает задачу, которая через aiohttp забирает цены с Deribit и сохраняет в PostgreSQL. FastAPI читает данные из той же БД и отдаёт через REST API.

---

## Структура проекта
```
deribit-price-tracker/
├── app/
│   ├── api/
│   │   ├── dependencies.py      # Dependency Injection для FastAPI
│   │   ├── schemas.py           # Pydantic схемы запросов/ответов
│   │   └── routes/
│   │       └── prices.py        # Эндпоинты /prices
│   ├── core/
│   │   ├── config.py            # Настройки через pydantic-settings
│   │   └── exceptions.py        # Кастомные исключения
│   ├── db/
│   │   ├── models.py            # SQLAlchemy ORM модели
│   │   ├── repository.py        # Слой доступа к данным
│   │   ├── session.py           # Async сессия (FastAPI)
│   │   └── sync_session.py      # Sync сессия (Celery)
│   ├── services/
│   │   ├── deribit_client.py    # HTTP клиент для Deribit API
│   │   └── price_service.py     # Бизнес-логика
│   ├── tasks/
│   │   └── celery_app.py        # Celery приложение и задачи
│   └── main.py                  # Точка входа FastAPI
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Требования

- Docker >= 24.0
- Docker Compose >= 2.0

Для локального запуска без Docker: Python >= 3.12, PostgreSQL >= 16, Redis >= 7.

---

## Быстрый старт

**1. Клонировать репозиторий**
```bash
git clone https://gitlab.com/your-username/deribit-price-tracker.git
cd deribit-price-tracker
```

**2. Создать файл окружения**
```bash
cp .env.example .env
```

**3. Запустить проект**
```bash
docker compose up --build
```

После старта API доступно на `http://localhost:8000`, Swagger UI на `http://localhost:8000/docs`.

**4. Проверить работу** (подождать ~60 секунд пока Celery соберёт первые цены)
```bash
curl "http://localhost:8000/api/v1/prices/latest?ticker=btc_usd"
```


## API документация

Все эндпоинты принимают обязательный query-параметр `ticker`.
Поддерживаемые значения: `btc_usd`, `eth_usd`.

### GET `/api/v1/prices/`

Получить все сохранённые цены по тикеру.
```
GET /api/v1/prices/?ticker=btc_usd
```
```json
{
  "ticker": "btc_usd",
  "count": 2,
  "records": [
    {
      "id": 2,
      "ticker": "btc_usd",
      "price": "65432.10000000",
      "timestamp": 1716390120
    },
    {
      "id": 1,
      "ticker": "btc_usd",
      "price": "65100.50000000",
      "timestamp": 1716390060
    }
  ]
}
```

### GET `/api/v1/prices/latest`

Получить последнюю записанную цену по тикеру.
```
GET /api/v1/prices/latest?ticker=btc_usd
```
```json
{
  "ticker": "btc_usd",
  "price": "65432.10000000",
  "timestamp": 1716390120
}
```

### GET `/api/v1/prices/range`

Получить цены за период по Unix timestamp.
```
GET /api/v1/prices/range?ticker=btc_usd&from_timestamp=1716390000&to_timestamp=1716390120
```

| Параметр | Тип | Описание |
|----------|-----|----------|
| `ticker` | string | Тикер валюты |
| `from_timestamp` | integer | Начало периода (Unix timestamp, секунды) |
| `to_timestamp` | integer | Конец периода (Unix timestamp, секунды) |

### Коды ошибок

| Код | Причина |
|-----|---------|
| `400` | Неподдерживаемый тикер или некорректные параметры |
| `404` | Данные не найдены |

---


