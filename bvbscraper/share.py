from .base import BaseEntity


class Share(BaseEntity):
    symbol = None
    isin = None
    market = None
    tier = None
    company = None

    def __init__(self, symbol, **kwargs):
        super().__init__()
        self.symbol = symbol
        self.isin = kwargs.get("isin")
        self.market = kwargs.get("market")
        self.company = kwargs.get("company")
        self.tier = kwargs.get("tier")

    def __repr__(self):
        return f"bvbscraper.Share object <{self.symbol}>"

    def __eq__(self, other):
        return self.symbol == other.symbol
