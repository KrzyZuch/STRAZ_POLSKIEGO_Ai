from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.utils import append_provider_suffix, replace_provider_environment  # noqa: E402

DATA_DIR = ROOT / "data" / "sample"


def normalize_base_url(base_url: str) -> str:
    normalized = base_url.strip()
    if not normalized:
        raise ValueError("Base URL nie może być pusty.")
    if not normalized.startswith(("http://", "https://")):
        normalized = f"https://{normalized}"
    return normalized.rstrip("/")


def load_json(name: str) -> dict[str, Any]:
    with (DATA_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def build_provider_id(prefix: str, suffix: str | None = None) -> str:
    safe_suffix = suffix or str(int(time.time() * 1000))
    return append_provider_suffix(prefix, safe_suffix)


def prepare_demo_payloads(
    suffix: str | None = None,
    provider_environment: str = "demo",
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registration = load_json("provider_registration.json")
    observation = load_json("fish_pond_observation.json")
    event_payload = load_json("fish_behavior_event.json")

    provider_id = replace_provider_environment(registration["provider_id"], provider_environment)
    provider_id = build_provider_id(provider_id, suffix)
    registration["provider_id"] = provider_id
    observation["provider"]["provider_id"] = provider_id
    event_payload["provider"]["provider_id"] = provider_id
    return registration, observation, event_payload


def request_json(
    base_url: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: int = 15,
) -> tuple[int, dict[str, Any]]:
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["X-Provider-Token"] = token

    body: bytes | None = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    request = Request(
        f"{normalize_base_url(base_url)}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            data = json.loads(response.read().decode("utf-8"))
            return status, data
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8")
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            data = {"error": raw_body or str(exc)}
        return exc.code, data


def expect_status(actual: int, expected: int, operation: str) -> None:
    if actual != expected:
        raise RuntimeError(
            f"Nieoczekiwany status dla {operation}: expected={expected}, actual={actual}"
        )


def run_smoke_test(
    base_url: str,
    timeout: int = 15,
    provider_environment: str = "demo",
) -> dict[str, Any]:
    registration, observation, event_payload = prepare_demo_payloads(
        provider_environment=provider_environment,
    )
    provider_id = registration["provider_id"]

    result: dict[str, Any] = {"base_url": normalize_base_url(base_url)}

    register_status, register_data = request_json(
        base_url,
        "POST",
        "/v1/providers/register",
        registration,
        timeout=timeout,
    )
    expect_status(register_status, 201, "provider register")
    result["register"] = {"status": register_status, "data": register_data}

    token = register_data["write_token"]
    rotate_status, rotate_data = request_json(
        base_url,
        "POST",
        f"/v1/providers/{provider_id}/tokens/rotate",
        {},
        token=token,
        timeout=timeout,
    )
    expect_status(rotate_status, 200, "provider token rotate")
    result["rotate"] = {"status": rotate_status, "data": rotate_data}
    token = rotate_data["write_token"]

    observation_status, observation_data = request_json(
        base_url,
        "POST",
        "/v1/observations",
        observation,
        token=token,
        timeout=timeout,
    )
    expect_status(observation_status, 202, "observation")
    result["observation"] = {"status": observation_status, "data": observation_data}

    event_status, event_data = request_json(
        base_url,
        "POST",
        "/v1/events",
        event_payload,
        token=token,
        timeout=timeout,
    )
    expect_status(event_status, 202, "event")
    result["event"] = {"status": event_status, "data": event_data}

    recommendation_status, recommendation_data = request_json(
        base_url,
        "POST",
        "/v1/recommendations/fish-pond",
        {"observation": observation, "last_behavior_event": event_payload},
        token=token,
        timeout=timeout,
    )
    expect_status(recommendation_status, 200, "recommendation")
    result["recommendation"] = {
        "status": recommendation_status,
        "data": recommendation_data,
    }

    status_status, status_data = request_json(
        base_url,
        "GET",
        f"/v1/providers/{provider_id}/status",
        timeout=timeout,
    )
    expect_status(status_status, 200, "provider status")
    result["status"] = {"status": status_status, "data": status_data}
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smoke test dla publicznego endpointu Cloudflare / Workers."
    )
    parser.add_argument(
        "base_url",
        help="Bazowy adres wdrożonego API, np. https://fish-pond-api-v1.<subdomain>.workers.dev",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout pojedynczego żądania w sekundach.",
    )
    parser.add_argument(
        "--provider-environment",
        default="demo",
        help="Environment wpisywany do provider_id podczas smoke testu.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_smoke_test(
            args.base_url,
            timeout=args.timeout,
            provider_environment=args.provider_environment,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
