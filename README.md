# BVB Scraper

Python module with the scope to scrape information about securities listed on the [Bucharest Stock Exchange](https://www.bvb.ro/).

## How to get it to work
1. `git clone` this repo from command line
2. enter the cloned repo with `cd bvbscraper` command
3. install the wheel with `pip` by referencing the path to the `.whl` file. For example `pip install https://github.com/holgyeso/bvbscraper`
4. On successful installation, the wheel can be imported in Python with `import bvbscraper`

## What the library offers
### Scrape all tickers from BVB with some generic information
The `ScraperService().get_all_shares()` offers the possibility to filter the shares by market and/or tier,
if not all shares must be scraped. By default, it will return the following info about a share: symbol, 
isin, name, total_shares, face_value, market, tier, company (name, fiscal_code, nace_code, district,
country_iso2, industry, sector). The attributes can be extended with detailed company information (
commerce_registry_code, address, website, email, activity field, description, shareholders) and
the start date of the share's trading.

### Return information about specific shares
The `ScraperService().get_share_info()` retrieves the above-mentioned information similarly as stated there, 
the only difference being that this function scrapes information about specific shares, therefore there is
no possibility to filter by market and/or tier. However, the share can be specified as a `symbol` (str) or
as a `share` object.

### Get the price history of a share
The `ScraperService().get_history()` function returns open, high, low and closing prices according to the specified 
period (1d, 5d, 2w, 1m, 3m, 6m, 1y, 2y, 5y, 10y, ytd, max) or a start and end date. The used interval by default is daily,
but it can be changed to one of the values: 1min, 5min, 15min, 30min, 1h, 1D, 1W, 1M. Moreover, the function
expects a bvbscraper.share.Share() object as its required parameter.