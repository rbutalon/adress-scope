# IPv4/IPv6 Address Information System

AddressScope is a Flask web dashboard that retrieves the public address visible to the internet and presents available geolocation and network context. It is built for Cisco DEVASC Project Activity 3, Option 2.

## Objectives

- Identify the currently visible public IPv4 and IPv6 addresses.
- Validate returned addresses before displaying them.
- Present location, ASN, and organization fields clearly.
- Keep external API communication in the Python backend.
- Handle missing connectivity, rate limits, malformed data, and missing fields safely.

## Features

- Independent IPv4 and IPv6 lookup attempts.
- Responsive dashboard with availability indicators.
- Location and network metadata sections.
- Check, refresh, and clipboard copy actions.
- User-safe error and unavailable states.
- Repeatable pytest suite with mocked external responses.

## Technology and API

Python 3, Flask, requests, HTML5, CSS3, and JavaScript. Data is provided by [ipapi.co](https://ipapi.co/api/). The implementation uses the documented `GET https://ipapi.co/json/` caller lookup and `GET https://ipapi.co/{ip}/json/` address lookup format. The caller endpoint returns one address for the network path selected by the operating system; the application validates its IP family instead of pretending one response contains both families.

The free API has rate limits and can return HTTP 429. IPv6 availability depends on the host network and resolver. A missing IPv6 route is a valid unavailable state, not a backend crash.

## Structure

```text
ip-address-information/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── api_client.py
│   ├── display.py
│   ├── ip_handler.py
│   ├── routes.py
│   └── validators.py
├── templates/ (index.html, about.html)
├── static/ (css/style.css, js/script.js)
└── tests/ (validator, API, handler, and route tests)
```

## Installation and use

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), then select **Check my IP**. Use **Refresh** for a new lookup and **Copy** on an available address to copy it.

## Testing

```bash
pytest -v
```

Tests do not call the internet. API responses, invalid JSON, HTTP failures, rate limits, timeouts, connection failures, partial data, and route behavior are mocked.

## Example output

The dashboard displays a validated address such as a value returned by the live service. It never substitutes a hardcoded sample address. If a family is unavailable, its card says `Unavailable` and explains that connectivity was not detected.

## Error handling and limitations

The backend maps network failures and malformed API responses into user-safe messages and returns HTTP 503 only when neither address family can be retrieved. Location fields may be absent in the provider response. The organization field is reported as the provider's `org` value and is not presented as a guaranteed ISP identity. Because ipapi.co documents a single caller endpoint rather than separate family-specific paths, family detection follows the host's selected network route and verifies the returned family.

## Future enhancements

Manual IP lookup, connectivity diagnostics, address history, TXT/CSV export, IPv4/IPv6 comparison, scheduled refresh, additional network reporting, richer visualization, diagnostic tools, and configurable dashboard settings are intentionally left as backlog items.

## GitHub collaboration

Suggested branches are `main`, `feature/ipv4-detection`, `feature/ipv6-detection`, `feature/api-integration`, `feature/web-dashboard`, and `feature/testing`. Keep pull requests focused, run `pytest -v`, request review, and merge only after the checks pass. Suggested commits include `Add validated IP family lookup`, `Build dashboard address cards`, and `Add mocked API and route tests`. No remote repository is configured by this project.
