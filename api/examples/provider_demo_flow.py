from __future__ import annotations

import json
import sys
import time
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.utils import append_provider_suffix, replace_provider_environment  # noqa: E402

DATA_DIR = ROOT / "data" / "sample"


def load_json(name: str) -> dict:
    with (DATA_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def post_json(
    connection: HTTPConnection,
    path: str,
    payload: dict,
    token: str | None = None,
) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["X-Provider-Token"] = token
    connection.request(
        "POST",
        path,
        body=json.dumps(payload).encode("utf-8"),
        headers=headers,
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
    provider_environment = "demo"
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        provider_environment = sys.argv[2]

    registration = load_json("provider_registration.json")
    observation = load_json("fish_pond_observation.json")
    event_payload = load_json("fish_behavior_event.json")
    unique_suffix = int(time.time())
    registration["provider_id"] = replace_provider_environment(
        registration["provider_id"],
        provider_environment,
    )
    registration["provider_id"] = append_provider_suffix(
        registration["provider_id"],
        str(unique_suffix),
    )
    observation["provider"]["provider_id"] = registration["provider_id"]
    event_payload["provider"]["provider_id"] = registration["provider_id"]

    connection = HTTPConnection(host, port, timeout=5)

    try:
        result = {}
        result["register"] = post_json(connection, "/v1/providers/register", registration)
        provider_id = registration["provider_id"]
        token = result["register"][1]["write_token"]
        result["rotate"] = post_json(
            connection,
            f"/v1/providers/{provider_id}/tokens/rotate",
            {},
            token=token,
        )
        token = result["rotate"][1]["write_token"]
        result["observation"] = post_json(
            connection,
            "/v1/observations",
            observation,
            token=token,
        )
        result["event"] = post_json(
            connection,
            "/v1/events",
            event_payload,
            token=token,
        )
        result["recommendation"] = post_json(
            connection,
            "/v1/recommendations/fish-pond",
            {"observation": observation, "last_behavior_event": event_payload},
            token=token,
        )
        result["status"] = get_json(connection, f"/v1/providers/{provider_id}/status")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
