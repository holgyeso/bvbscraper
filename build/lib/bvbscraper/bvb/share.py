import datetime
from typing import Any
from bvbscraper.bvb.company import Company
from bvbscraper.bvb.base import BaseEntity
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
        self.isin = kwargs.get("isin")
        self.name = kwargs.get("name")
        self.company = kwargs.get("company")
        self.total_shares = kwargs.get("total_shares")
        self.face_value = kwargs.get("face_value")
        self.market = kwargs.get("market")
        self.tier = kwargs.get("tier")
        self.start_trading_date = kwargs.get("start_trading_date")

    @property
    def symbol(self):
        return self.__symbol

    @symbol.setter
    def symbol(self, symbol: str):
        # symbols in Romania should contain only alpha chars or numbers
        if symbol:
            if type(symbol) != str:
                raise TypeError("Symbol should be of type str.")
            else:
                symbol = symbol.replace(' ', '')
                if re.findall("^[a-zA-Z0-9]+$", symbol):
                    self.__symbol = symbol.upper()
                else:
                    raise ValueError("Share instance cannot be initialized with invalid string")
        else:
            raise ValueError("Symbol must be given")

    @property
    def isin(self):
        if '_Share__isin' in vars(self):
            return self.__isin
        return None

    @isin.setter
    def isin(self, isin):
        if isin:
            isin_pattern = "^[A-Z]{2}[A-Z0-9]{9}[0-9]{1}$"
            if type(isin) == str:
                if re.findall(isin_pattern, isin):
                    self.__isin = isin
                else:
                    raise ValueError("Invalid ISIN code.")
            else:
                raise TypeError("ISIN must be of type str.")

    @property
    def name(self):
        if '_Share__name' in vars(self):
            return self.__name
        return None

    @name.setter
    def name(self, name):
        if name:
            if type(name) != str:
                raise TypeError("Share name should be of type str.")
            self.__name = name

    @property
    def company(self):
        if '_Share__company' in vars(self):
            return self.__company
        return None

    @company.setter
    def company(self, company):
        if company:
            if isinstance(company, Company):
                self.__company = company
            else:
                raise TypeError("Company attribute must be of type bvb.company.Company class")

    @property
    def total_shares(self):
        if '_Share__total_shares' in vars(self):
            return self.__total_shares
        return None

    @total_shares.setter
    def total_shares(self, total_shares):
        if total_shares:
            try:
                total_shares = int(total_shares)
            except ValueError:
                raise TypeError("Total shares must be integer or convertable to that.")

            if total_shares <= 0:
                raise ValueError("Total shares must be a non-null positive integer")

            self.__total_shares = total_shares

    @property
    def face_value(self):
        if '_Share__face_value' in vars(self):
            return self.__face_value
        return None

    @face_value.setter
    def face_value(self, face_value):
        if face_value:
            if type(face_value) == str:
                face_value = face_value.replace("-", "").strip()
                if face_value:
                    try:
                        face_value = float(face_value)
                    except ValueError:
                        raise TypeError("Face value cannot be string")
            if type(face_value) == int or type(face_value) == float:
                self.__face_value = face_value

    @property
    def market(self):
        if '_Share__market' in vars(self):
            return self.__market
        return None

    @market.setter
    def market(self, market):
        if market:
            if market in ['REGS', 'XRS1', 'XRSI']:
                self.__market = market
            else:
                raise ValueError("Invalid market abbreviation.")

    @property
    def tier(self):
        if '_Share__tier' in vars(self):
            return self.__tier
        return None

    @tier.setter
    def tier(self, tier):
        if tier:
            if type(tier) != str:
                raise TypeError("Tier must be of type str")

            tier = tier.upper()

            valid_tiers = ["INT'L", "PREMIUM", "STANDARD", "AERO PREMIUM", "AERO STANDARD", "AERO BASE", "INTL-MTS"]
            if tier in valid_tiers:
                self.__tier = tier
            else:
                raise ValueError("Invalid tier abbreviation.")

    @property
    def info(self):
        company = None
        if self.company:
            company = self.company.info
        return {
                    'symbol': self.symbol,
                    'isin': self.isin,
                    'share_name': self.name,
                    'total_shares': self.total_shares,
                    'face_value': self.face_value,
                    'market': self.market,
                    'tier': self.tier,
                    'company': company,
                    'start_trading_date': self.start_trading_date
                }

    @property
    def start_trading_date(self):
        if '_Share__start_trading_date' in vars(self):
            return self.__start_trading_date
        return None

    @start_trading_date.setter
    def start_trading_date(self, start_date):
        if start_date:
            if type(start_date) == str:
                try:
                    start_date = datetime.datetime.strptime(start_date, "%m/%d/%Y")
                except ValueError:
                    raise ValueError("Start date cannot be converted to datetime.datetime")

            if type(start_date) == datetime.datetime:
                self.__start_trading_date = start_date

    def __repr__(self):
        return f"BVBScraper.Share object <{self.symbol}>"

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)


