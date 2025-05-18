import asyncio
import config

from kafka import KafkaConsumer
from logging_config import logger

async def main():

    consumer = KafkaConsumer(topic=config.TOPIC_SCRAPED_ITEMS)
    await consumer.start()

    try:
        while True:
            key, value = await consumer.get_one()
            logger.info(f"Received: key={key}, value={value}")
    finally:
        await consumer.stop()


asyncio.run(main())
