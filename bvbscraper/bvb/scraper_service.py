from share import Share
from company import Company
from utils import share_utils as utils
import pytz
import datetime
import dateutil.relativedelta as relativedelta
import warnings
import logging



class ScraperService:

    def __preprocess_SharesListForDownload_header(self, current_header: str) -> list:
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

    def __validate_SharesListForDownload_header(self, current_header_list: list):
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

    def __get_sector_industry_tz(self, symbol:str) -> set:
        """Calls the symbol wapi of BVB and scrapes the industry and sector company attributes.

        Args:
            symbol (str): The symbol of a valid share on BVB

        Returns:
            set: first item is the sector and the second one the industry.
        """
        _BASE_URL = "https://wapi.bvb.ro/api/symbols?symbol="
        _REQUEST_HEADERS = {'Referer': 'https://www.bvb.ro/'}

        share_data = utils.get_url_response(_BASE_URL + symbol, _REQUEST_HEADERS).json()

        return (share_data["sector"], share_data["industry"], share_data["timezone"])

    def get_share_info(self, symbol: str | list = 'ALL') -> list:
        """Function to download information about a share from the BVB market:
            * Symbol (ticker)
            * ISIN code
            * Security name
            * Total number of shares
            * Face value
            * Segment
            * Market
            * Tier
            * Company information:
                * Issuer's name
                * Fiscal code
                * CAEN code
                * District
                * Country ISO 2 code
                * Sector
                * Industry
                * Timezone

        Args:
            symbol (str): the ticker(s) about that info is needed to be downloaded. This can be given as:
                            * list of symbols (all str) e.g. ['AAG', 'H2O']
                            * a single str e.g. 'AAG'
                            * or 'ALL' (default) which will download all shares from BVB

        Returns:
            list: consisting of Share objects created based on the inputted symbol parameter.
            This will return only the valid shares from the input.
        """

        # Check the symbol input's type.  
        # The content of the str doesn't needs to be validated, because of how the processing is implemented
        # It will process the whole file, but won't create objects if valid Symbol not in symbol parameter.
        if not (type(symbol) == list or type(symbol) == str):
            raise ValueError("The symbol parameter should be of type string or should be a list of str values")

        if type(symbol) == str and symbol != 'ALL':
            symbol = [symbol.upper()] # transform to list so it can be checked with in <list> operator

        # make all symbols upper
        symbol = [s.upper() for s in symbol if type(s) == str] if symbol != 'ALL' else symbol

        _URL = "https://www.bvb.ro/FinancialInstruments/Markets/SharesListForDownload.ashx"

        # returns a csv that has \r\n line endings and ; separator
        response = utils.get_url_response(_URL).text
        # the last line has also \r\n ending => the additional empty row should be deleted
        response_lines = response.split("\r\n")[:-1]

        # preprocess & check header
        header_list = self.__preprocess_SharesListForDownload_header(
            response_lines[0]  # response_lines[0] == the header
        )
        self.__validate_SharesListForDownload_header(header_list)

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
            "Status": header_list.index("Status"), #Share.status
        }

        share_list = []
        
        # for each response line create the Company and Share objects
        for response_line in response_lines[1:]: # except header row
                
            response_line_list = response_line.split(";")

            response_line_symbol = response_line_list[symbol_headers_index["Symbol"]].strip()
            
            if response_line_symbol in symbol or symbol == 'ALL':

                # get sector and industry
                sector, industry, timezone = self.__get_sector_industry_tz(response_line_list[symbol_headers_index["Symbol"]])

                try:
                    # create the Company object
                    company = Company(
                        name=response_line_list[company_headers_index["Issuer"]], 
                        fiscal_code=response_line_list[company_headers_index["Fiscal / Unique Code"]],
                        caen_code=response_line_list[company_headers_index["CAEN Code"]],
                        district=response_line_list[company_headers_index["District"]],
                        country_iso2=response_line_list[company_headers_index["Country"]],
                        sector=sector,
                        industry=industry,
                        timezone=timezone
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
                        status=response_line_list[symbol_headers_index["Status"]],
                    )

                except Exception as e:
                    raise Exception(f"[Exception at line beginning with '{response_line_list[0]}'] ")
            
                share_list.append(share)

        return share_list

    def get_day_of_last_trade(self, share: str, before_ts = None) -> datetime.datetime.timestamp:
        """Function to retrieve the last timestamp for that the specific share had trades recorded.

        Args:
            share (str): The symbol (ticker) of the share

        Returns:
            datetime.datetime.timestamp: the timestamp of the last trade
        """
        if before_ts:
            lookup_ts = before_ts
        else:
            lookup_ts = int(datetime.datetime.timestamp(datetime.datetime.now()))

        url = f"https://wapi.bvb.ro/api/history?symbol={share}&dt=DAILY&p=day&ajust=1&from={lookup_ts}&to={lookup_ts}"
        header = {"Referer": "https://bvb.ro/"}

        response = utils.get_url_response(url=url, headers=header).json()

        if response['s'] == "no_data":
            return response["nextTime"]
        else:
            return lookup_ts
        
    
    def get_trading_history(self, 
                              share: str | Share, 
                              period: str = None, 
                              start_date: str = None,
                              end_date: str = None) -> dict:
        """Function to return in a dictionary the daily (adjusted) price statistics of a share, i.e. open, close, low, high and volume.

        Args:
            share (str | Share): the symbol of a share as a string or a Share object. If a symbol is given, the corresponding Share object will be created by executing get_share_info with the given symbol.

            period (str, optional): returns the prices from a given period reported to the current datetime. Defaults to None. If period is given, this will be considered rather than start_date and end_date. Valid periods: 1d, 5d, 1m, 3m, 6m, 1y, 2y, 5y, 10y, YTD, MAX.

            start_date (str, optional): A string in '%Y-%m-%d' format (e.g. 2024-02-18) denoting from which date should the function return the historical prices. Defaults to None. See below the usage at Observations.
            end_date (str, optional): A string in '%Y-%m-%d' format (e.g. 2024-02-18) denoting until which date should the function return the historical prices. Defaults to None. See below the usage at Observations.

            Observations: if period is given, this will be considered, independent of whether the start_date and end_date parameters were given or not. However, if:
                * period = None; start_date = None; end_date = None => all history will be returned, i.e. it equals with period = 'MAX'.
                * period = None; start_date = 'valid_date'; end_date = None => all history will be returned starting with start_date until current date.
                * period = None; start_date = None; end_date = 'valid_date' => all history will be returned until end_date
                * period = None; start_date = 'valid_date'; end_date = 'valid_date' => history between the two dates will be returned.

        Returns:
            dict: the shape of the dictionary will be: 
                * 't' = timpestamp of observations
                * 'o' = opening price
                * 'c' = closing price
                * 'l' = lowest price
                * 'h' = highest price
                * 'v' = volume
                * 's' = status. If this is not 'ok', a ValueError is raised with 'Invalid response'
        """
        
        if not isinstance(share, Share):
            share = self.get_share_info(symbol=share)[0]

        share_tz = pytz.timezone('EUROPE/ATHENS')
        if not share.company.timezone:
            warnings.warn(f"Share object {share.symbol} does not have timezone information. Default of 'Europe/Athens' will be used.")
        else:
            share_tz = pytz.timezone(share.company.timezone)

        valid_period_timedelta_mapping = {
            "1D": datetime.timedelta(days=1),
            "5D": datetime.timedelta(days=5),
            "1M": relativedelta.relativedelta(months=1),
            "3M": relativedelta.relativedelta(months=3),
            "6M": relativedelta.relativedelta(months=6),
            "1Y": relativedelta.relativedelta(years=1),
            "2Y": relativedelta.relativedelta(years=2),
            "5Y": relativedelta.relativedelta(years=5),
            "10Y": relativedelta.relativedelta(years=10),
            "YTD": None,
            "MAX": None
        }

        if period and type(period) != str:
            raise TypeError("The given period should be of type str.")
        

        if period and period.upper() not in valid_period_timedelta_mapping:
            raise TypeError(f"Period ({period}) given, but is not between valid periods: 1d, 5d, 1m, 3m, 6m, 1y, 2y 5y, 10y, YTD, MAX. Please use start_date and end_date for other options.")
        
        if period:
            period = period.upper()

            if period == "YTD":
                end_date = datetime.datetime.now(tz=share_tz)
                start_date = end_date.replace(month=1, day=1)
            elif period == "MAX":
                end_date = datetime.datetime.now(tz=share_tz)
                start_date = datetime.datetime(year=1970, month=1, day=1, tzinfo=share_tz)
            else:
                end_date = datetime.datetime.now(tz=share_tz)
                start_date = end_date - valid_period_timedelta_mapping[period]

        else: ## start_date and end_date should be defined here
            if not (type(start_date) == str or not start_date):
                raise ValueError(f"Start date {start_date} given, but is not of type string.")
            
            if not (type(end_date) == str or not end_date):
                raise ValueError(f"End date {end_date} given, but is not of type string.")

            if start_date:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            else:
                start_date = datetime.datetime(year=1970, month=1, day=1, tzinfo=share_tz) # start at the least possible start_date
            if end_date:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end_date = datetime.datetime.now(tz=share_tz) # get prices until current date

        # transform dates to timestamp
        start_ts = int(datetime.datetime.timestamp(start_date))
        end_ts = int(datetime.datetime.timestamp(end_date))

        logging.info(f"Get trading data for {share.symbol} from {start_ts} ({start_date.date()}) until {end_ts} ({end_date.date()})")

        url = f"https://wapi.bvb.ro/api/history?symbol={share.symbol}&dt=DAILY&p=day&ajust=1&from={start_ts}&to={end_ts}"
        header = {"Referer": "https://bvb.ro/"}

        response = utils.get_url_response(url=url, headers=header).json()

        if response['s'] != 'ok':
            if response['s'] == "no_data":
                warnings.warn(f"No trading data for {share.symbol} in period between {start_date.date()} and {end_date.date()}.")
                response = {
                    't': [],
                    'o': [],
                    'h': [],
                    'l': [],
                    'c': [],
                    'v': [],
                    's': 'ok'
                }
            else:
                raise ValueError(f"Invalid response: {response}")

        return response