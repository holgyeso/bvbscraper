# from bvbscraper.bvb.share import Share
# from bvbscraper.bvb.company import Company
# from bvbscraper.bvb.utils import share_utils as utils
import time
from share import Share
from company import Company
from utils import share_utils as utils
from bs4 import BeautifulSoup
import datetime
import dateutil.relativedelta as relativedelta
import re
import pandas as pd
import warnings



class ScraperService:
    _TIMEZONE = datetime.timezone.utc
    _ALL_VALUES = ['', 'ALL']
    _HISTORY_INTERVALS = {
        "1MIN": {'dt': 'INTRA', 'p': 'intraday_1'},
        "5MIN": {'dt': 'INTRA', 'p': 'intraday_5'},
        "15MIN": {'dt': 'INTRA', 'p': 'intraday_15'},
        "30MIN": {'dt': 'INTRA', 'p': 'intraday_30'},
        "1H": {'dt': 'INTRA', 'p': 'intraday_60'},
        "1D": {'dt': 'DAILY', 'p': 'day'},
        "1W": {'dt': 'DAILY', 'p': 'week'},
        "1M": {'dt': 'MONTH', 'p': 'month'}
    }
    _HISTORY_PERIODS = {
        "1D": datetime.timedelta(days=1),
        "5D": datetime.timedelta(days=5),
        "2W": relativedelta.relativedelta(weeks=2),
        "1M": relativedelta.relativedelta(months=1),
        "3M": relativedelta.relativedelta(months=3),
        "6M": relativedelta.relativedelta(months=6),
        "1Y": relativedelta.relativedelta(years=1),
        "2Y": relativedelta.relativedelta(years=2),
        "5Y": relativedelta.relativedelta(years=5),
        "10Y": relativedelta.relativedelta(years=10),
        "YTD": None,
        "MAX": None}
    _MIN_START_DATE = datetime.datetime(
        1970, 1, 1, tzinfo=datetime.timezone.utc)

    # # UTIL FUNCTIONS #
    # def _standardize_list_parameter(self, possible_values: list, value: str or list):
    #     """
    #     The function normalizes the `value` parameter:
    #         - checks if the value is a valid one (one of the possible_values)
    #         - if the value symbolizes all possible values, then all possible values will be returned
    #         - if `value` is a valid possible value, the list representation of this will be returned
    #         - if `value` is a list and all it's elements are valid, `value` will be returned
    #     :param possible_values: all valid values that the `value` parameter can have (besides '', 'ALL')
    #     :type possible_values: list
    #     :param value: the value that must be validated and normalized
    #     :type value: str or list
    #     :return: normalized value as list, containing only valid values written with uppercase
    #     :rtype: list
    #     :raises ValueError: if the provided value contains invalid elements
    #     :raises TypeError: if `possible_values` is not list or `values` is not string or list
    #     """
    #     if type(possible_values) != list:
    #         raise TypeError("possible_values parameter should be of type list.")

    #     # if a single string value was provided
    #     if type(value) == str:
    #         value = value.upper()

    #         # if market param means all, return all possible market values
    #         if value in self._ALL_VALUES:
    #             return list(possible_values)

    #         # if a single market was added, return it as list only if it is a valid market; otherwise raise error.
    #         else:
    #             if value in possible_values:
    #                 return [value]
    #             else:
    #                 raise ValueError("The provided '" + value + "' abbreviation is not valid.")
    #     # if the value is a list and contains valid elements, return value with uppercase, else raise error
    #     elif type(value) == list:
    #         for v in value:
    #             if v.upper() not in possible_values:
    #                 raise ValueError("The provided '" + v + "' abbreviation is not valid.")
    #         return [v.upper() for v in value]
    #     # if it was not a str nor a list, raise error
    #     else:
    #         raise TypeError("Market parameter must be a str or list.")

    # # SCRAPING FUNCTIONS #
    # def __get_shares_from_share_list(self, market: str or list = 'all', tier: str or list = 'all',
    #                                  symbol: str or list = 'all'):
    #     """
    #     Gets all shares from BVB that are traded in the specified market and tier with some general info:
    #         * symbol
    #         * isin
    #         * name
    #         * total_shares
    #         * face_value
    #         * market
    #         * tier
    #         * company:
    #             * name
    #             * fiscal_code
    #             * nace_code
    #             * district
    #             * country_iso2
    #     If the symbol parameter is given, the symbol will act as a filter, so a Share object will be returned only
    #     for those symbols that are valid (were in the scraped CSV from BVB).
    #     :param market: the abbreviation of a BVB market or '' or 'all' representing all markets. Defaults to 'all'.
    #     :type: str or list
    #     :param tier: abbreviation of a BVB market tier or '' or 'all' representing all market tiers. Defaults to 'all'.
    #     :type: str or list
    #     :param symbol: the symbols for that the above-mentioned information needs to be retrieved.
    #     :type: str or list
    #     :return: an array that contains Share instances that match the market and tier criteria
    #     :rtype: list of Share objects

    #     .. note::
    #     market abbreviations:
    #         |    - 'REGS' => Regulated Market
    #         |    - 'AERO'  => AeRO
    #         |    - 'MTS' => MTS Intl
    #     tier abbreviations:
    #         |   - 'INTL': => REGS Int'l tier
    #         |   - 'PREMIUM': => REGS Premium
    #         |   - 'STANDARD': => REGS Standard
    #         |   - 'AERO_PREMIUM': => AeRO Premium
    #         |   - 'AERO_STANDARD': => AeRO Standard
    #         |   - 'AERO_BASE': => AeRO Base
    #         |   - 'MTS_INTL': => Intl MTS

    #     The script automatically recognizes needed and filter columns by the column names. If a column is not present
    #     in a row, it will not be considered.
    #     """
    #     _URL = "https://www.bvb.ro/FinancialInstruments/Markets/SharesListForDownload.ashx"

    #     _NEEDED_COLUMNS = {  # info that will be returned about a share
    #         'symbol': 'Simbol',
    #         'isin': 'ISIN',
    #         'name': 'Denumire emisiune',  # it is not necessarily the issuer's name
    #         'total_shares': 'Actiuni',
    #         'face_value': 'Valoare nominala',
    #     }
    #     _COMPANY_COLUMNS = {  # info about the company that will be converted into a company object referenced in share
    #         'name': 'Emitent',
    #         'fiscal_code': 'Cod Fiscal / CUI',
    #         'nace_code': 'Cod CAEN',
    #         'district': 'Judet',
    #         'country_iso2': 'Tara'

    #     }
    #     _FILTER_COLUMNS = {'symbol': 'Simbol', 'tier': 'Sectiune bursa',
    #                        'market': 'Piata Principala'}  # columns by those data rows will be filtered

    #     # market and tier parameter mapping dicts {param_value: scraped_value}
    #     _MARKETS = {
    #         'REGS': 'REGS',  # Regulated Market
    #         'AERO': 'XRS1',  # AeRO
    #         'MTS': 'XRSI'  # MTS Intl
    #     }

    #     _TIERS = {
    #         'INTL': "INT'L",  # REGS Int'l tier
    #         'PREMIUM': 'PREMIUM',  # REGS Premium
    #         'STANDARD': 'STANDARD',  # REGS Standard
    #         'AERO_PREMIUM': 'AERO PREMIUM',  # AeRO Premium
    #         'AERO_STANDARD': 'AERO STANDARD',  # AeRO Standard
    #         'AERO_BASE': 'AERO BASE',  # AeRO Base
    #         'MTS_INTL': 'INTL-MTS',  # Intl MTS
    #     }

    #     # construct the filter dict that contains the possible values of each filter column
    #     _FILTERS = {
    #         'symbol': [],  # will be removed if all symbols must be downloaded
    #         'market': [],
    #         'tier': []
    #     }

    #     if type(symbol) == str:
    #         if symbol.upper() != 'ALL':
    #             symbol = [symbol]

    #     if type(symbol) == list:
    #         for sy in symbol:
    #             if type(sy) == str:
    #                 if re.findall("^[a-zA-Z0-9]+$", sy):
    #                     _FILTERS['symbol'].append(sy.upper())

    #     if not _FILTERS['symbol']:
    #         del _FILTERS['symbol']

    #     market_filter_values = self._standardize_list_parameter(possible_values=list(_MARKETS), value=market)
    #     _FILTERS['market'] = [_MARKETS[m] for m in market_filter_values]

    #     tier_filter_values = self._standardize_list_parameter(possible_values=list(_TIERS), value=tier)
    #     _FILTERS['tier'] = [_TIERS[t] for t in tier_filter_values]

    #     # scrape BVB and process the returned csv
    #     response = utils.get_url_response(_URL).text  # returns a csv that has \r\n line endings and ; separator
    #     response_lines = response.split("\r\n")  # the first row will be the header and the last one will be ''
    #     headers = [column.upper() for column in response_lines[0].split(";")]

    #     # retrieve the index of needed and filter columns; so data could be accessed directly based on index and
    #     # there will be no need to iterate through the header columns and each row column and check if the header
    #     # is in _NEEDED_COLUMNS, get its index and based on this get the value from the row.
    #     _NEEDED_COLUMNS_INDEX = {n: headers.index(_NEEDED_COLUMNS[n]) for n in _NEEDED_COLUMNS}
    #     _COMPANY_COLUMNS_INDEX = {c: headers.index(_COMPANY_COLUMNS[c]) for c in _COMPANY_COLUMNS}
    #     _FILTER_COLUMNS_INDEX = {f: headers.index(_FILTER_COLUMNS[f]) for f in _FILTER_COLUMNS}

    #     # first each row in response_lines should be split by ';' then, all filters should be checked, and
    #     # if the row meets the criteria, the needed information will be selected and a Share instance will be
    #     # initialized and added to return_values.
    #     return_values = []

    #     for row in response_lines[1:-1]:
    #         data_row = row.split(";")
    #         if len(data_row) > 1:
    #             valid_row = True
    #             # iterate through the filter columns' index and check if the split data row has on the index
    #             # corresponding to a certain filter column a value that meets the criteria set in _FILTERS for the
    #             # specific filter column.
    #             for filter_column in _FILTERS:
    #                 # if the data row's value in the filter column's index does not belong to possible values of the
    #                 # specific filter, the row should not be considered
    #                 filter_index = _FILTER_COLUMNS_INDEX[filter_column]
    #                 if filter_index >= len(data_row):
    #                     valid_row = False
    #                     break
    #                 else:
    #                     if data_row[filter_index].upper() not in _FILTERS[filter_column]:
    #                         valid_row = False
    #                         break
    #             if valid_row:
    #                 share_init_dict = {}

    #                 for col in _NEEDED_COLUMNS:
    #                     try:
    #                         share_init_dict[col] = data_row[_NEEDED_COLUMNS_INDEX[col]]
    #                     except IndexError:
    #                         share_init_dict[col] = None

    #                 for col in _FILTER_COLUMNS:
    #                     try:
    #                         share_init_dict[col] = data_row[_FILTER_COLUMNS_INDEX[col]]
    #                     except IndexError:
    #                         share_init_dict[col] = None

    #                 company_dict = {}
    #                 for col in _COMPANY_COLUMNS:
    #                     try:
    #                         company_dict[col] = data_row[_COMPANY_COLUMNS_INDEX[col]]
    #                     except IndexError:
    #                         company_dict[col] = None

    #                 co_name = company_dict['name']
    #                 co_fiscal_code = company_dict['fiscal_code']
    #                 company = Company(name=co_name, fiscal_code=co_fiscal_code, params=company_dict)

    #                 share_init_dict['company'] = company
    #                 share_symbol = share_init_dict['symbol']

    #                 return_values.append(Share(symbol=share_symbol, params=share_init_dict))

    #     return return_values


    # def __get_detailed_company_info(self, share: Share):
    #     """
    #     Gets the following information from the "Issuer profile" section of the page of a share on BVB.
    #     The information will be inserted in the Share's company attribute of type bvb.company.Company.
            # * commerce_registry_code
            # * address
            # * website
            # * email
            # * activity field
            # * description
            # * shareholders
    #     :param share: the share object that's company fields will be completed.
    #     :type: bvb.share.Share
    #     :return: the new Share object with the fields that were retrieved from BVB
    #     :rtype: list of Shares.
    #     """

        # _COMPANY_INFO_BUTTON = "Issuer profile"

        # html = utils.post_response_instrument_details_form(
        #     symbol=share.symbol,
        #     button=_COMPANY_INFO_BUTTON,
        #     form_id="aspnetForm"
        # )

        # soup = BeautifulSoup(html, 'html.parser')

        # company_info = {}

        # # issuer profile
        # profile_table = soup.find("table", {"id": "ctl00_body_ctl02_CompanyProfile_dvIssProfile"})

        # _NEEDED_PROFILE_INFO = {
        #     'Commerce Registry Code': 'commerce_registry_code',
        #     'Address': 'address',
        #     'Website': 'website',
        #     'E-mail': 'email',
        #     'Field of activity': 'activity_field'
        # }

        # for tr in profile_table.find_all('tr'):
        #     tds = tr.find_all('td')
        #     if len(tds) != 2:
        #         raise ValueError("A tr element does not have exactly two td elements in company profile")

        #     key = tds[0].text
        #     if key in _NEEDED_PROFILE_INFO:
        #         if key == "Website":
        #             val = tds[1].find("a")['href']
        #         else:
        #             val = tds[1].text.replace("\r\n", "").strip()
        #         company_info[_NEEDED_PROFILE_INFO[key]] = val

        # # issuer description
        # description_div = soup.find("div", {"id": "ctl00_body_ctl02_CompanyProfile_CDescription"})
        # if description_div:
        #     description_span = description_div.find_all("span", {"lang": "EN-US"})
        #     desc_text = ""
        #     for span in description_span:
        #         desc_text += span.text

        #     company_info["description"] = desc_text

        # # shareholders
        # shareholders = soup.find("table", {"id": "gvDetails"})
        # if shareholders:
        #     shareholder_list = []
        #     trs = shareholders.find_all("tr")
        #     headers = [th.text for th in trs[0].find_all("th")]
        #     for tr in trs[1:-1]:
        #         shareholder_dict = {}
        #         tds = tr.find_all("td")
        #         for h in range(0, len(headers)):
        #             shareholder_dict[headers[h]] = tds[h].text
        #         shareholder_list.append(shareholder_dict)

        #     company_info["shareholders"] = shareholder_list

        # for i in company_info:
        #     share.company.__setattr__(i, company_info[i])

        # return share

    # def __get_issue_info(self, share: Share):
    #     """
    #     Gets the following information from the "Overview" section of the page of a share on BVB:
    #         * start_trading_day
    #     :param share: the share object that's attributes will be completed.
    #     :type: bvb.share.Share
    #     :return: the new Share object with the fields that were retrieved from BVB
    #     :rtype: list of Shares.
    #     """
    #     _COMPANY_INFO_BUTTON = "Overview"

    #     html = utils.post_response_instrument_details_form(
    #         symbol=share.symbol,
    #         button=_COMPANY_INFO_BUTTON,
    #         form_id="aspnetForm"
    #     )

    #     soup = BeautifulSoup(html, 'html.parser')

    #     issue_info = soup.find("h2", string="Issue info").parent.find("table", {"id": "dvInfo"})

    #     _NEEDED_INFO = {
    #         # "Share Capital": "share_capital", #TODO: to be added if necessary at financials
    #         "Start trading date": "start_trading_date"
    #     }

    #     share_info = {}

    #     for tr in issue_info.find_all("tr"):
    #         tds = tr.find_all("td")
    #         key = tds[0].text
    #         if key in _NEEDED_INFO:
    #             share_info[_NEEDED_INFO[key]] = tds[1].text

    #     for info in share_info:
    #         share.__setattr__(info, share_info[info])

    #     return share

    # # AGGREGATING SCRAPING FUNCTIONS #
    # def __get_general_share_info(self, symbol: str or list):
    #     """
    #     Initializes a share object for the symbol with the following information:
    #         * symbol
    #         * isin
    #         * name
    #         * total_shares
    #         * face_value
    #         * market
    #         * tier
    #         * company:
    #             * name
    #             * fiscal_code
    #             * nace_code
    #             * district
    #             * country_iso2
    #             * sector
    #             * industry
    #     Calls the __get_shares_from_share_list() and __get_symbol_info_wapi() scraping functions
    #     :param symbol:
    #     :type: str or list of strings
    #     :return: list of Shares with the above information retrieved.
    #     :rtype: list of Share objects
    #     """
    #     shares = self.__get_shares_from_share_list(market='all', tier='all', symbol=symbol)
    #     for share in shares:
    #         share = self.__get_symbol_info_wapi(share=share)

    #     return shares

    # def __get_additional_info(self, shares: Share or list,
    #                           detailed_company_info: bool = False, issue_info: bool = False):
    #     """
    #     Calls the specific functions on the provided shares objects
    #     :param shares:
    #     :type: Share or list of Share objects
    #     :param detailed_company_info: True if detailed_company_info should be retrieved. Defaults to False.
    #     :type: bool
    #     :param issue_info: True if issue_info should be retrieved. Defaults to False.
    #     :type: bool
    #     :return: list of Shares object with completed information based on what parameters were set to be True.
    #     :rtype: list of Share objects
    #     """
    #     if isinstance(shares, Share):
    #         shares = [shares]

    #     for share in shares:
    #         if detailed_company_info:
    #             share = self.__get_detailed_company_info(share=share)
    #         if issue_info:
    #             share = self.__get_issue_info(share=share)

    #     return shares

    # # PUBLIC FUNCTIONS #
    # def get_all_shares(self, market: str or list = 'all', tier: str or list = 'all',
    #                    detailed_company_info: bool = True, issue_info: bool = True):
    #     """
    #     Gets all shares from BVB that are traded in the specified market and tier, with the following information:
    #         * symbol
    #         * isin
    #         * name
    #         * total_shares
    #         * face_value
    #         * market
    #         * tier
    #         * company:
    #             * name
    #             * fiscal_code
    #             * nace_code
    #             * district
    #             * country_iso2
    #             * industry
    #             * sector
    #     :param market: the abbreviation of BVB market(s) or '' or 'all' representing all markets.
    #     :param tier: the abbreviation of BVB market tier(s) or '' or 'all' representing all market tiers.
    #     :param detailed_company_info: if True then further information will be returned about a share:
    #     commerce_registry_code, address, website, email, activity field, description, shareholders. Defaults to True.
    #     :param issue_info: if True, the start date of trading will be returned as well
    #     :return: an array that contain Share instances that match the market and tier criteria

    #     .. note::
    #     market abbreviations:
    #         |    - 'REGS' => Regulated Market
    #         |    - 'AERO'  => AeRO
    #         |    - 'MTS' => MTS Intl
    #     tier abbreviations:
    #         |   - 'INTL': => REGS Int'l tier
    #         |   - 'PREMIUM': => REGS Premium
    #         |   - 'STANDARD': => REGS Standard
    #         |   - 'AERO_PREMIUM': => AeRO Premium
    #         |   - 'AERO_STANDARD': => AeRO Standard
    #         |   - 'AERO_BASE': => AeRO Base
    #         |   - 'MTS_INTL': => Intl MTS
    #     """
    #     shares = self.__get_shares_from_share_list(market=market, tier=tier)

    #     for share in shares:
    #         share = self.__get_symbol_info_wapi(share=share)

    #     share = self.__get_additional_info(shares=shares, detailed_company_info=detailed_company_info,
    #                                        issue_info=issue_info)

    #     return shares

    # def get_share_info(self, symbol: str or list = None,
    #                    detailed_company_info: bool = True, issue_info: bool = True,
    #                    share: Share or list = None):
    #     """
    #     Gets information of a share about:
    #         * symbol
    #         * isin
    #         * name
    #         * total_shares
    #         * face_value
    #         * market
    #         * tier
    #         * company:
    #             * name
    #             * fiscal_code
    #             * nace_code
    #             * district
    #             * country_iso2
    #             * industry
    #             * sector
    #     :param symbol: the BVB ticker of the share about that information must be retrieved
    #     :param detailed_company_info: if True then further information will be returned about a share:
    #     commerce_registry_code, address, website, email, activity field, description, shareholders. Defaults to True.
    #     :param issue_info: if True, the start date of trading will be returned as well
    #     :param share: the share can be specified as a bvbscraper.share.Share object too
    #     :return: a Share object or a list of Shares with the specified information according to the parameters
    #     """
    #     if share is None and symbol is None:
    #         raise ValueError("One of share and symbol parameters must be given.")

    #     if share:
    #         if type(share) == str:
    #             share = [share]

    #         if type(share) == list:
    #             for sh in share:
    #                 if not isinstance(sh, Share):
    #                     raise TypeError(f"The provided {sh} share is not of type bvbscraper.bvb.Share.")
    #     else:
    #         if type(symbol) == str:
    #             symbol = [symbol]

    #         if type(symbol) == list:
    #             share = self.__get_general_share_info(symbol=symbol)

    #     share = self.__get_additional_info(shares=share, detailed_company_info=detailed_company_info,
    #                                        issue_info=issue_info)

    #     if len(share) == 1:
    #         return share[0]

    #     return share

