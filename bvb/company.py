import re

from bvb.base import BaseEntity


class Company(BaseEntity):
    __name = None

    def __init__(self, name, fiscal_code, params: dict = None, **kwargs):
        super().__init__()
        self.name = name
        self.fiscal_code = fiscal_code
        if params is not None:
            kwargs = params | kwargs
        self.nace_code = kwargs.get("nace_code")
        self.district = kwargs.get("district")
        self.country_iso2 = kwargs.get("country_iso2")
        self.sector = kwargs.get("sector")
        self.industry = kwargs.get("industry")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if name:
            if type(name) != str:
                raise TypeError("Company name should be of type str.")
            self.__name = name
        else:
            raise ValueError("Company name must be given.")
    @property
    def fiscal_code(self):
        return self.__fiscal_code

    @fiscal_code.setter
    def fiscal_code(self, fiscal_code):
        if fiscal_code:
            if type(fiscal_code) != str and type(fiscal_code) != int:
                raise TypeError("Company's fiscal code can contain only characters and numbers.")
            if len(str(fiscal_code).strip()) == 0:
                raise ValueError("Fiscal code cannot be empty.")
            self.__fiscal_code = fiscal_code
        else:
            raise ValueError("Fiscal code must be given")

    @property
    def nace_code(self):
        if "_Company__nace_code" in vars(self):
            return self.__nace_code
        return None

    @nace_code.setter
    def nace_code(self, nace_code):
        if nace_code:
            nace_code = nace_code.replace("-", "").strip()

            if type(nace_code) == int:
                nace_code = str(nace_code)

            if re.findall(r"^[0-9]{4}$", nace_code):
                self.__nace_code = nace_code

    @property
    def district(self):
        if '_Company__district' in vars(self):
            return self.__district
        return None

    @district.setter
    def district(self, district):
        if district:
            if type(district) != str:
                raise TypeError("District must be of type str.")
            self.__district = district

    @property
    def country_iso2(self):
        if '_Company__country_iso2' in vars(self):
            return self.__country_iso2
        return None

    @country_iso2.setter
    def country_iso2(self, country_iso2):
        if country_iso2:
            if type(country_iso2) != str:
                raise TypeError("Country's ISO 2 code must be of type str.")
            country_iso2 = country_iso2.upper().strip()
            if re.findall(r"^[A-Z]{2}$", country_iso2):
                self.__country_iso2 = country_iso2
            else:
                raise ValueError("Country's ISO 2 code must contain exactly two alpha characters.")

    @property
    def sector(self):
        if '_Company__sector' not in vars(self):
            return self.__sector
        return  None

    @sector.setter
    def sector(self, sector):
        self.__sector = sector

    @property
    def industry(self):
        if '_Company__industry' not in vars(self):
            return self.__industry
        return None

    @industry.setter
    def industry(self, industry):
        self.__industry = industry

    @property
    def info(self):
        return {
            "company_name": self.name,
            "fiscal_code": self.fiscal_code,
            "nace_code": self.nace_code,
            "district": self.district,
            "country_iso2": self.country_iso2,
            "sector": self.sector,
            "industry": self.industry
        }

    def __repr__(self):
        return f"BVBScraper.Company object <name={self.__name}>"
