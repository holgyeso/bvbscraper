import re

from bvb.share import Share
from bvb.company import Company
from bvb.utils import share_utils as utils
from bs4 import BeautifulSoup


class ScraperService:
    # _TIMEZONE = pytz.timezone('Europe/Bucharest')
    _ALL_VALUES = ['', 'ALL']

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
                if v.upper() not in possible_values:
                    raise ValueError("The provided '" + v + "' abbreviation is not valid.")
            return [v.upper() for v in value]
        # if it was not a str nor a list, raise error
        else:
            raise TypeError("Market parameter must be a str or list.")

    def __get_symbol_info_wapi(self, share: Share):
        """
        Calls the symbol wapi of BVB and scrapes the industry and sector company attributes
        :param share: a Share object for that information will be retrieved
        :type: bvb.share.Share
        :return: a new Share object that has sector and industry information added
        """
        _URL = "https://wapi.bvb.ro/api/symbols?symbol=" + share.symbol
        _REQUEST_HEADERS = {'Referer': 'https://www.bvb.ro/'}
        data = utils.get_url_response(_URL, _REQUEST_HEADERS).json()  # api returns a json

        # data regarding company -> industry and sector
        share.company.sector = data["sector"]
        share.company.industry = data["industry"]

        # TODO: explore if anything else is needed from this dict

        return share

    def __get_shares_from_share_list(self, market: str or list = 'all', tier: str or list = 'all',
                                     symbol: str or list = 'all'):
        """
        Gets all shares from BVB that are traded in the specified market and tier with some general info
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

        _NEEDED_COLUMNS = {  # info that will be returned about a share
            'symbol': 'SYMBOL',
            'isin': 'ISIN',
            'name': 'SECURITY NAME',  # it is not necessarily the issuer's name
            'total_shares': 'SHARES',
            'face_value': 'FACE VALUE',
        }
        _COMPANY_COLUMNS = {  # info about the company that will be converted into a company object referenced in share
            'name': 'ISSUER',
            'fiscal_code': 'FISCAL / UNIQUE CODE',
            'nace_code': 'CAEN CODE',
            'district': 'DISTRICT',
            'country_iso2': 'COUNTRY'

        }
        _FILTER_COLUMNS = {'symbol': 'SYMBOL', 'tier': 'TIER',
                           'market': 'MAIN MARKET'}  # columns by those data rows will be filtered

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
            'symbol': [],  # will be removed if all symbols must be downloaded
            'market': [],
            'tier': []
        }

        if type(symbol) == str:
            if symbol.upper() != 'ALL':
                symbol = [symbol]

        if type(symbol) == list:
            for sy in symbol:
                if type(sy) == str:
                    if re.findall("^[a-zA-Z0-9]+$", sy):
                        _FILTERS['symbol'].append(sy.upper())

        if not _FILTERS['symbol']:
            del _FILTERS['symbol']

        market_filter_values = self._standardize_list_parameter(possible_values=list(_MARKETS), value=market)
        _FILTERS['market'] = [_MARKETS[m] for m in market_filter_values]

        tier_filter_values = self._standardize_list_parameter(possible_values=list(_TIERS), value=tier)
        _FILTERS['tier'] = [_TIERS[t] for t in tier_filter_values]

        # scrape BVB and process the returned csv
        response = utils.get_url_response(_URL).text  # returns a csv that has \r\n line endings and ; separator
        response_lines = response.split("\r\n")  # the first row will be the header and the last one will be ''
        headers = [column.upper() for column in response_lines[0].split(";")]

        # retrieve the index of needed and filter columns; so data could be accessed directly based on index and
        # there will be no need to iterate through the header columns and each row column and check if the header
        # is in _NEEDED_COLUMNS, get its index and based on this get the value from the row.
        _NEEDED_COLUMNS_INDEX = {n: headers.index(_NEEDED_COLUMNS[n]) for n in _NEEDED_COLUMNS}
        _COMPANY_COLUMNS_INDEX = {c: headers.index(_COMPANY_COLUMNS[c]) for c in _COMPANY_COLUMNS}
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
                        try:
                            share_init_dict[col] = data_row[_NEEDED_COLUMNS_INDEX[col]]
                        except IndexError:
                            share_init_dict[col] = None

                    for col in _FILTER_COLUMNS:
                        try:
                            share_init_dict[col] = data_row[_FILTER_COLUMNS_INDEX[col]]
                        except IndexError:
                            share_init_dict[col] = None

                    company_dict = {}
                    for col in _COMPANY_COLUMNS:
                        try:
                            company_dict[col] = data_row[_COMPANY_COLUMNS_INDEX[col]]
                        except IndexError:
                            company_dict[col] = None

                    co_name = company_dict['name']
                    co_fiscal_code = company_dict['fiscal_code']
                    company = Company(name=co_name, fiscal_code=co_fiscal_code, params=company_dict)

                    share_init_dict['company'] = company
                    share_symbol = share_init_dict['symbol']

                    return_values.append(Share(symbol=share_symbol, params=share_init_dict))

        return return_values

    def __get_share_info(self, symbol: str or list = 'all'):
        shares = self.__get_shares_from_share_list(market='all', tier='all', symbol=symbol)
        for share in shares:
            share = self.__get_symbol_info_wapi(share=share)
        return shares

    def __get_detailed_company_info(self, share: Share):
        _BASE_URL = "https://www.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s="
        _COMPANY_INFO_BUTTON = "Issuer profile"


        html = utils.post_response_aspx_form(
            url=_BASE_URL + share.symbol,
            button=_COMPANY_INFO_BUTTON,
            form_id="aspnetForm"
        )

        soup = BeautifulSoup(html, 'html.parser')

        company_info = {}

        # issuer profile
        profile_table = soup.find("table", {"id": "ctl00_body_ctl02_CompanyProfile_dvIssProfile"})

        _NEEDED_PROFILE_INFO = {
            'Commerce Registry Code': 'commerce_registry_code',
            'Address': 'address',
            'Website': 'website',
            'E-mail': 'email',
            'Field of activity': 'activity_field'
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

        for i in company_info:
            share.company.__setattr__(i, company_info[i])

        return share

    def get_shares(self, market: str or list = 'all', tier: str or list = 'all'):
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
        shares = self.__get_shares_from_share_list(market=market, tier=tier)
        for share in shares:
            share = self.__get_symbol_info_wapi(share=share)
        return shares

    def get_share_info(self, symbol: str or list = 'all'):
        return self.__get_share_info(symbol=symbol)

    def get_all_share_info(self, share: Share or list = None, symbol: str or list = None):
        if share is None and symbol is None:
            raise ValueError("One of share and symbol parameters must be given.")

        if share is not None:
            if type(share) == str:
                share = [share]

            if type(share) == list:
                for sh in share:
                    if not isinstance(sh, Share):
                        raise TypeError(f"The provided {sh} share is not of type bvbscraper.bvb.Share.")
        else:
            if type(symbol) == str:
                symbol = [symbol]

            if type(symbol) == list:
                share = self.get_share_info(symbol=symbol)

        for sh in share:
            sh = self.__get_detailed_company_info(share=sh)

        return share
