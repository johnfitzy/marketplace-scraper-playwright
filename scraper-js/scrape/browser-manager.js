import { chromium } from "playwright";
import { config } from "../config/config.js";

export class BrowserManager {
  constructor(browser, context) {
    this.browser = browser;
    this.context = context;
  }

  static async create() {
    const browser = await chromium.launch({
      headless: config.scraping.headless,
    });

    const context = await browser.newContext({
      viewport: {
        width: config.scraping.viewPortWidth,
        height: config.scraping.viewPortHeight,
      },
    });

    return new BrowserManager(browser, context);
  }

  async page() {
    return this.context.newPage();
  }

  async close() {
    await this.browser.close();
  }
}
