from app.validators import validate_ip


def test_valid_ipv4():
    assert validate_ip("192.0.2.14", 4) == "192.0.2.14"


def test_invalid_ipv4():
    assert validate_ip("192.0.2.999", 4) is None


def test_valid_ipv6():
    assert validate_ip("2001:db8::14", 6) == "2001:db8::14"


def test_invalid_ipv6():
    assert validate_ip("2001:db8:not-an-ip", 6) is None
