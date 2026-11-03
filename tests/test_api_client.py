import requests
import pytest

from app.api_client import ApiClientError, IpApiClient


class Response:
    def __init__(self, status=200, data=None, error=None):
        self.status_code = status
        self.data = data
        self.error = error

    def json(self):
        if self.error:
            raise ValueError("bad json")
        return self.data


class Session:
    def __init__(self, response=None, error=None):
        self.response, self.error = response, error
        self.headers = {}
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def test_successful_response():
    client = IpApiClient(session=Session(Response(data={"ip": "192.0.2.3"})))
    assert client.lookup_family(4)[0] == "192.0.2.3"


def test_missing_or_wrong_family_is_unavailable():
    client = IpApiClient(session=Session(Response(data={"city": "Example"})))
    assert client.lookup_family(4) is None


def test_caller_lookup_is_cached_between_families():
    session = Session(Response(data={"ip": "192.0.2.3"}))
    client = IpApiClient(session=session)
    client.lookup_family(4)
    client.lookup_family(6)
    assert session.calls == 1


@pytest.mark.parametrize("status,kind", [(429, "rate_limit"), (503, "http")])
def test_http_errors(status, kind):
    with pytest.raises(ApiClientError) as error:
        IpApiClient(session=Session(Response(status=status, data={}))).lookup_family(4)
    assert error.value.kind == kind


def test_invalid_json():
    with pytest.raises(ApiClientError) as error:
        IpApiClient(session=Session(Response(error=True))).lookup_family(4)
    assert error.value.kind == "invalid_json"


@pytest.mark.parametrize("exception,kind", [(requests.Timeout(), "timeout"), (requests.ConnectionError(), "connection")])
def test_network_errors(exception, kind):
    with pytest.raises(ApiClientError) as error:
        IpApiClient(session=Session(error=exception)).lookup_family(4)
    assert error.value.kind == kind
