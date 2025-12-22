import { BrowserManager } from "./browser-manager.js";
import { config } from "../config/config.js";
import { expect } from "@playwright/test";

const browserManager = await BrowserManager.create();

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function parseLinksToJson(links) {
  const structuredData = [];

  const pricePattern = /(?<currency>[^\d\s]*)?(?<amount>\d[\d,.]*)/;

  for (const item of links) {
    if (!item.text) continue;

    const lines = item.text
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);

    // Find first line that contains a price
    let match = null;
    for (const line of lines) {
      const m = line.match(pricePattern);
      if (m) {
        match = m;
        break;
      }
    }

    if (!match || !match.groups) continue;

    const amountStr = match.groups.amount.replace(/,/g, "");
    const price = Number(amountStr);
    if (Number.isNaN(price)) continue;

    const currency = match.groups.currency || "";

    if (lines.length < 2) continue;

    const title = lines[lines.length - 2];
    const location = lines[lines.length - 1];

    structuredData.push({
      title,
      price,
      currency,
      location,
      url: item.url,
      image_url: item.image_url ?? null,
    });
  }

  return structuredData;
}

export async function extractAndFilterLinks(page, job, notInclude = null) {
  const product = job.product.toLowerCase();

  // $$eval(selector, fn, arg)
  // runs fn in the browser
  return await page.$$eval(
    "a",
    // Function runs in browser
    (anchors, { product, notInclude }) => {
      const results = [];

      for (const a of anchors) {
        const text = a.innerText?.trim() || "";
        if (!text.toLowerCase().includes(product)) continue;

        if (
          notInclude &&
          text.toLowerCase().includes(notInclude.toLowerCase())
        ) {
          continue;
        }

        const href = a.getAttribute("href");
        const img = a.querySelector("img");

        results.push({
          text,
          url: href
            ? href.startsWith("http")
              ? href
              : `https://www.facebook.com${href}`
            : null,
          image_url: img?.src || null,
        });
      }

      return results;
    },
    { product, notInclude } // injected args to func (boundary crossing from node to browser)
  );
}

export async function scrollUntilBottom(
  page,
  containerSelector,
  pause = 1000,
  maxAttempts = 50
) {
  const container = page.locator(containerSelector);
  await container.hover();

  let previousScrollTop = -1;

  for (let i = 0; i < maxAttempts; i++) {
    const currentScrollTop = await container.evaluate((el) => el.scrollTop);

    if (currentScrollTop === previousScrollTop) {
      break; // reached bottom
    }

    previousScrollTop = currentScrollTop;

    await container.evaluate((el) => {
      el.scrollTop += el.clientHeight;
    });

    await page.waitForTimeout(pause);
  }
}

export async function preparePageForDataExtraction(job) {
  const page = await browserManager.page();

  await page.goto(
    `${config.scraping.baseURL}?query=${job.product}&minPrice=${job.min_price}&maxPrice=${job.max_price}&daysSinceListed=1&exact=true`
  );

  // Close login popup (if present)
  await page.getByRole("button", { name: "Close" }).click();

  // Location button
  const locationButton = page.getByRole("button", { name: /Within/i });

  await locationButton.click();

  // Enter search location
  const locationQuery = `${job.city} ${job.country}`;
  await page.getByRole("combobox", { name: "Location" }).fill(locationQuery);

  // Capture the first option
  const firstOption = page
    .locator('ul[role="listbox"] >> li[role="option"]')
    .first();

  // Wait for the dropdown select to be present
  await expect(firstOption).toBeVisible();

  const selectedLocationText = await firstOption
    .locator("span")
    .first()
    .textContent();

  if (!selectedLocationText) {
    throw new Error("Could not read location option text");
  }

  // Click the first option
  await firstOption.click();

  const searchRadius = config.scraping.searchRadius;

  // Set search radius
  await page.getByRole("combobox", { name: "Radius" }).click();

  await page.getByRole("option", { name: searchRadius.toString() }).click();

  await page.getByRole("button", { name: "Apply" }).click();

  // Regex to help getting change in location
  const finalRegex = new RegExp(
    `(?=.*${escapeRegex(selectedLocationText)})(?=.*Within\\s${searchRadius}\\s?km)`,
    "i"
  );

  // Wait for loading of initial search results after radius set
  await expect(page.getByRole("button", { name: finalRegex })).toBeVisible();

  // Return the page
  return page;
}