# def get_history(self, share: Share or list, period: str = "1m", start_date: datetime or str = None,
#                     end_date: datetime or str = None, interval: str = '1D',
#                     adjusted: bool = True, format: str = 'json'):
#         # """
#         # Gets open, close, highest and lowest price and volume for the specific share.
#         # Period or start_date and end_date must be provided.
#         # If all three are provided, start date and end date will be considered.

#         # :param format: json or dataframe
#         # :param share: a Share object that's history should be downloaded
#         # :type: bvb.share.Share
#         # :param period: Valid periods: 1d, 5d, 2w, 1m, 3m, 6m, 1y, 2y, 5y, 10y, ytd, max
#         # :param start_date: download start date string (YYYY-MM-DD) or datetime.datetime object.
#         # :param end_date: download end date string (YYYY-MM-DD), "now" or datetime.datetime object.
#         # :param interval: frequency of data. Valid intervals: 1min, 5min, 15min, 30min, 1h, 1D, 1W, 1M. Defaults to 1 day (1D).
#         # :param adjusted: True to return adjusted prices, False for unadjusted. Defaults True.
#         # :return: pandas.DataFrame with date, open, close, high, low, volume columns. ##TODO: revise
#         # """

#         # if not isinstance(share, Share):
#         #     raise TypeError("Provided share is not type of Share.")

