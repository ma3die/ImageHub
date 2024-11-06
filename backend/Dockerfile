# Объединенный Dockerfile для веб-приложения и сервиса обработки изображений
FROM python:3.10-slim

# Установим необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    libmagic1 \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установим рабочую директорию
WORKDIR /app

# Скопируем файлы зависимостей и установим их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь код приложения
COPY . .

# Установим переменную окружения для указания, какой сервис запускать
ARG SERVICE=web
ENV SERVICE=$SERVICE

# Выполним миграции и запустим сервер для веб-приложения
CMD ["sh", "-c", "if [ \"$SERVICE\" = \"web\" ]; then python manage.py migrate && python manage.py runserver 0.0.0.0:8000; else python apps/services/rabbitmq/image_event_listener.py; fi"]
