import pika


class ProducerClient:

    @staticmethod
    def send_message(body):
        parameters = pika.URLParameters('amqp://rabbit:rabbit@rabbitmq:5672')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.queue_declare(queue='stats')
        channel.basic_publish(
            exchange='',
            routing_key='stats',
            body=body
        )
        connection.close()
