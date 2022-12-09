from bvb.base import BaseEntity


class Share(BaseEntity):
    symbol = None
    isin = None
    market = None
    tier = None
    company = None

    def __init__(self, symbol: str, params: dict = None, **kwargs):
        super().__init__()
        self.symbol = symbol
        if params is not None:
            # order of merge is important, since explicitly given parameters will be considered in case the params and
            # kwargs both contain the same key
            kwargs = params | kwargs
        self.isin = kwargs.get("isin")
        self.market = kwargs.get("market")
        self.company = kwargs.get("company")
        self.tier = kwargs.get("tier")

    def __repr__(self):
        return f"BVBScraper.Share object <{self.symbol}>"

    def __eq__(self, other):
        return self.symbol == other.symbol
