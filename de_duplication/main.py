import redis.asyncio as redis  # this is the new official async API
import asyncio
import hashlib
import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

import config
from logging_config import logger


def fingerprint(data: dict) -> str:
    # Use sorted JSON as the fingerprint basis
    dedup_fields = {
        "title": data.get("title"),
        "price": data.get("price"),
        "location": data.get("location"),
        "url": data.get("url"),
    }

    normalized = json.dumps(dedup_fields, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()

async def main():

    redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    consumer = AIOKafkaConsumer(
    config.TOPIC_SCRAPED_ITEMS,
        bootstrap_servers=config.BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=config.BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    await consumer.start()
    await producer.start()

    try:
        async for msg in consumer:

            data = msg.value
            fp = fingerprint(data)

            if not await redis_client.exists(fp):
                await redis_client.set(fp, 1, ex=config.TTL)  # 24h TTL
                logger.info("New item found: %s", data["title"])
                await producer.send(config.TOPIC_NEW_ITEMS, value=data)
            else:
                logger.info("Duplicate skipped: %s", data["title"])
    finally:
        await consumer.stop()
        await producer.stop()
        await redis_client.close()

asyncio.run(main())
