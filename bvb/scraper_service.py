import requests
from requests import Response

from bvb.share import Share
from bvb.company import Company


class ScraperService:
    # _TIMEZONE = pytz.timezone('Europe/Bucharest')
    _ALL_VALUES = ['', 'ALL']

    def _get_url_response(self, url: str, headers: dict = None) -> Response:
        """
        Returns the response of a GET request to the specified URL if it successful.
        :param url: the URL from that information must be retrieved
        :type url: str
        :param headers: special header definition
        :type headers: dict
        :return: the text content of the URL
        :rtype: requests.models.Response object
        :raises ValueError: in case the response is not valid (contains no text or the response code was not 200)
        """
        response = ""
        if headers is None:
            response = requests.get(url)
        else:
            response = requests.get(url, headers=headers)
        if response.status_code != 200 and response.text == '':
            raise ValueError("Response is not valid.")
        return response

    def _standardize_list_parameter(self, possible_values: list, value: str or list):
        """
        The function normalizes the `value` parameter:
            - checks if the value is a valid one (one of the possible_values)
            - if the value symbolizes all possible values, then all possible values will be returned
            - if `value` is a valid possible value, the list representation of this will be returned
            - if `value` is a list and all it's elements are valid, `value` will be returned
        :param possible_values: all valid values that the `value` parameter can have (besides _ALL_VALUES)
        :type possible_values: list
        :param value: the value that must be checked and normalized
        :type value: str or list
        :return: normalized value as list, containing only valid values written with uppercase
        :rtype: list
        :raises ValueError: if the provided value contains invalid elements
        :raises TypeError: if `possible_values` is not list or `values` is not string or list
        """
        if type(possible_values) != list:
            raise TypeError("possible_values parameter should be of type list.")

        # if a single string value was provided
        if type(value) == str:
            value = value.upper()

            # if market param means all, return all possible market values
            if value in self._ALL_VALUES:
                return list(possible_values)

            # if a single market was added, return it as list only if it is a valid market; otherwise raise error.
            else:
                if value in possible_values:
                    return [value]
                else:
                    raise ValueError("The provided '" + value + "' abbreviation is not valid.")

        # if the value is a list and contains valid elements, return value with uppercase, else raise error
        elif type(value) == list:
            for v in value:
                if v not in possible_values:
                    raise ValueError("The provided '" + v + "' abbreviation is not valid.")
            return value
        # if it was not a str nor a list, raise error
        else:
            raise TypeError("Market parameter must be a str or list.")

    def __get_shares(self, market: str or list = 'all', tier: str or list = 'all'):
        """
        Gets all shares from BVB that are traded in the specified market and tier
        :param market: the abbreviation of a BVB market or '' or 'all' representing all markets.
        :type: str or list
        :param tier: the abbreviation of a BVB market tier or '' or 'all' representing all market tiers.
        :return: an array that contains Share instances that match the market and tier criteria

        .. note::
        market abbreviations:
            |    - 'REGS' => Regulated Market
            |    - 'AERO'  => AeRO
            |    - 'MTS' => MTS Intl
        tier abbreviations:
            |   - 'INTL': => REGS Int'l tier
            |   - 'PREMIUM': => REGS Premium
            |   - 'STANDARD': => REGS Standard
            |   - 'AERO_PREMIUM': => AeRO Premium
            |   - 'AERO_STANDARD': => AeRO Standard
            |   - 'AERO_BASE': => AeRO Base
            |   - 'MTS_INTL': => Intl MTS

        The script automatically recognizes needed and filter columns by the column names. If a column is not present
        in a row, it will not be considered.
        """
        _URL = "https://www.bvb.ro/FinancialInstruments/Markets/SharesListForDownload.ashx"

        _NEEDED_COLUMNS = {'symbol': 'SYMBOL', 'isin': 'ISIN'}  # info that will be returned about a share
        _FILTER_COLUMNS = {'tier': 'TIER', 'market': 'MAIN MARKET'}  # columns by those data rows will be filtered

        # market and tier parameter mapping dicts {param_value: scraped_value}
        _MARKETS = {
            'REGS': 'REGS',  # Regulated Market
            'AERO': 'XRS1',  # AeRO
            'MTS': 'XRSI'  # MTS Intl
        }

        _TIERS = {
            'INTL': "INT'L",  # REGS Int'l tier
            'PREMIUM': 'PREMIUM',  # REGS Premium
            'STANDARD': 'STANDARD',  # REGS Standard
            'AERO_PREMIUM': 'AERO PREMIUM',  # AeRO Premium
            'AERO_STANDARD': 'AERO STANDARD',  # AeRO Standard
            'AERO_BASE': 'AERO BASE',  # AeRO Base
            'MTS_INTL': 'INTL-MTS',  # Intl MTS
        }

        # construct the filter dict that contains the possible values of each filter column
        _FILTERS = {
            'market': [],
            'tier': []
        }

        market_filter_values = self._standardize_list_parameter(possible_values=list(_MARKETS), value=market)
        _FILTERS['market'] = [_MARKETS[m] for m in market_filter_values]

        tier_filter_values = self._standardize_list_parameter(possible_values=list(_TIERS), value=tier)
        _FILTERS['tier'] = [_TIERS[t] for t in tier_filter_values]

        # scrape BVB and process the returned csv
        response = self._get_url_response(_URL).text  # returns a csv that has \r\n line endings and ; separator
        response_lines = response.split("\r\n")  # the first row will be the header and the last one will be ''
        headers = [column.upper() for column in response_lines[0].split(";")]

        # retrieve the index of needed and filter columns; so data could be accessed directly based on index and
        # there will be no need to iterate through the header columns and each row column and check if the header
        # is in _NEEDED_COLUMNS, get its index and based on this get the value from the row.
        _NEEDED_COLUMNS_INDEX = {n: headers.index(_NEEDED_COLUMNS[n]) for n in _NEEDED_COLUMNS}
        _FILTER_COLUMNS_INDEX = {f: headers.index(_FILTER_COLUMNS[f]) for f in _FILTER_COLUMNS}

        # first each row in response_lines should be split by ';' then, all filters should be checked, and
        # if the row meets the criteria, the needed information will be selected and a Share instance will be
        # initialized and added to return_values.
        return_values = []

        for row in response_lines[1:-1]:
            data_row = row.split(";")
            if len(data_row) > 1:
                valid_row = True
                # iterate through the filter columns' index and check if the split data row has on the index
                # corresponding to a certain filter column a value that meets the criteria set in _FILTERS for the
                # specific filter column.
                for filter_column in _FILTERS:
                    # if the data row's value in the filter column's index does not belong to possible values of the
                    # specific filter, the row should not be considered
                    filter_index = _FILTER_COLUMNS_INDEX[filter_column]
                    if filter_index >= len(data_row):
                        valid_row = False
                        break
                    else:
                        if data_row[filter_index].upper() not in _FILTERS[filter_column]:
                            valid_row = False
                            break
                if valid_row:
                    share_init_dict = {}

                    for col in _NEEDED_COLUMNS:
                        col_index = _NEEDED_COLUMNS_INDEX[col]
                        if col_index < len(data_row):
                            share_init_dict[col] = data_row[col_index]

                    for col in _FILTER_COLUMNS:
                        share_init_dict[col] = data_row[_FILTER_COLUMNS_INDEX[col]]

                    share_symbol = share_init_dict['symbol']
                    # del share_init_dict['symbol']

                    return_values.append(Share(symbol=share_symbol, params=share_init_dict))

        return return_values

    def get_shares(self, market='all', tier='all'):
        """
        Gets all shares from BVB that are traded in the specified market and tier
        :param market: the abbreviation of a BVB market or '' or 'all' representing all markets.
        :type: str or list
        :param tier: the abbreviation of a BVB market tier or '' or 'all' representing all market tiers.
        :return: an array that contains Share instances that match the market and tier criteria

        .. note::
        market abbreviations:
            |    - 'REGS' => Regulated Market
            |    - 'AERO'  => AeRO
            |    - 'MTS' => MTS Intl
        tier abbreviations:
            |   - 'INTL': => REGS Int'l tier
            |   - 'PREMIUM': => REGS Premium
            |   - 'STANDARD': => REGS Standard
            |   - 'AERO_PREMIUM': => AeRO Premium
            |   - 'AERO_STANDARD': => AeRO Standard
            |   - 'AERO_BASE': => AeRO Base
            |   - 'MTS_INTL': => Intl MTS
        """
        return self.__get_shares(market=market, tier=tier)

    def get_share_info(self, share: Share):
        _URL = "https://wapi.bvb.ro/api/symbols?symbol=" + share.symbol
        _REQUEST_HEADERS = {'Referer': 'https://www.bvb.ro/'}
        data = self._get_url_response(_URL, _REQUEST_HEADERS).json() # api returns a json

        # data["description"] = company name
        company = Company(name=data["description"], sector=data["sector"], industry=data["industry"])
        share.company = company

        return share
