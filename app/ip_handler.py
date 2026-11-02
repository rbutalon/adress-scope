from .api_client import ApiClientError, IpApiClient
from .validators import validate_ip


EMPTY = {"address": None, "available": False}


def _empty_result():
    return {
        "success": True,
        "ipv4": dict(EMPTY),
        "ipv6": dict(EMPTY),
        "location": {key: None for key in ("city", "region", "country", "country_code", "postal_code", "latitude", "longitude", "timezone")},
        "network": {"asn": None, "organization": None},
        "warnings": [],
    }


def _merge_metadata(result, metadata):
    if not metadata:
        return
    fields = {
        "city": "city", "region": "region", "country_name": "country",
        "country_code": "country_code", "postal": "postal_code", "latitude": "latitude",
        "longitude": "longitude", "timezone": "timezone",
    }
    for source, target in fields.items():
        if result["location"][target] is None and metadata.get(source) is not None:
            result["location"][target] = metadata[source]
    if result["network"]["asn"] is None:
        result["network"]["asn"] = metadata.get("asn")
    if result["network"]["organization"] is None:
        result["network"]["organization"] = metadata.get("org")


def collect_ip_info(client=None):
    client = client or IpApiClient()
    result = _empty_result()
    for version, key in ((4, "ipv4"), (6, "ipv6")):
        try:
            found = client.lookup_family(version)
            if found:
                address, metadata = found
                result[key] = {"address": validate_ip(address, version), "available": True}
                _merge_metadata(result, metadata)
        except ApiClientError as exc:
            result["warnings"].append({"family": key, "message": str(exc), "kind": exc.kind})
    if result["warnings"] and not result["ipv4"]["available"] and not result["ipv6"]["available"]:
        result["success"] = False
        result["message"] = "Unable to retrieve public IP information right now."
    return result
