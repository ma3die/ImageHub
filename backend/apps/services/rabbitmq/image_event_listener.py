import pika
from loguru import logger

# Конфигурация RabbitMQ
RABBITMQ_HOST = "localhost"  # Используйте свои настройки подключения
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_QUEUE = "image_events"

def callback(ch, method, properties, body):
    """Обработчик входящих сообщений."""
    logger.info(f"Получено сообщение из RabbitMQ: {body.decode()}")

def start_listening():
    """Запускает прослушивание очереди RabbitMQ."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    # , port = RABBITMQ_PORT, credentials = credentials
    channel = connection.channel()

    # Подписываемся на очередь
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)

    logger.info("Сервис обработки изображений запущен и слушает RabbitMQ...")
    channel.start_consuming()

if __name__ == "__main__":
    start_listening()
