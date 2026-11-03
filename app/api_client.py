import requests

from .validators import validate_ip

BASE_URL = "https://ipapi.co"


class ApiClientError(Exception):
    """A user-safe error raised while contacting ipapi.co."""

    def __init__(self, message, kind="api"):
        super().__init__(message)
        self.kind = kind


class IpApiClient:
    def __init__(self, timeout=8, session=None):
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json", "User-Agent": "IP-Address-Information/1.0"})
        self._caller_data = None

    def _get_json(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)
        except requests.Timeout as exc:
            raise ApiClientError("The IP service took too long to respond.", "timeout") from exc
        except requests.ConnectionError as exc:
            raise ApiClientError("The IP service could not be reached.", "connection") from exc
        except requests.RequestException as exc:
            raise ApiClientError("The IP service request failed.", "request") from exc

        if response.status_code == 429:
            raise ApiClientError("The IP service rate limit was reached. Try again later.", "rate_limit")
        if not 200 <= response.status_code < 300:
            raise ApiClientError(f"The IP service returned HTTP {response.status_code}.", "http")
        try:
            data = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError) as exc:
            raise ApiClientError("The IP service returned invalid data.", "invalid_json") from exc
        if not isinstance(data, dict):
            raise ApiClientError("The IP service returned an unexpected response.", "invalid_response")
        if data.get("error"):
            raise ApiClientError(data.get("reason") or "The IP service reported an error.", "api")
        return data

    def lookup_family(self, version):
        """Ask the caller-IP endpoint for the current address and verify its family.

        ipapi.co documents one caller endpoint, not separate IPv4/IPv6 paths. The
        response is therefore checked rather than assuming it contains both types.
        The operating system's HTTP resolver chooses the available network family.
        The caller response is cached so checking both families costs one request.
        """
        if self._caller_data is None:
            self._caller_data = self._get_json(f"{BASE_URL}/json/")
        data = self._caller_data
        address = validate_ip(data.get("ip"), version)
        if address is None:
            return None
        return address, data

    def lookup_address(self, address):
        data = self._get_json(f"{BASE_URL}/{address}/json/")
        returned = validate_ip(data.get("ip"))
        if returned != address:
            raise ApiClientError("The IP service returned mismatched address data.", "invalid_response")
        return data
