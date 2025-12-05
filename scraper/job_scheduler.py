import random
import time

from logging_config import logger


async def job_scheduler(jobs, queue):
    """Continuously shuffle and enqueue jobs, respecting queue capacity."""

    while True:
        logger.debug(f"\nShuffling!!\n")
        random.shuffle(jobs)
        #  re-connect to proxy probably as well.
        batch_start = time.time()
        for job in jobs:
            await queue.put(job)  # will pause if queue is full (throttle)
            logger.info(f"Queued job: {job}")