#         # if period is None and start_date is None and end_date is None:
#         #     raise ValueError("Period or start and end date must be provided.")

#         # if start_date and end_date:
#         #     if type(start_date) == str:
#         #         try:
#         #             start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
#         #         except ValueError:
#         #             raise ValueError("Start date cannot be converted to datetime.datetime: invalid str format.")

#         #     if type(start_date) != datetime.datetime:
#         #         raise TypeError("Start date not of type datetime.datetime.")

#         #     if start_date < self._MIN_START_DATE:
#         #         raise ValueError("Timestamp ranges between 1970 -> 2038")

#         #     if type(end_date) == str:
#         #         if end_date.upper() == "NOW":
#         #             end_date = datetime.datetime.now(tz=self._TIMEZONE)
#         #         else:
#         #             try:
#         #                 end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
#         #             except ValueError:
#         #                 raise ValueError("End date cannot be converted to datetime.datetime: invalid str format.")

#         #     if type(end_date) != datetime.datetime:
#         #         raise TypeError("End date is not of type datetime.datetime.")

#         # else:
#         #     if type(period) != str:
#         #         raise TypeError("Period must be of type str.")

#         #     period = period.upper()

#         #     if period not in self._HISTORY_PERIODS:
#         #         raise ValueError("Invalid period.")

