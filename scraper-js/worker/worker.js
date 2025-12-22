import {Sema} from "async-sema";
import {config} from "../config/config.js";
import {
    preparePageForDataExtraction,
    scrollUntilBottom,
    extractAndFilterLinks,
    parseLinksToJson,
} from "../scrape/scraper.js";
import {next} from "../jobs/job-fetcher.js";

import {pushResults} from "../pushResults/pushResults.js";

const sema = new Sema(config.worker.maxConcurrency);

async function processJob(job) {
    let page;

    try {
        page = await preparePageForDataExtraction(job);
        if (!page) return;

        const id = crypto.randomUUID();

        console.log(`[${id}] start`);
        await scrollUntilBottom(page, "#facebook");

        const links = await extractAndFilterLinks(page, job);
        const jsonResults = parseLinksToJson(links);

        await pushResults(jsonResults);
        console.log(`[${id}] job finished pushed results to redis`);

    } catch (err) {
        console.error("Error with scrape", err);
    } finally {
        if (page) await page.close();
        sema.release();
    }
}

export async function run() {

    while (true) {
        await sema.acquire();
        const job = await next();
        void processJob(job);
    }
}