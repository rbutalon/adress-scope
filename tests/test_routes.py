from app import create_app
from app import routes


def test_pages_load():
    client = create_app({"TESTING": True}).test_client()
    assert client.get("/").status_code == 200
    assert client.get("/about").status_code == 200


def test_api_returns_structured_data(monkeypatch):
    payload = {"success": True, "ipv4": {"address": "192.0.2.1", "available": True}, "ipv6": {"address": None, "available": False}, "location": {}, "network": {}, "warnings": []}
    monkeypatch.setattr(routes, "collect_ip_info", lambda **kwargs: payload)
    response = create_app({"TESTING": True}).test_client().get("/api/ip-info")
    assert response.status_code == 200
    assert response.get_json() == payload


def test_api_failure_is_service_unavailable(monkeypatch):
    monkeypatch.setattr(routes, "collect_ip_info", lambda **kwargs: {"success": False, "message": "offline"})
    response = create_app({"TESTING": True}).test_client().get("/api/ip-info")
    assert response.status_code == 503


def test_api_uses_configured_timeout(monkeypatch):
    seen = {}

    def fake_collect(timeout=8):
        seen["timeout"] = timeout
        return {"success": True, "warnings": []}

    monkeypatch.setattr(routes, "collect_ip_info", fake_collect)
    client = create_app({"TESTING": True, "API_TIMEOUT": 3}).test_client()
    assert client.get("/api/ip-info").status_code == 200
    assert seen["timeout"] == 3


def test_health_endpoint():
    response = create_app({"TESTING": True}).test_client().get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
