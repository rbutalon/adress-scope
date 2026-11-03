import ipaddress
import math


def validate_ip(value, version=None):
    """Return a canonical IP string, or None for missing/invalid values."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        address = ipaddress.ip_address(value.strip())
    except ValueError:
        return None
    if version is not None and address.version != version:
        return None
    return str(address)


def validate_coordinates(latitude, longitude):
    """Return ``(lat, lon)`` as floats when both are valid, else ``(None, None)``.

    Coordinates arrive from an external service, so they are range-checked
    before reaching the map. Non-finite values (NaN, infinity) are rejected.
    """
    lat = _coordinate(latitude, 90)
    lon = _coordinate(longitude, 180)
    if lat is None or lon is None:
        return None, None
    return lat, lon


def _coordinate(value, limit):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or abs(number) > limit:
        return None
    return number
