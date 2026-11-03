from app.validators import validate_coordinates, validate_ip


def test_valid_ipv4():
    assert validate_ip("192.0.2.14", 4) == "192.0.2.14"


def test_invalid_ipv4():
    assert validate_ip("192.0.2.999", 4) is None


def test_valid_ipv6():
    assert validate_ip("2001:db8::14", 6) == "2001:db8::14"


def test_invalid_ipv6():
    assert validate_ip("2001:db8:not-an-ip", 6) is None


def test_valid_coordinates_are_floats():
    assert validate_coordinates("37.7749", -122.4194) == (37.7749, -122.4194)


def test_equator_and_prime_meridian_are_valid():
    assert validate_coordinates(0, 0) == (0.0, 0.0)


def test_coordinates_out_of_range_are_rejected():
    assert validate_coordinates(91, 0) == (None, None)
    assert validate_coordinates(0, 181) == (None, None)


def test_coordinates_reject_missing_or_non_numeric():
    assert validate_coordinates(None, 10) == (None, None)
    assert validate_coordinates("north", 10) == (None, None)
    assert validate_coordinates(True, 10) == (None, None)
    assert validate_coordinates("nan", 10) == (None, None)