#         #     end_date = datetime.datetime.now(tz=self._TIMEZONE)

#         #     if period == 'YTD':
#         #         start_date = end_date.replace(month=1, day=1)

#         #     elif period == 'MAX':
#         #         if share.start_trading_date:
#         #             start_date = share.start_trading_date  # FIXME: see if -1 is needed or not
#         #         else:
#         #             start_date = self._MIN_START_DATE  # FIXME: see what the api does when min < min_trading_date

#         #     else:
#         #         start_date = end_date - self._HISTORY_PERIODS[period]

#         # if interval.upper() not in self._HISTORY_INTERVALS:
#         #     raise ValueError(f"Invalid {interval} interval.")

#         # if type(adjusted) != bool:
#         #     raise TypeError("Parameter adjusted must be of type bool.")

#         # print("start date: ", start_date)
#         # print("end date: ", end_date)

#         # start_timestamp = int(datetime.datetime.timestamp(start_date))  # FIXME: int() is ok w 1m interval?
#         # end_timestamp = int(datetime.datetime.timestamp(end_date))
#         # dt = self._HISTORY_INTERVALS[interval]['dt']
#         # p = self._HISTORY_INTERVALS[interval]['p']
#         # if adjusted:
#         #     adjusted = 1
#         # else:
#         #     adjusted = 0

