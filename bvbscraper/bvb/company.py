import re
from typing import Any
from bvb.base import BaseEntity

class Company(BaseEntity):
    __name = None

    def __init__(self, name, 
                 fiscal_code, 
                 caen_code=None,
                 district=None, 
                 country_iso2=None, 
                 sector=None,
                 industry=None,
                 timezone=None,
                 ):
        super().__init__()
        self.name = name
        self.fiscal_code = fiscal_code
        self.caen_code = caen_code
        self.district = district
        self.country_iso2 = country_iso2

        self.sector = sector
        self.industry = industry

        self.timezone = timezone

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if name:
            if type(name) != str:
                raise TypeError(f"Company name ({name}) should be of type str.")
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
                raise ValueError(f"Company's fiscal code ({fiscal_code}) can contain only characters and numbers.")
            if len(str(fiscal_code).strip()) == 0:
                raise ValueError("Fiscal code cannot be empty.")
            self.__fiscal_code = fiscal_code
        else:
            raise ValueError("Fiscal code must be given")

    @property
    def caen_code(self):
        if "_Company__caen_code" in vars(self):
            return self.__caen_code
        return None

    @caen_code.setter
    def caen_code(self, caen_code):
        if caen_code:

            if type(caen_code) == int:
                caen_code = str(caen_code)

            caen_code = caen_code.replace("-", "").strip()
            if caen_code:

                if re.findall(r"^[0-9]{4}$", caen_code):
                    self.__caen_code = caen_code

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
                raise TypeError(f"Country's ISO 2 code must be of type str. {country_iso2} doesn't match this pattern.")
            country_iso2 = country_iso2.upper().strip()
            if re.findall(r"^[A-Z]{2}$", country_iso2):
                self.__country_iso2 = country_iso2
            else:
                raise ValueError(f"Country's ISO 2 code must contain exactly two alpha characters. {country_iso2} doesn't match this pattern.")

    @property
    def sector(self):
        if '_Company__sector' in vars(self):
            return self.__sector
        return None

    @sector.setter
    def sector(self, sector):
        if sector:
            if type(sector) != str:
                raise TypeError("Sector must be of type string")
            self.__sector = sector.upper()

    @property
    def industry(self):
        if '_Company__industry' in vars(self):
            return self.__industry
        return None

    @industry.setter
    def industry(self, industry):
        if industry:
            if type(industry) != str:
                raise TypeError("Industry must be of type string")
            self.__industry = industry.upper()

    @property
    def timezone(self):
        if '_Company__timezone' in vars(self):
            return self.__timezone
        return None

    @timezone.setter
    def timezone(self, timezone):
        if timezone:
            if type(timezone) != str:
                raise TypeError("Timezone must be of type string")
            self.__timezone = timezone.upper()


    @property
    def info(self):
        return {
            "company_name": self.name,
            "fiscal_code": self.fiscal_code,
            "district": self.district,
            "country_iso2": self.country_iso2,
            "caen_code": self.caen_code,
            "sector": self.sector,
            "industry": self.industry,
        }

    def __repr__(self):
        return f"BVBScraper.Company object <name={self.__name}>"

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)


