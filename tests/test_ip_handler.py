from app.api_client import ApiClientError
from app.ip_handler import collect_ip_info


class Client:
    def __init__(self, values): self.values = values
    def lookup_family(self, version):
        value = self.values.get(version)
        if isinstance(value, Exception): raise value
        return value


def metadata(ip):
    return (ip, {"city": "Example City", "country_name": "Exampleland", "country_code": "EX", "asn": "AS64500", "org": "Example Network"})


def test_both_families_and_metadata():
    result = collect_ip_info(Client({4: metadata("192.0.2.4"), 6: metadata("2001:db8::4")}))
    assert result["success"] is True
    assert result["ipv4"]["available"] and result["ipv6"]["available"]
    assert result["location"]["city"] == "Example City"
    assert result["network"]["asn"] == "AS64500"


def test_partial_availability_is_successful():
    result = collect_ip_info(Client({4: metadata("192.0.2.4"), 6: None}))
    assert result["success"] is True
    assert result["ipv6"]["available"] is False


def test_both_unavailable_is_failure():
    result = collect_ip_info(Client({4: ApiClientError("offline", "connection"), 6: None}))
    assert result["success"] is False
