# Marketplace Scraper Playwright
## A scraper for Marketplace listing using Python, Playwright Asyncio
### Build
```shell
source venv/bin/activate
pip install -r requirements.txt
```

### Config
- All development config is in `.env`. This is picked up by `config.py`
- Currently, it will only read scrape jobs from a file from `./job_params` with individual json entries like:
```shell
{"country": "New Zealand", "radius": "100", "radius_unit": "kilometres", "days_listed": 1, "exact": true, "top_results": 5, "not_include": "case", "city": "Whanganui", "product": "iPhone 11", "min_price": 30, "max_price": 395}
```
....this is extendable in `job_source.py`
### Running
```shell
python main.py
```
### Tracing
```shell
playwright show-trace trace.zip
```
