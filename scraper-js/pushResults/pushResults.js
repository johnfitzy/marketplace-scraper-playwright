import {redis} from "./redisClient.js";
import stringify from "fast-json-stable-stringify";
import crypto from "crypto";
import {config} from "../config/config.js";

function hashResult(result) {

    const fields = {
        title: result.title,
        location: result.location,
        url: result.url,
        price: result.price
    }

    const json = stringify(fields);
    return crypto.createHash("sha256").update(json).digest("hex");
}


async function isDuplicate(result) {
    const hashedResult = hashResult(result)

    // Instead of set use keys with individual TTL and only add if not present
    const added = await redis.set(
        `dedup:${hashedResult}`,
        "1", // Can be anything
        {
            NX: true, // Only set if key doesn't exist
            EX: config.redis.deDupTTL
        }
    );

    console.log(`${added}: ${hashedResult}`);
    return added === "OK";
}

async function pushResultToQueue(result) {
    await redis.lPush(config.redis.resultQueueName, JSON.stringify(result));
}

export async function pushResults(results) {
    for (const result of results) {
        const isDup = await isDuplicate(result);
        if (isDup) {
            await pushResultToQueue(result);
        }
    }
}