#         # print("headers", {"symbol": share.symbol,
#         #                   "dt": dt,
#         #                   "p": p,
#         #                   "ajust": adjusted,
#         #                   "from": start_timestamp,
#         #                   "end": end_timestamp})

#         # url = f'https://wapi.bvb.ro/api/history?symbol={share.symbol}&' \
#         #       f'dt={dt}&' \
#         #       f'p={p}&' \
#         #       f'ajust={adjusted}&' \
#         #       f'from={start_timestamp}&' \
#         #       f'to={end_timestamp}'
#         # headers = {"Referer": "https://bvb.ro/"}

#         # share_history = utils.get_url_response(url=url, headers=headers).json()

#         # if format == 'json':
#         #     return share_history
#         # elif format == 'dataframe':
#         #     df = pd.DataFrame(share_history) \
#         #         .rename(columns={"t": "date", "o": "open", "h": "high", "l": "low", "c": "closing", "v": "volume"})
#         #     df.date = df.date.map(lambda timestamp: datetime.datetime.fromtimestamp(timestamp, tz=self._TIMEZONE))
#         #     return df.set_index("date") \
#         #         .drop(columns=["s"])
#         pass


def __preprocess_SharesListForDownload_header(current_header: str) -> list:
    """Preprocessing consists of splitting the string header into a list and
    mapping RO headers to EN headers if needed.

    Args:
        current_header (str): the current headers (first row from downloaded file)

    Returns:
        list: this contains the preprocessed headers
    """
    
    # the problem is with English vs Romanian files:
    # the same link can return RO or EN headers depending on the session / cookie
    # the mappings were created in Feb 2024 by downloading both RO and EN files from BVB
    ro_en_mappings = {
        'Simbol': 'Symbol',
        'Denumire emisiune':  'Security name',
        'ISIN': 'ISIN',
        'Emitent': 'Issuer',
        'Cod Fiscal / CUI': 'Fiscal / Unique Code',
        'Actiuni': 'Shares',
        'Valoare nominala': 'Face value',
        'Cod CAEN': 'CAEN Code',
        'Judet': 'District',
        'Tara': 'Country',
        'Sectiune bursa': 'Exchange segment',
        'Piata Principala': 'Main Market',
        'Categoria': 'Tier',
        'Stare': 'Status',
        'Model tranzactionare': 'Trading Model Type',
        'Lista pasi de pret': 'Price steps list'
    }

    # 1. split the header with delimiter ";"
    preproc_headers = current_header.split(";")

    # 2. remove any trailing spaces
    for header in range(len(preproc_headers)):
        preproc_headers[header] = preproc_headers[header].strip()

    # 3. if headers are in RO, apply EN mappings
    if 'Simbol' in preproc_headers:
        for header in range(len(preproc_headers)):
            try:
                preproc_headers[header] = ro_en_mappings[preproc_headers[header]]
            except KeyError:
                warnings.warn(
                    f'[Header Preprocessing] Unfound English mapping for Romanian header "{preproc_headers[header]}"')

    return preproc_headers

