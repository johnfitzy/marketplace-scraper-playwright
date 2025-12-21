// Call to enforce a required var
function required(name) {
    const value = process.env[name];
    if (!value) {
        throw new Error(`Missing required env var: ${name}`);
    }
    return value;
}

export const config = {
    worker: {
        maxConcurrency: Number(process.env.MAX_CONCURRENCY || 3),
    },
    scraping: {
        headless: process.env.HEADLESS === "true" || false,
        viewPortWidth: Number(process.env.VIEWPORT_WIDTH) || 1920,
        viewPortHeight: Number(process.env.VIEWPORT_HEIGHT) || 1080,
        baseURL:
            process.env.BASE_URL || "https://www.facebook.com/marketplace/search",
        searchRadius: 100,
    },
    redis: {
        url: process.env.REDIS_URL || "localhost",
        port: Number(process.env.REDIS_PORT || 6379),
        deDupTTL: Number(process.env.REDIS_DUP_TTL || 120), // seconds
        resultQueueName: process.env.REDIS_RESULT_QUEUE_NAME || "queue:results"
    }
};
