import json

from aiokafka import AIOKafkaProducer

import config

class KafkaPublisher:
    def __init__(self, bootstrap_servers=config.BOOTSTRAP_SERVERS):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8")
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send(self, topic, key, value):
        await self.producer.send_and_wait(topic, key=key, value=value)
