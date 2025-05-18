import asyncio
import config
from logging_config import  logger
from scraper import worker
from job_scheduler import job_scheduler
from job_source import get_strategy_from_env
from playwright.async_api import async_playwright




async def main():

    logger.info("Starting application...")

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    contexts = [await browser.new_context() for _ in range(config.NUM_CONTEXTS)]

    queue  = asyncio.Queue(maxsize=config.MAX_QUEUE_SIZE)
    jobs_list = await get_strategy_from_env().get_scrape_jobs()

    consumers = [
        asyncio.create_task(worker(f"worker-{worker_id}", queue, contexts[worker_id % config.NUM_CONTEXTS])) for worker_id in range(
            config.NUM_WORKERS)
    ]

    await job_scheduler(jobs_list, queue)

asyncio.run(main())