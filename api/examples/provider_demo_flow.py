from __future__ import annotations

import json
import sys
from http.client import HTTPConnection
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "sample"


def load_json(name: str) -> dict:
    with (DATA_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def post_json(connection: HTTPConnection, path: str, payload: dict) -> tuple[int, dict]:
    connection.request(
        "POST",
        path,
        body=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    response = connection.getresponse()
    data = json.loads(response.read().decode("utf-8"))
    return response.status, data


def get_json(connection: HTTPConnection, path: str) -> tuple[int, dict]:
    connection.request("GET", path)
    response = connection.getresponse()
    data = json.loads(response.read().decode("utf-8"))
    return response.status, data


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    registration = load_json("provider_registration.json")
    observation = load_json("fish_pond_observation.json")
    event_payload = load_json("fish_behavior_event.json")

    connection = HTTPConnection(host, port, timeout=5)

    try:
        result = {}
        result["register"] = post_json(connection, "/v1/providers/register", registration)
        result["observation"] = post_json(connection, "/v1/observations", observation)
        result["event"] = post_json(connection, "/v1/events", event_payload)
        result["recommendation"] = post_json(
            connection,
            "/v1/recommendations/fish-pond",
            {"observation": observation, "last_behavior_event": event_payload},
        )
        provider_id = registration["provider_id"]
        result["status"] = get_json(connection, f"/v1/providers/{provider_id}/status")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
