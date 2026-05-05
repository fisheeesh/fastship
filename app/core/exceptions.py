class FastShipException(Exception):
    """Base exception for all exceptions in fastship api"""


class EntityNotFound(FastShipException):
    """Entity not found in database"""


class BadPassword(FastShipException):
    """Password is not strong enough or invalid"""


class ClientNotAuthorized(FastShipException):
    """Client is not authorized to perform the action"""


class ClientNotVerified(FastShipException):
    """Client is not verified"""


class NothingToUpdate(FastShipException):
    """No data provided to update"""


class BadCredentials(FastShipException):
    """User email or password is incorrect"""


class InvalidToken(FastShipException):
    """Access token is invalid or expired"""


class DeliveryPartnerNotAvailable(FastShipException):
    """Delivery partner/s do not service the destination"""


class DeliveryPartnerCapacityExceeded(FastShipException):
    """Delivery partner has reached their max handling capacity"""
