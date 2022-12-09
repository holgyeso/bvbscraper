from bvb.base import BaseEntity


class Company(BaseEntity):
    __name = None

    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.sector = kwargs.get("sector")
        self.industry = kwargs.get("industry")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def sector(self):
        return self.__sector

    @sector.setter
    def sector(self, sector):
        self.__sector = sector

    @property
    def industry(self):
        return self.__industry

    @industry.setter
    def industry(self, industry):
        self.__industry = industry

    @property
    def info(self):
        return {'name': self.__name,
                'sector': self.__sector,
                'industry': self.__industry}

    @info.setter
    def info(self, info_dict):
        if 'name' in info_dict:
            self.name = info_dict['name']
        if 'sector' in info_dict:
            self.sector = info_dict['sector']
        if 'industry' in info_dict:
            self.industry = info_dict['industry']

    def __repr__(self):
        return f"BVBScraper.Company object <name={self.__name}>"
