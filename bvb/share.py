import bvb.company
from bvb.base import BaseEntity
import re


class Share(BaseEntity):
    __symbol = None
    __specs = {}  #

    def __init__(self, symbol: str, params: dict = None, **kwargs):
        super().__init__()
        self.symbol = symbol
        if params is not None:
            # order of merge is important, since explicitly given parameters will be considered in case the params and
            # kwargs both contain the same key
            kwargs = params | kwargs
        self.__isin = kwargs.get("isin")
        self.__market = kwargs.get("market")
        self.__company = kwargs.get("company")
        self.__tier = kwargs.get("tier")

    @property
    def symbol(self):
        return self.__symbol

    @symbol.setter
    def symbol(self, symbol: str):
        # symbols in Romania should contain only alpha chars or numbers
        if type(symbol) != str:
            raise TypeError("Symbol should be of type str.")
        else:
            symbol = symbol.replace(' ', '')
            if re.findall("^[a-zA-Z0-9]+$", symbol.replace(' ', '')):
                self.__symbol = symbol.upper()
            else:
                raise ValueError("Share instance cannot be initialized with invalid string")

    @property
    def info(self):
        return {'symbol': self.symbol,
                'isin': self.isin,
                'company': self.company,
                'market': self.market,
                'tier': self.tier}

    @info.setter
    def info(self, info_dict):
        if 'symbol' in info_dict:
            self.symbol = info_dict['symbol']
        if 'isin' in info_dict:
            self.isin = info_dict['isin']
        if 'company' in info_dict:
            self.company = info_dict['company']
        if 'market' in info_dict:
            self.market = info_dict['market']
        if 'tier' in info_dict:
            self.tier = info_dict['tier']

    @property
    def company(self):
        return self.__company

    @company.setter
    def company(self, company):
        if isinstance(company, bvb.company.Company):
            self.__company = company
        else:
            raise TypeError("Company attribute must be of type bvb.company.Company class")

    @property
    def isin(self):
        return self.__isin

    @isin.setter
    def isin(self, isin):
        isin_pattern = "^[A-Z]{2}[A-Z0-9]{9}[0-9]{1}$"
        if type(isin) == str:
            if re.findall(isin_pattern, isin):
                self.__isin = isin
            else:
                raise ValueError("Invalid ISIN code.")
        else:
            raise TypeError("ISIN must be of type str.")

    @property
    def market(self):
        return self.__market

    @market.setter
    def market(self, market):
        if market in ['REGS', 'XRS1', 'XRSI']:
            self.__market = market
        else:
            raise ValueError("Invalid market abbreviation.")

    @property
    def tier(self):
        return self.__tier

    @tier.setter
    def tier(self, tier):
        valid_tiers = ["INT'L", "PREMIUM", "STANDARD", "AERO PREMIUM", "AERO STANDARD", "AERO BASE", "INTL-MTS"]
        if tier in valid_tiers:
            self.__tier = tier
        else:
            raise ValueError("Invalid tier abbreviation.")

    def __repr__(self):
        return f"BVBScraper.Share object <{self.symbol}>"

    def __eq__(self, other):
        return self.symbol == other.symbol