def __validate_SharesListForDownload_header(current_header_list: list):
    """Check if the expected columns appear in the downloaded file. These are:
        - 'Symbol',
        - 'Security name',
        - 'ISIN',
        - 'Issuer',
        - 'Fiscal / Unique Code',
        - 'Shares',
        - 'Face value',
        - 'CAEN Code',
        - 'District',
        - 'Country',
        - 'Exchange segment',
        - 'Main Market',
        - 'Tier',
        - 'Status',
        - 'Trading Model Type',
        - 'Price steps list'

    Obs. The order doesn't matter. If there are additional columns, it doesn't matter either but those won't be processed.

    Args:
        current_header_list (list): The list of current headers

    Raises:
        KeyError: when an expected column is not in current_header_list
    """
    
    expected_header_list = [
        'Symbol',
        'Security name',
        'ISIN',
        'Issuer',
        'Fiscal / Unique Code',
        'Shares',
        'Face value',
        'CAEN Code',
        'District',
        'Country',
        'Exchange segment',
        'Main Market',
        'Tier',
        'Status',
        'Trading Model Type',
        'Price steps list'
    ]

    for expected_header in expected_header_list:
        if expected_header not in current_header_list:
            raise KeyError(f'[Header list validation] Expected column "{expected_header}" not found among actual header columns')

