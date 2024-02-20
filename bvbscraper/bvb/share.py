from typing import Any
from company import Company
from base import BaseEntity
import re


class Share(BaseEntity):
    __symbol = None

    def __init__(self, 
                 symbol,
                 isin,
                 name,
                 company,
                 total_shares,
                 face_value,
                 market,
                 tier,
                 status,
                 segment=None,
                 ):
        super().__init__()
        self.symbol = symbol
        self.isin = isin
        self.name = name
        self.company = company
        self.total_shares = total_shares
        self.face_value = face_value
        self.segment = segment
        self.market = market
        self.tier = tier
        self.status = status

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
                    raise ValueError(f"Share instance cannot be initialized with invalid string: '{symbol}'")
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
                    raise ValueError(f"Invalid ISIN code: '{isin}'.")
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
                raise TypeError(f"Total shares ({total_shares}) must be integer or convertable to that.")

            if total_shares <= 0:
                raise ValueError(f"Total shares ({total_shares}) must be a non-null positive integer")

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
                face_value = face_value.replace(",", ".")
                if face_value:
                    try:
                        face_value = float(face_value)
                    except ValueError:
                        raise TypeError(f"Face value ({face_value}) cannot be string")
            if type(face_value) == int or type(face_value) == float:
                self.__face_value = face_value

    @property
    def segment(self):
        if '_Share__segment' in vars(self):
            return self.__segment
        return None

    @segment.setter
    def segment(self, segment):
        if segment:
            if segment in ['BSE', 'BER', 'ATS']:
                self.__segment = segment
            else:
                raise ValueError(f"Invalid segment abbreviation: {segment}.")

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
            elif market == '-':
                self.__market = None
            else:
                raise ValueError(f"Invalid market abbreviation: '{market}'.")

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

            tier_ro_en_mappings = {
                "INTL-SMT": "INTL-MTS",
                "AERO BAZA": "AERO BASE"
            }

            tier = tier_ro_en_mappings[tier] if tier in tier_ro_en_mappings else tier

            valid_tiers = ["INT'L", "PREMIUM", "STANDARD", "AERO PREMIUM", "AERO STANDARD", "AERO BASE", "INTL-MTS", "III-R"]
            if tier in valid_tiers:
                self.__tier = tier
            elif tier == '-':
                self.__tier = None
            else:
                raise ValueError(f"Invalid tier abbreviation: {tier}.")
    @property
    def status(self):
        if '_Share__status' in vars(self):
            return self.__status
        return None

    @status.setter
    def status(self, status):
        if status:
            if type(status) != str:
                raise TypeError("Status must be of type str")

            status = status.upper()

            status_ro_en_mappings = {
                "TRANZACTIONABILA": "TRADEABLE",
                "SUSPENDATA": "SUSPENDED"
            }

            if status in status_ro_en_mappings:
                self.__status = status_ro_en_mappings[status]
            else:
                raise ValueError(f"Invalid Status: {status}.")

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
                    'segment': self.segment,
                    'market': self.market,
                    'tier': self.tier,
                    'status': self.status,
                    'company': company,
                }

    def __repr__(self):
        return f"BVBScraper.Share object <{self.symbol}>"

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)