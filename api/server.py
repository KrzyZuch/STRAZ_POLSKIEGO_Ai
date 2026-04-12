from __future__ import annotations

import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.utils import (  # noqa: E402
    ensure_provider_environment_allowed,
    parse_allowed_provider_environments,
    validate_event_payload,
    validate_observation_payload,
    validate_provider_descriptor_payload,
)
from api.storage import (  # noqa: E402
    DEFAULT_DB_PATH,
    OperationalStore,
    ProviderConflictError,
    ProviderNotFoundError,
)
from models.fish_pond.recommendation_engine import generate_recommendation  # noqa: E402


class ProviderEnvironmentPolicyError(Exception):
    pass


class FishPondAPIHandler(BaseHTTPRequestHandler):
    server_version = "FishPondAPIServer/0.2"

    @property
    def store(self) -> OperationalStore:
        return self.server.store  # type: ignore[attr-defined]

    @property
    def allowed_provider_environments(self) -> set[str] | None:
        return self.server.allowed_provider_environments  # type: ignore[attr-defined]

    @property
    def deployment_environment(self) -> str | None:
        return self.server.deployment_environment  # type: ignore[attr-defined]

    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Nieprawidłowy JSON.") from exc

    def _not_found(self) -> None:
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Nie znaleziono zasobu."})

    def _bad_request(self, message: str) -> None:
        self._send_json(HTTPStatus.BAD_REQUEST, {"error": message})

    def _unauthorized(self, message: str) -> None:
        self._send_json(HTTPStatus.UNAUTHORIZED, {"error": message})

    def _conflict(self, message: str) -> None:
        self._send_json(HTTPStatus.CONFLICT, {"error": message})

    def _forbidden(self, message: str) -> None:
        self._send_json(HTTPStatus.FORBIDDEN, {"error": message})

    def _enforce_provider_environment(self, provider_id: str) -> None:
        try:
            ensure_provider_environment_allowed(
                provider_id,
                self.allowed_provider_environments,
                self.deployment_environment,
            )
        except ValueError as exc:
            raise ProviderEnvironmentPolicyError(str(exc)) from exc

    def _require_provider_token(self, provider_id: str) -> None:
        provided_token = self.headers.get("X-Provider-Token")
        if self.store.get_provider(provider_id) is None:
            raise PermissionError("Provider musi zostać najpierw zarejestrowany.")
        if not self.store.verify_provider_token(provider_id, provided_token):
            raise PermissionError("Brak poprawnego tokenu providera.")

    def _handle_provider_register(self, payload: Dict[str, Any]) -> None:
        provider = validate_provider_descriptor_payload(payload)
        self._enforce_provider_environment(provider["provider_id"])
        response = self.store.register_provider(provider)
        self._send_json(HTTPStatus.CREATED, response)

    def _handle_provider_token_rotate(self, provider_id: str) -> None:
        if self.store.get_provider(provider_id) is None:
            raise ProviderNotFoundError("Provider nie istnieje.")
        self._enforce_provider_environment(provider_id)
        self._require_provider_token(provider_id)
        response = self.store.rotate_provider_token(provider_id)
        self._send_json(HTTPStatus.OK, response)

    def _handle_observation(self, payload: Dict[str, Any]) -> None:
        observation = validate_observation_payload(payload)
        provider_id = observation["provider"]["provider_id"]
        self._enforce_provider_environment(provider_id)
        self._require_provider_token(provider_id)
        self.store.update_provider_seen(provider_id)
        self.store.save_observation(observation)
        self._send_json(
            HTTPStatus.ACCEPTED,
            {
                "status": "accepted",
                "provider_id": provider_id,
                "message": "Obserwacja została zapisana w bazie operacyjnej.",
            },
        )

    def _handle_event(self, payload: Dict[str, Any]) -> None:
        event = validate_event_payload(payload)
        provider_id = event["provider"]["provider_id"]
        self._enforce_provider_environment(provider_id)
        self._require_provider_token(provider_id)
        self.store.update_provider_seen(provider_id)
        self.store.save_event(event)
        self._send_json(
            HTTPStatus.ACCEPTED,
            {
                "status": "accepted",
                "provider_id": provider_id,
                "message": "Zdarzenie zostało zapisane w bazie operacyjnej.",
            },
        )

    def _handle_recommendation(self, payload: Dict[str, Any]) -> None:
        if "observation" not in payload:
            raise ValueError("Brak pola observation.")
        observation = validate_observation_payload(payload["observation"])
        provider_id = observation["provider"]["provider_id"]
        self._enforce_provider_environment(provider_id)
        self._require_provider_token(provider_id)

        last_event = payload.get("last_event")
        if last_event is None:
            last_event = payload.get("last_behavior_event")
        if last_event is not None:
            last_event = validate_event_payload(last_event)

        recommendation = generate_recommendation(
            observation,
            context=payload.get("context"),
            last_event=last_event,
        )
        self.store.update_provider_seen(provider_id)
        self.store.save_recommendation(recommendation)
        self._send_json(HTTPStatus.OK, recommendation)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/v1/providers/register":
                self._handle_provider_register(payload)
                return
            parts = [part for part in parsed.path.split("/") if part]
            if (
                len(parts) == 5
                and parts[:2] == ["v1", "providers"]
                and parts[3:] == ["tokens", "rotate"]
            ):
                self._handle_provider_token_rotate(parts[2])
                return
            if parsed.path == "/v1/observations":
                self._handle_observation(payload)
                return
            if parsed.path == "/v1/events":
                self._handle_event(payload)
                return
            if parsed.path == "/v1/recommendations/fish-pond":
                self._handle_recommendation(payload)
                return
            self._not_found()
        except ValueError as exc:
            self._bad_request(str(exc))
        except PermissionError as exc:
            self._unauthorized(str(exc))
        except ProviderConflictError as exc:
            self._conflict(str(exc))
        except ProviderNotFoundError as exc:
            self._not_found()
        except ProviderEnvironmentPolicyError as exc:
            self._forbidden(str(exc))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) == 4 and parts[:2] == ["v1", "providers"] and parts[3] == "status":
            provider_id = parts[2]
            provider_status = self.store.provider_status(provider_id)
            if provider_status is None:
                self._not_found()
                return
            self._send_json(HTTPStatus.OK, provider_status)
            return
        self._not_found()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def create_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    db_path: str | Path | None = None,
    deployment_environment: str | None = None,
    allowed_provider_environments: set[str] | None = None,
) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), FishPondAPIHandler)
    server.store = OperationalStore(db_path)  # type: ignore[attr-defined]
    server.deployment_environment = deployment_environment  # type: ignore[attr-defined]
    server.allowed_provider_environments = allowed_provider_environments  # type: ignore[attr-defined]
    return server


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    db_path = os.environ.get("FISH_POND_DB_PATH", str(DEFAULT_DB_PATH))
    deployment_environment = os.environ.get("DEPLOYMENT_ENVIRONMENT")
    allowed_provider_environments = parse_allowed_provider_environments(
        os.environ.get("ALLOWED_PROVIDER_ENVIRONMENTS"),
        deployment_environment,
    )
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    if len(sys.argv) >= 3:
        db_path = sys.argv[2]
    server = create_server(
        host,
        port,
        db_path=db_path,
        deployment_environment=deployment_environment,
        allowed_provider_environments=allowed_provider_environments,
    )
    print(f"Fish pond API server listening on http://{host}:{port}")
    print(f"Operational DB: {db_path}")
    if deployment_environment:
        print(f"Deployment environment: {deployment_environment}")
    if allowed_provider_environments is not None:
        print(
            "Allowed provider environments: "
            + ", ".join(sorted(allowed_provider_environments))
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
