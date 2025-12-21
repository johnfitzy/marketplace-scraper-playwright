import {Sema} from "async-sema";
import {config} from "../config/config.js";
import {
    preparePageForDataExtraction,
    scrollUntilBottom,
    extractAndFilterLinks,
    parseLinksToJson,
} from "../scrape/scraper.js";

import {pushResults} from "../pushResults/pushResults.js";

const sema = new Sema(config.worker.maxConcurrency);

// TODO; basic blocking run make it properly async
export async function run() {

    // TODO; hard coded single job for now. Fix later with scheduling
    const job = {
        country: "New Zealand",
        radius: "100",
        radius_unit: "kilometres",
        days_listed: 1,
        exact: true,
        top_results: 5,
        not_include: "case",
        city: "Auckland",
        product: "iPhone 16",
        min_price: 100,
        max_price: 1750,
    };

    // Initial search with this job
    const page = await preparePageForDataExtraction(job);

    // Initial search failed for some reason
    if (!page) {
        console.warn("Skipping job due to scrape failure");
        sema.release();
        return;
    }

    // Scroll all the way to the bottom so get all links
    await scrollUntilBottom(page, "#facebook");

    await page.content();

    // Extract links
    const links = await extractAndFilterLinks(page, job);

    // TODO; remove later
    // console.log(links);

    const results = parseLinksToJson(links);

    await pushResults(results)



    // TODO; remove later
    // console.log(results);

    // Close the page
    page.close();
}