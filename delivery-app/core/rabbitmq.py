import aio_pika
from aio_pika import Message, DeliveryMode
import asyncio


class RabbitMQClient:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

    async def send_message(self, queue_name: str, message: str):
        await self.channel.default_exchange.publish(
            Message(body=message.encode(), delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=queue_name,
        )

    async def close(self):
        if self.connection:
            await self.connection.close()
