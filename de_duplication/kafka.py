from aiokafka import AIOKafkaConsumer
import config
import json

class KafkaConsumer:
    def __init__(self, topic, group_id="default-group", bootstrap_servers=config.BOOTSTRAP_SERVERS):
        self.topic = topic
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            enable_auto_commit=True
        )

    async def start(self):
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    async def get_one(self):
        msg = await self.consumer.getone()
        return msg.key, msg.value
