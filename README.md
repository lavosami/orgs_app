# Organizations Directory API

REST API для управления справочником организаций с поддержкой иерархических видов деятельности, геолокации и поиска.

## Возможности

- 📋 Управление организациями с контактной информацией
- 🏢 Связанные здания с координатами
- 📞 Множественные телефонные номера
- 🎯 Иерархические виды деятельности (до 3 уровней)
- 🔍 Поиск по названию организации
- 📍 Геопространственный поиск (bbox, радиус)
- 🔐 API ключ для аутентификации

## Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **Pydantic** - валидация данных
- **Alembic** - миграции базы данных
- **Docker** - контейнеризация

## Структура проекта

```
orgs_app/
├── app/
│   ├── main.py          # Основное приложение FastAPI
│   ├── models.py        # SQLAlchemy модели
│   ├── schemas.py       # Pydantic схемы
│   ├── crud.py          # CRUD операции
│   ├── database.py      # Конфигурация БД
│   └── seed_data.py     # Начальные данные
├── alembic/             # Миграции БД
├── tests/               # Тесты
├── docker-compose.yml   # Docker конфигурация
├── Dockerfile          # Docker образ
└── requirements.txt    # Зависимости Python
```

## Быстрый старт

### 1. Запуск с Docker (Рекомендуется)

#### Предварительные требования
- Docker
- Docker Compose

#### Запуск приложения
```bash
# Клонирование репозитория
git clone <repository-url>
cd orgs_app

# Запуск всех сервисов
docker-compose up --build

# Или запуск в фоновом режиме
docker-compose up -d --build
```

#### Проверка работы
После запуска сервисы будут доступны по адресам:
- **API**: http://localhost:8000
- **API Документация**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5050 (admin@admin.com / pgadmin)

#### Управление контейнерами
```bash
# Просмотр логов
docker-compose logs -f web
docker-compose logs -f db

# Остановка сервисов
docker-compose down

# Остановка с удалением volumes (удалит данные БД)
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart web

# Просмотр статуса сервисов
docker-compose ps
```

#### Выполнение команд в контейнере
```bash
# Подключение к контейнеру приложения
docker-compose exec web bash

# Выполнение миграций
docker-compose exec web alembic upgrade head

# Добавление начальных данных
docker-compose exec web python app/seed_data.py

# Запуск тестов
docker-compose exec web pytest tests/
```

#### Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
DATABASE_URL=postgresql+psycopg2://user:password@db:5432/database
API_KEY=your-secret-api-key
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=database
```

### 2. Ручная установка

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/database"
export API_KEY="your-secret-api-key"

# Запуск PostgreSQL (если не используется Docker)
# Создание миграций
alembic upgrade head

# Запуск приложения
uvicorn app.main:app --reload
```

## API Endpoints

### Аутентификация
Все запросы требуют заголовок `X-API-Key` с валидным API ключом.

### Виды деятельности (Activities)

#### Создание вида деятельности
```http
POST /activities/
Content-Type: application/json
X-API-Key: your-api-key

{
  "name": "Образование",
  "parent_id": null
}
```

#### Получение корневых видов деятельности
```http
GET /activities/
X-API-Key: your-api-key
```

### Организации (Organizations)

#### Создание организации
```http
POST /organizations/
Content-Type: application/json
X-API-Key: your-api-key

{
  "name": "МГУ им. М.В. Ломоносова",
  "phones": [
    {"number": "+7 (495) 939-10-00"}
  ],
  "building": {
    "address": "Ленинские горы, 1",
    "latitude": 55.7031,
    "longitude": 37.5306
  },
  "activities": ["activity-uuid-here"]
}
```

#### Получение организации по ID
```http
GET /organizations/{org_id}
X-API-Key: your-api-key
```

#### Поиск организаций по названию
```http
GET /organizations/search_name/?q=университет
X-API-Key: your-api-key
```

