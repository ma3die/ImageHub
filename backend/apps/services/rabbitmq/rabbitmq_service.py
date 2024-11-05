import pika
from django.conf import settings
from loguru import logger

def send_rabbitmq_message(message: str):
    """Отправляет сообщение в очередь RabbitMQ."""
    try:
        # Подключение к RabbitMQ
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, credentials=credentials)
        )
        # , port = settings.RABBITMQ_PORT, credentials = credentials
        channel = connection.channel()

        # Создание очереди, если она ещё не создана
        channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

        # Отправка сообщения
        channel.basic_publish(
            exchange='',
            routing_key=settings.RABBITMQ_QUEUE,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # сохраняет сообщения при сбое
            )
        )
        logger.info(f"Сообщение отправлено в RabbitMQ: {message}")
        connection.close()

    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в RabbitMQ: {e}")

print(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)