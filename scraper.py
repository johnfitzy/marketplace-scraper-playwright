import time
import json
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, expect

import config
from logging_config import logger


async def scroll_until_bottom(page, container_selector, pause=1000, max_attempts=50):
    locator = page.locator(container_selector)
    await locator.hover()

    for _ in range(max_attempts):
        prev_scroll_top = await locator.evaluate("el => el.scrollTop")
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(pause)
        new_scroll_top = await locator.evaluate("el => el.scrollTop")
        if new_scroll_top == prev_scroll_top:
            break

def extract_and_filter_links(soup, job, not_include=None):
    links = []
    for link in soup.find_all('a'):
        if job['product'].lower() in link.text.lower():
            href_tag = link.get('href')
            href = f'https://www.facebook.com/{href_tag}' if href_tag else None
            text = '\n'.join(link.stripped_strings)
            img_tag = link.find('img')
            image_url = img_tag['src'] if img_tag else None
            #TODO; this is buggy
            if not_include is not None and not_include.lower() not in text.lower():
                links.append({
                    'text': text,
                    'url': href,
                    'image_url': image_url
                })
    return links

def parse_links_to_json(links):
    structured_data = []
    price_pattern = re.compile(r'(?P<currency>[^\d\s]*)?(?P<amount>\d[\d,\.]*)')

    for item in links:
        lines = item["text"].split("\n")
        match = next((price_pattern.search(line) for line in lines if price_pattern.search(line)), None)
        if not match:
            continue
        price = float(match.group("amount").replace(",", ""))
        currency = match.group("currency") or ""
        if len(lines) < 2:
            continue
        title = lines[-2]
        location = lines[-1]
        structured_data.append({
            "title": title,
            "price": price,
            "currency": currency,
            "location": location,
            "url": item["url"],
            "image_url": item.get("image_url")
        })

    return structured_data

async def scrape(job, context):
    page = None

    try:

        page = await context.new_page()

        await page.set_viewport_size({"width": config.VIEWPORT_WIDTH, "height": config.VIEWPORT_HEIGHT})

        await page.goto(
            f'https://www.facebook.com/marketplace/search?query={job["product"]}&minPrice={job["min_price"]}&maxPrice={job["max_price"]}&daysSinceListed=1&exact=true')

        await page.get_by_role("button", name="Close").click()

        default_location = page.get_by_role("button", name=re.compile("Within 65", re.IGNORECASE))

        await default_location.click()

        location = f'{job["city"]}, {job["country"]}'

        # Enter the search location
        await page.get_by_role("combobox", name="Location").fill(location)

        # Not selecting the specific location just the first to avoid name spelling differences.
        dropdown_locator = page.locator('ul[role="listbox"] >> li[role="option"]')

        # Wait for first option to appear
        await dropdown_locator.first.wait_for(timeout=5000)

        await page.locator('ul[role="listbox"] >> li[role="option"]').first.click()

        # Click select radius button
        await page.get_by_role("combobox", name="Radius").click()

        # Select the search radius (change to variable)
        await page.get_by_role("option", name="100").click()

        # Click the apply button
        await page.get_by_role("button", name="Apply").click()

        # Wait for the default location sidebar button to change to the new search location.
        await (expect(default_location).to_be_hidden(timeout=10_000))

        await scroll_until_bottom(page, "#facebook", pause=1000, max_attempts=50)

        content = await page.content()

        return BeautifulSoup(content, 'html.parser')

    except PlaywrightTimeoutError:
        logger.error("Timeout occurred while trying to click the button.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
    finally:
        if page is not None:
            logger.info("Closing page...")
            await page.close()


# 1 browser instance shared by all workers
#
# N browser contexts created up front (e.g. 4)
#
# Each worker is assigned a context (based on index modulo)
#
# Each job opens a new page in that assigned context
#
# Page is closed after the job is done
async def worker(name, queue, context):


    while True:
        job = await queue.get()

        logger.info(f"{name} picked up scrape job: {job}")

        if config.TRACE_ENABLED:
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)

        time_start = None

        try:
            time_start = time.time()

            soup = await scrape(job, context)
            links = extract_and_filter_links(soup, job, "case")
            json_result = parse_links_to_json(links)

            time_end = time.time()

            time_since_last_finished = None
            if job.get('last_finished') is not None:
                time_since_last_finished = round(time_end - job['last_finished'])
                job['last_finished'] = round(time_end, 2)

            else:
                job['last_finished'] = time_end


            print(f'Finished! runtime: {round(time_end - time_start, 2)} time since last finished {time_since_last_finished}\n {json.dumps(json_result)}')
            
            # print(json.dumps(json_result, 2) + "\n")
        finally:
            queue.task_done()

            if config.TRACE_ENABLED:

                job_dets  = f'{job['city']}_{job['country'].strip().replace(" ", "")}_{job["product"].strip().replace(" ", "")}_min_{job["min_price"]}_max_{job["max_price"]}_{time_start}'
                await context.tracing.stop(path = f'{config.TRACE_PATH}/{job_dets}.zip')