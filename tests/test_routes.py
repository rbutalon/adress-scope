from app import create_app
from app import routes


def test_pages_load():
    client = create_app({"TESTING": True}).test_client()
    assert client.get("/").status_code == 200
    assert client.get("/about").status_code == 200


def test_api_returns_structured_data(monkeypatch):
    payload = {"success": True, "ipv4": {"address": "192.0.2.1", "available": True}, "ipv6": {"address": None, "available": False}, "location": {}, "network": {}, "warnings": []}
    monkeypatch.setattr(routes, "collect_ip_info", lambda: payload)
    response = create_app({"TESTING": True}).test_client().get("/api/ip-info")
    assert response.status_code == 200
    assert response.get_json() == payload


def test_api_failure_is_service_unavailable(monkeypatch):
    monkeypatch.setattr(routes, "collect_ip_info", lambda: {"success": False, "message": "offline"})
    response = create_app({"TESTING": True}).test_client().get("/api/ip-info")
    assert response.status_code == 503