def __get_sector_and_industry(symbol:str) -> set:
    """Calls the symbol wapi of BVB and scrapes the industry and sector company attributes.

    Args:
        symbol (str): The symbol of a valid share on BVB

    Returns:
        set: first item is the sector and the second one the industry.
    """
    _BASE_URL = "https://wapi.bvb.ro/api/symbols?symbol="
    _REQUEST_HEADERS = {'Referer': 'https://www.bvb.ro/'}

    share_data = utils.get_url_response(_BASE_URL + symbol, _REQUEST_HEADERS).json()

    return (share_data["sector"], share_data["industry"])


def get_all_shares():
    _URL = "https://www.bvb.ro/FinancialInstruments/Markets/SharesListForDownload.ashx"

    # returns a csv that has \r\n line endings and ; separator
    response = utils.get_url_response(_URL).text
    # the last line has also \r\n ending => the additional empty row should be deleted
    response_lines = response.split("\r\n")[:-1]

    # preprocess & check header
    header_list = __preprocess_SharesListForDownload_header(
        response_lines[0]  # response_lines[0] == the header
    )
    __validate_SharesListForDownload_header(header_list)

    # save the index of the columns in the header list
    company_headers_index = {
        "Issuer": header_list.index("Issuer"),  # Company.name
        "Fiscal / Unique Code": header_list.index("Fiscal / Unique Code"),  # Company.fiscal_code
        "CAEN Code": header_list.index("CAEN Code"),  # Company.caen_code
        "District": header_list.index("District"),  # Company.district
        "Country": header_list.index("Country"),  # Company.country_iso2
    }
    symbol_headers_index = {
        "Symbol": header_list.index("Symbol"),  # Share.symbol
        "ISIN": header_list.index("ISIN"),  # Share.isin
        "Security name": header_list.index("Security name"),  # Share.name
        "Shares": header_list.index("Shares"),  # Share.total_shares
        "Face value": header_list.index("Face value"),  # Share.face_value
        "Exchange segment": header_list.index("Exchange segment"),  # Share.segment
        "Main Market": header_list.index("Main Market"),  # Share.market
        "Tier": header_list.index("Tier"),  # Share.tier
    }

    share_list = []
    
    # for each response line create the Company and Share objects
    for response_line in response_lines[1:]: # except header row

        try:

            response_line_list = response_line.split(";")

            # get sector and industry
            sector, industry = __get_sector_and_industry(response_line_list[symbol_headers_index["Symbol"]])

            # create the Company object
            company = Company(
                name=response_line_list[company_headers_index["Issuer"]], 
                fiscal_code=response_line_list[company_headers_index["Fiscal / Unique Code"]],
                caen_code=response_line_list[company_headers_index["CAEN Code"]],
                district=response_line_list[company_headers_index["District"]],
                country_iso2=response_line_list[company_headers_index["Country"]],
                sector=sector,
                industry=industry
            )

            # create the Share object
            share = Share(
                symbol=response_line_list[symbol_headers_index["Symbol"]],
                isin=response_line_list[symbol_headers_index["ISIN"]],
                name=response_line_list[symbol_headers_index["Security name"]],
                company=company,
                total_shares=response_line_list[symbol_headers_index["Shares"]],
                face_value=response_line_list[symbol_headers_index["Face value"]],
                segment=response_line_list[symbol_headers_index["Exchange segment"]],
                market=response_line_list[symbol_headers_index["Main Market"]],
                tier=response_line_list[symbol_headers_index["Tier"]],
            )
        except Exception as e:
            raise Exception(f"[Exception at line beginning with '{response_line_list[0]}'] ")
        share_list.append(share)

    return share_list


