from bvb.base import BaseEntity
import re

class Share(BaseEntity):
    __symbol = None
    __info = {}

    def __init__(self, symbol: str, params: dict = None, **kwargs):
        super().__init__()
        self.symbol = symbol
        if params is not None:
            # order of merge is important, since explicitly given parameters will be considered in case the params and
            # kwargs both contain the same key
            kwargs = params | kwargs
        self.__info['isin'] = kwargs.get("isin")
        self.__info['market'] = kwargs.get("market")
        self.__info['company'] = kwargs.get("company")
        self.__info['tier'] = kwargs.get("tier")
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
        return self.__info

    @info.setter
    def info(self, info_dict):
        self.__info = info_dict

    @property
    def company(self):
        if 'company' in self.__info:
            return self.__info['company']
        else:
            return None

    @company.setter
    def company(self, company):
        self.__info['company'] = company
    # @property
    # def company(self):
    #     return self.__info['company']
    #
    # @company.setter
    # def company(self, company: str):
    #     if company != '':
    #         if type(company) != str:
    #             raise TypeError("Company should be of type str.")
    #         self.__info['company'] = company
    #     else:
    #         raise ValueError("Company should have a value.")

    def __repr__(self):
        return f"BVBScraper.Share object <{self.symbol}>"

    def __eq__(self, other):
        return self.symbol == other.symbol
