import ipaddress


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
