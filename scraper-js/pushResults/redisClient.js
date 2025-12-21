import { config } from "../config/config.js";
import { createClient } from "redis";

export const redis = createClient({
    url: config.redis.REDIS_URL,
});

redis.on("error", err => console.error("Redis Client Error:", err));

await redis.connect();
