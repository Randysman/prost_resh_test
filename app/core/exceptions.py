class DeribitClientError(Exception):
    """Raised when Deribit API returns an error response."""


class UnsupportedTickerError(ValueError):
    """Raised when an unsupported ticker symbol is requested."""


class PriceNotFoundError(LookupError):
    """Raised when no price records are found for the given query."""