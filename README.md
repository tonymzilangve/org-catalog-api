# ORG CATALOG API

Сервис предоставляет REST API для работы со справочником организаций, зданий и деятельности.

## Технический стек

- Python 3.x
- FastAPI
- SQLAlchemy + Alembic (миграции)
- PostgreSQL
- Docker
- Uvicorn (ASGI сервер)

## 🚀 Быстрый старт

### Настройка окружения

1. Клонируйте репозиторий
2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```
3. Настройте переменные окружения в `.env`:
```
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=db_name
DATABASE_URL=postgresql://postgres:password@db/org_db
API_KEY=your_api_key_here
```


### Запуск через Docker-Compose

Запуск всех сервисов:
```bash
docker compose up -d
```


## Структура проекта

```
org-catalog-api/
├── alembic/              # Миграции базы данных
├── app/                  # Исходный код
│   ├── api/              # Настройки API
│       ├── routes/       # API маршруты
│       └── schemas/      # Схемы валидации Pydantic
│   ├── core/             # Основные настройки и конфигурация
│   ├── db/               # Конфигурация БД 
│       ├── database.py   # Подключение к БД
│       └── models.py     # Модели данных    
│   └── main.py           # Точка входа приложения
├── alembic.ini           # Настройки миграций
├── docker-compose.yml    # Примеры использования
├── Dockerfile            # Конфигурация Docker
├── requirements.txt      # Зависимости проекта
└── .env.example          # Пример конфигурации окружения
```
