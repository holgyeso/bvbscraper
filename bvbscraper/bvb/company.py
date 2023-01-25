import re
from typing import Any

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
        self.commerce_registry_code = kwargs.get("commerce_registry_code")
        self.address = kwargs.get("address")
        self.website = kwargs.get("website")
        self.email = kwargs.get("email")
        self.activity_field = kwargs.get("activity_field")
        self.description = kwargs.get("description")
        self.shareholders = kwargs.get("shareholders")

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
    def commerce_registry_code(self):
        if '_Company__commerce_registry_code' in vars(self):
            return self.__commerce_registry_code
        return None

    @commerce_registry_code.setter
    def commerce_registry_code(self, reg_code):
        if reg_code:
            if type(reg_code) != str:
                raise TypeError("Commerce Registry Code must be of type str")

            reg_code = reg_code.upper()

            if re.findall(r"^[JCF][0-9]{2}/[0-9]+/[0-9]{4}", reg_code):
                self.__commerce_registry_code = reg_code

    @property
    def address(self):
        if '_Company__address' in vars(self):
            return self.__address
        return None

    @address.setter
    def address(self, address):
        if address:
            if type(address) != str:
                raise TypeError("Address must be of type str")
            self.__address = address

    @property
    def website(self):
        if '_Company__website' in vars(self):
            return self.__website
        return None

    @website.setter
    def website(self, website):
        if website:
            if type(website) != str:
                raise TypeError("Website must be of type str")

            self.__website = website

    @property
    def email(self):
        if '_Company__email' in vars(self):
            return self.__email
        return None

    @email.setter
    def email(self, email):
        if email:
            if type(email) != str:
                raise TypeError("Email must be of type str")
            if re.findall(r"^(.+@.+\..+)+", email):
                self.__email = email

    @property
    def activity_field(self):
        if '_Company__activity_field' in vars(self):
            return self.__activity_field
        return None

    @activity_field.setter
    def activity_field(self, activity):
        if activity:
            if type(activity) != str:
                raise TypeError("Field of activity must be of type str")
            self.__activity_field = activity.upper()

    @property
    def description(self):
        if '_Company__description' in vars(self):
            return self.__description
        return None

    @description.setter
    def description(self, desc):
        if desc:
            if type(desc) != str:
                raise TypeError("Description must be of type str")
            self.__description = desc

    @property
    def shareholders(self):
        if '_Company__shareholders' in vars(self):
            return self.__shareholders
        return None

    @shareholders.setter
    def shareholders(self, shareholders):
        if shareholders:
            if type(shareholders) != list:
                raise TypeError("Type of shareholders is defined to be list")
            self.__shareholders = shareholders

    @property
    def info(self):
        return {
            "company_name": self.name,
            "fiscal_code": self.fiscal_code,
            "commerce_registry_code": self.commerce_registry_code,
            "headquarters": self.address,
            "district": self.district,
            "country_iso2": self.country_iso2,
            "nace_code": self.nace_code,
            "sector": self.sector,
            "industry": self.industry,
            "activity_field": self.activity_field,
            "description": self.description,
            "website": self.website,
            "email": self.email,
            "shareholders": self.shareholders
        }

    def __repr__(self):
        return f"BVBScraper.Company object <name={self.__name}>"

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)


