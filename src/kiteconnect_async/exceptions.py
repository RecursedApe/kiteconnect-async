"""
    exceptions.py

    Exceptions raised by the Kite Connect client.

    :copyright: (c) 2021 by Zerodha Technology.
    :license: see LICENSE for details.
"""

class KiteException(Exception):
    """
    Base exception class representing a Kite client exception.

    Every specific Kite client exception is a subclass of this
    and  exposes two instance variables `.code` (HTTP error code)
    and `.message` (error text).
    """

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(KiteException, self).__init__(message)
        self.code = code

class GeneralException(KiteException):
    """An unclassified, general error. Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(GeneralException, self).__init__(message, code)


class TokenException(KiteException):
    """Represents all token and authentication related errors. Default code is 403."""

    def __init__(self, message, code=403):
        """Initialize the exception."""
        super(TokenException, self).__init__(message, code)


class DataException(KiteException):
    """Represents a bad response from the backend Order Management System (OMS). Default code is 502."""

    def __init__(self, message, code=502):
        """Initialize the exception."""
        super(DataException, self).__init__(message, code)