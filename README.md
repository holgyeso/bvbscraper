# BVB Scraper

Python module with the scope to scrape information about securities listed on the [Bucharest Stock Exchange](https://www.bvb.ro/).

## How to get it to work
1. `git clone` this repo from the command line
2. enter the cloned repo with `cd bvbscraper` command

## What the library offers
### Scrape information about (all) tickers from BVB
The `ScraperService().get_all_shares()` offers the possibility to get the following info about a share: symbol, isin, name, total_shares, face_value, segment, market, tier, company (name, fiscal_code, nace_code, district,
country_iso2, industry, sector, timezone). 

```
import scraper_service

# initialize the ScraperService object
BVBscraper = scraper_service.ScraperService()

# get info about all shares listed on BVB
BVBscraper.get_share_info(symbol = 'ALL')

# get info about a specific share listed on BVB 
BVBscraper.get_share_info(symbol = 'AAG')
# if the given share is invalid on BVB, the response will be an empty list
BVBscraper.get_share_info(symbol = 'GOOGL')

# multiple shares can be given as a list as well
BVBscraper.get_share_info(symbol = ['AAG', 'ALT', 'VITK'])
# but only valid values will be returned (AAG, ALT, VITK in the example below)
BVBscraper.get_share_info(symbol = ['AAG', 'ALT', 'VITK', 'GOOGL', 1])
```

### Visualize the scraped information
The `info` property of any `Share` or `Company` object will return information about the corresponding object. Since the `company` attribute of a `Share` object is of type `Company`, the `info` property of a `Share` object returns a nested dictionary. To flatten it and visualize the scraped information as a `pandas.dataframe`, the code below can be used:

```
import scraper_service
import pandas as pd

# initialize the ScraperService object
BVBscraper = scraper_service.ScraperService()

# get all shares
shares = BVBscraper.get_share_info(symbol = 'ALL')

# unflatten the info dictionaries
flattened_dict = {}
for share in shares:
    share_dict = share.info
    symbol = share_dict['symbol']
    flattened_dict[symbol] = {}
    for att in share_dict:
        if att != 'symbol':
            if att == 'company':
                for co_att in share_dict['company']:
                    flattened_dict[symbol][co_att] = share_dict['company'][co_att]
            else:
                flattened_dict[symbol][att] = share_dict[att]

# create a pandas DataFrame
share_df = pd.DataFrame.from_dict(flattened_dict, orient='index')
share_df.head()
```


### Get the price history of a share
The `ScraperService().get_trading_history()` function returns _daily_ open, high, low and closing prices along with the volume according to the specified period (1d, 5d, 1m, 3m, 6m, 1y, 2y, 5y, 10y, ytd, max) or a start and end date. The returned values will contain only prices for trading days on BVB.

```
import scraper_service

# initialize the ScraperService object
BVBscraper = scraper_service.ScraperService()

# get all daily trading entries for a given stock
BVBscraper.get_trading_history(share="AAG")
# equivalent with:
BVBscraper.get_trading_history(share="AAG", period="MAX")

# get daily trading entries by giving a Share object
aag = BVBscraper.get_share_info(symbol = 'AAG')
BVBscraper.get_trading_history(share=aag, period="MAX")

# get daily trading entries starting from 2023
BVBscraper.get_trading_history(share="AAG", start_date="2023-01-01")

# get daily trading entries by giving the exact period
BVBscraper.get_trading_history(share="AAG", start_date="2023-01-03", end_date="2023-12-31")
```

From the `dict` output, a `pandas.dataframe` object can be created, as follows:
```
import scraper_service
import pandas as pd
from datetime import datetime

# initialize the ScraperService object
BVBscraper = scraper_service.ScraperService()

# get daily trading history
aag_prices = BVBscraper.get_trading_history(share="AAG", start_date="2023-01-03", end_date="2023-12-31")

# transform returned dict to pandas DataFrame
aag_trading_df = pd.DataFrame(aag_prices)
aag_trading_df = aag_trading_df.rename(columns={
    "t": "timestamp",
    "o": "open_price",
    "c": "close_price",
    "h": "high_price",
    "l": "low_price",
    "v": "volume"
})
aag_trading_df.drop(columns=["s"], inplace=True)

# add a date column derived from the timestamp
aag_trading_df['date'] = aag_trading_df['timestamp'].map(lambda ts: datetime.datetime.fromtimestamp(ts).date())
aag_trading_df
```