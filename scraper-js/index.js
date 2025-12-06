import { run } from "./worker/worker.js";
// import { config } from "./config/config.js";

console.log("Starting scraper worker.....");

// initial set up
run()
    .then(() => {
        console.log("All operations complete, exiting.");
        process.exit(0);
    })
    .catch((err) => {
        console.error("An error occurred:", err);
        process.exit(1);
    });