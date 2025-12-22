import { run } from "./worker/worker.js";

console.log("Starting scraper worker.....");

// initial set up
try {
    await run();
    console.log("All operations complete, exiting.");
} catch (err) {
    console.error("An error occurred:", err);
    process.exit(1);
}