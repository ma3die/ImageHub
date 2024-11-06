# ImageHub

**ImageHub** – это многосервисное приложение на Django с использованием Celery для асинхронной обработки изображений и RabbitMQ для передачи сообщений. Redis используется как брокер сообщений и бэкенд для хранения результатов задач Celery.

## Архитектура

ImageHub состоит из следующих компонентов:

1. **web** – основной сервис веб-приложения, запускающий Django сервер.
2. **image_processor** – сервис для обработки изображений.
3. **celery** – Celery worker для выполнения асинхронных задач.
4. **redis** – брокер сообщений для Celery.
5. **db** – база данных PostgreSQL.
6. **rabbitmq** – брокер сообщений RabbitMQ для передачи событий обработки изображений.

## Установка и запуск

### Клонирование репозитория

```
git clone https://github.com/ma3die/ImageHub.git
```

### 1. Подготовка окружения

1. Установите Docker и Docker Compose, если они не установлены.
2. Создайте файл `.env` в корне проекта и добавьте следующие переменные окружения:

   ```env
   # Настройки PostgreSQL
   POSTGRES_HOST=''
   POSTGRES_DB=''
   POSTGRES_USER=''
   POSTGRES_PASSWORD=''
   POSTGRES_PORT=

   # Настройки RabbitMQ
   RABBITMQ_USER='guest'
   RABBITMQ_PASSWORD='guest'
   RABBITMQ_HOST=''
   RABBITMQ_PORT=

   # Настройки Redis
   REDIS_HOST=''
   REDIS_PORT=
   
   # Celery
   CELERY_BROKER_URL = ''
   CELERY_RESULT_BACKEND = ''

### 2. Запуск приложения
Чтобы запустить приложение, выполните команду:
```
docker-compose up --build
```
Docker Compose автоматически соберет образы для всех сервисов, определенных в docker-compose.yml, и запустит их.

### 3. Доступ к сервисам

После запуска приложение будет доступно по следующим адресам:

- **Django (web)**: `http://localhost:8000`
- **RabbitMQ Dashboard**: `http://localhost:15672` (логин: `guest`, пароль: `guest`)
- **Redis**: `localhost:6379`

### 4. Вход в контейнер Django

Если необходимо выполнить миграции или открыть Django shell, войдите в контейнер web:

```
docker-compose exec web bash
```

Запустите миграции (если не были выполнены автоматически):

```
python manage.py migrate
```

### Структура Docker Compose

- **web** – основной веб-сервер на Django.
- **image_processor** – обрабатывает изображения через отдельный Python-скрипт.
- **celery** – Celery worker для выполнения задач.
- **redis** – брокер сообщений для Celery.
- **db** – база данных PostgreSQL.
- **rabbitmq** – брокер сообщений для событий обработки изображений.