#### Организации по зданию
```http
GET /organizations/by-building/{building_id}
X-API-Key: your-api-key
```

#### Организации по виду деятельности
```http
GET /organizations/by-activity/{activity_id}
X-API-Key: your-api-key
```

#### Организации по виду деятельности с потомками
```http
GET /organizations/by-activity-desc/{activity_id}
X-API-Key: your-api-key
```

### Геопространственный поиск

#### Организации в прямоугольной области
```http
GET /organizations/in_bbox?lat_min=55.0&lat_max=56.0&lon_min=37.0&lon_max=38.0
X-API-Key: your-api-key
```

#### Организации в радиусе
```http
GET /organizations/within_radius?center_lat=55.7558&center_lon=37.6176&radius_m=1000
X-API-Key: your-api-key
```

### Здания (Buildings)

#### Получение всех зданий
```http
GET /buildings/
X-API-Key: your-api-key
```

## Модели данных

### Organization (Организация)
- `id` - UUID первичный ключ
- `name` - Название организации
- `phones` - Список телефонных номеров
- `building` - Связанное здание
- `activities` - Список видов деятельности

### Building (Здание)
- `id` - UUID первичный ключ
- `address` - Адрес
- `latitude` - Широта
- `longitude` - Долгота
- `organization_id` - Ссылка на организацию

### Phone (Телефон)
- `id` - UUID первичный ключ
- `number` - Номер телефона
- `organization_id` - Ссылка на организацию

### Activity (Вид деятельности)
- `id` - UUID первичный ключ
- `name` - Название вида деятельности
- `parent_id` - Родительский вид деятельности (иерархия до 3 уровней)

## Конфигурация

### Переменные окружения

- `DATABASE_URL` - URL подключения к PostgreSQL
- `API_KEY` - Секретный ключ для аутентификации API

### Docker Compose сервисы

- **web** - FastAPI приложение (порт 8000)
- **db** - PostgreSQL база данных (порт 5432)
- **pgadmin** - Веб-интерфейс для управления БД (порт 5050)

### Docker конфигурация

#### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml структура
- **db**: PostgreSQL 14 Alpine с постоянным томом для данных
- **pgadmin**: Веб-интерфейс для управления PostgreSQL
- **web**: FastAPI приложение с hot-reload для разработки

#### Полезные Docker команды
```bash
# Сборка только образа приложения
docker-compose build web

# Просмотр использования ресурсов
docker stats

# Очистка неиспользуемых образов
docker system prune

# Просмотр логов конкретного сервиса
docker-compose logs --tail=100 web

# Выполнение команд в базе данных
docker-compose exec db psql -U user -d database
```

## Разработка

### Запуск тестов
```bash
# Локально
pytest tests/

# В Docker
docker-compose exec web pytest tests/
```

### Создание миграций
```bash
# Локально
alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head

# В Docker
docker-compose exec web alembic revision --autogenerate -m "Описание изменений"
docker-compose exec web alembic upgrade head
```

### Добавление начальных данных
```bash
# Локально
python app/seed_data.py

# В Docker
docker-compose exec web python app/seed_data.py
```

### Разработка с Docker

#### Hot-reload
Приложение настроено на автоматическую перезагрузку при изменении файлов в папке `app/`.

#### Отладка
```bash
# Подключение к контейнеру для отладки
docker-compose exec web bash

# Просмотр логов в реальном времени
docker-compose logs -f web

# Перезапуск после изменений в requirements.txt
docker-compose up --build web
```

#### Работа с базой данных
```bash
# Подключение к PostgreSQL
docker-compose exec db psql -U user -d database

# Создание резервной копии
docker-compose exec db pg_dump -U user database > backup.sql

# Восстановление из резервной копии
docker-compose exec -T db psql -U user database < backup.sql
```

## API Документация

После запуска приложения документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Лицензия

См. файл [LICENSE](LICENSE) для подробностей.