def __get_company_info(symbol:str) -> dict:
    """Gets the following information from the "Issuer profile" ("Emitent") section of the page of a share on BVB"
            * commerce_registry_code
            * address
            * website
            * email
            * activity field
            * description
            * shareholders
    Args:
        symbol (str): The symbol of a valid share on BVB

    Returns:
        dict: containing the above information. The keys correspond to the list above.
    """
    _COMPANY_INFO_BUTTON = "Emitent"

    # get data from the Issuer profile tab
    html = utils.post_response_instrument_details_form(
        symbol=symbol,
        button=_COMPANY_INFO_BUTTON,
        form_id="aspnetForm"
    )

    # create a soup object on it
    soup = BeautifulSoup(html, 'html.parser')

    company_info = {}

    # issuer profile
    profile_table = soup.find("table", {"id": "ctl00_body_ctl02_CompanyProfile_dvIssProfile"})

    _NEEDED_PROFILE_INFO = {
        'Cod Registrul Comertului': 'commerce_registry_code',
        'Adresa': 'address',
        'Website': 'website',
        'E-mail': 'email',
        'Domeniu de activitate': 'activity_field'
    }

    for tr in profile_table.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) != 2:
            raise ValueError("A tr element does not have exactly two td elements in company profile")

        key = tds[0].text
        if key in _NEEDED_PROFILE_INFO:
            if key == "Website":
                val = tds[1].find("a")['href']
            else:
                val = tds[1].text.replace("\r\n", "").strip()
            company_info[_NEEDED_PROFILE_INFO[key]] = val

    # issuer description
    description_div = soup.find("div", {"id": "ctl00_body_ctl02_CompanyProfile_CDescription"})
    if description_div:
        description_span = description_div.find_all("span", {"lang": "EN-US"})
        desc_text = ""
        for span in description_span:
            desc_text += span.text

        company_info["description"] = desc_text

    # shareholders
    shareholders = soup.find("table", {"id": "gvDetails"})
    if shareholders:
        shareholder_list = []
        trs = shareholders.find_all("tr")
        headers = [th.text for th in trs[0].find_all("th")]
        for tr in trs[1:-1]:
            shareholder_dict = {}
            tds = tr.find_all("td")
            for h in range(0, len(headers)):
                shareholder_dict[headers[h]] = tds[h].text
            shareholder_list.append(shareholder_dict)

        company_info["shareholders"] = shareholder_list

    return company_info


def get_share_info(symbol: str):
        
    # get website, address, etc.
    return __get_company_info(symbol=symbol)