from datetime import datetime, timezone

from .api_client import ApiClientError, IpApiClient
from .validators import validate_coordinates, validate_ip


EMPTY = {"address": None, "available": False}
PROVIDER = "ipapi.co"
LOCATION_FIELDS = ("city", "region", "country", "country_code", "postal_code", "latitude", "longitude", "timezone")


def _empty_result():
    return {
        "success": True,
        "provider": PROVIDER,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ipv4": dict(EMPTY),
        "ipv6": dict(EMPTY),
        "location": {key: None for key in LOCATION_FIELDS},
        "network": {"asn": None, "organization": None},
        "warnings": [],
    }


def _merge_metadata(result, metadata):
    if not metadata:
        return
    fields = {
        "city": "city", "region": "region", "country_name": "country",
        "country_code": "country_code", "postal": "postal_code", "timezone": "timezone",
    }
    for source, target in fields.items():
        if result["location"][target] is None and metadata.get(source) is not None:
            result["location"][target] = metadata[source]

    latitude, longitude = validate_coordinates(metadata.get("latitude"), metadata.get("longitude"))
    if result["location"]["latitude"] is None and latitude is not None:
        result["location"]["latitude"] = latitude
        result["location"]["longitude"] = longitude

    if result["network"]["asn"] is None:
        result["network"]["asn"] = metadata.get("asn")
    if result["network"]["organization"] is None:
        result["network"]["organization"] = metadata.get("org")


def collect_ip_info(client=None, timeout=8):
    client = client or IpApiClient(timeout=timeout)
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
