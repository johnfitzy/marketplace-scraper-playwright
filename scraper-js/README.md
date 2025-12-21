# Scraper NodeJS

### ENV Vars

```
export MAX_CONCURRENCY=N // The number of scrapes to run concurrently. Maps to number of tabs in the context.
export HEADLESS={true|false} // The default is false
```

### Run

`node index.js`

### Notes on Playwright (so I don't forget)

1. Browser/Context/Page model:

```
Browser (Chromium process)        ← VERY expensive
 └── Context (session/profile)   ← medium cost (more of these might help basic session based bot detection)
      └── Page (tab)             ← cheap
```

