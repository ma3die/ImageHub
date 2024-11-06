import pika
from django.conf import settings
from loguru import logger

from apps.services.services import retry


@retry(exceptions=(ConnectionError,))
def send_rabbitmq_message(message: str):
    """Отправляет сообщение в очередь RabbitMQ."""
    try:
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, credentials=credentials)
        )
        channel = connection.channel()

        channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=settings.RABBITMQ_QUEUE,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        logger.info(f"Сообщение отправлено в RabbitMQ: {message}")
        connection.close()

    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в RabbitMQ: {e}")
