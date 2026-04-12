from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable

from adapters.utils import utc_now_iso, validate_provider_descriptor_payload


DEFAULT_DB_PATH = Path(os.environ.get("FISH_POND_DB_PATH", "/tmp/straz_fish_pond_v1.db"))


class ProviderConflictError(Exception):
    pass


class ProviderNotFoundError(Exception):
    pass


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_write_token() -> str:
    return secrets.token_urlsafe(24)


class OperationalStore:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS providers (
                  provider_id TEXT PRIMARY KEY,
                  provider_kind TEXT NOT NULL,
                  provider_label TEXT NOT NULL,
                  node_class TEXT,
                  supports_water_quality INTEGER NOT NULL DEFAULT 0,
                  supports_flow_monitoring INTEGER NOT NULL DEFAULT 0,
                  supports_edge_vision_summary INTEGER NOT NULL DEFAULT 0,
                  schema_version TEXT NOT NULL DEFAULT 'v1',
                  write_token_hash TEXT NOT NULL,
                  registered_at TEXT NOT NULL,
                  last_seen_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS observations (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  provider_id TEXT NOT NULL,
                  pond_id TEXT NOT NULL,
                  measurement_time TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  provider_id TEXT NOT NULL,
                  pond_id TEXT NOT NULL,
                  event_time TEXT NOT NULL,
                  event_type TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS recommendations (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  provider_id TEXT NOT NULL,
                  pond_id TEXT NOT NULL,
                  analysis_time TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )

    def register_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        validate_provider_descriptor_payload(provider)
        if self.get_provider(provider["provider_id"]) is not None:
            raise ProviderConflictError("Provider o tym provider_id już istnieje.")
        token = generate_write_token()
        current_time = utc_now_iso()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO providers (
                  provider_id, provider_kind, provider_label, node_class,
                  supports_water_quality, supports_flow_monitoring, supports_edge_vision_summary,
                  schema_version, write_token_hash, registered_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'v1', ?, ?, ?)
                """,
                (
                    provider["provider_id"],
                    provider["provider_kind"],
                    provider["provider_label"],
                    provider.get("node_class"),
                    int(bool(provider.get("supports_water_quality", False))),
                    int(bool(provider.get("supports_flow_monitoring", False))),
                    int(bool(provider.get("supports_edge_vision_summary", False))),
                    hash_token(token),
                    current_time,
                    current_time,
                ),
            )
        return {
            "provider_id": provider["provider_id"],
            "registration_status": "registered",
            "schema_version": "v1",
            "message": "Provider został zarejestrowany.",
            "write_token": token,
        }

    def rotate_provider_token(self, provider_id: str) -> Dict[str, Any]:
        if self.get_provider(provider_id) is None:
            raise ProviderNotFoundError("Provider nie istnieje.")
        token = generate_write_token()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE providers
                SET write_token_hash = ?, last_seen_at = ?
                WHERE provider_id = ?
                """,
                (hash_token(token), utc_now_iso(), provider_id),
            )
        return {
            "provider_id": provider_id,
            "rotation_status": "rotated",
            "schema_version": "v1",
            "message": "Token providera został obrócony.",
            "write_token": token,
        }

    def get_provider(self, provider_id: str) -> Dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT provider_id, provider_kind, provider_label, node_class,
                       supports_water_quality, supports_flow_monitoring, supports_edge_vision_summary,
                       schema_version, registered_at, last_seen_at, write_token_hash
                FROM providers
                WHERE provider_id = ?
                """,
                (provider_id,),
            ).fetchone()
        return dict(row) if row else None

    def provider_status(self, provider_id: str) -> Dict[str, Any] | None:
        provider = self.get_provider(provider_id)
        if provider is None:
            return None
        return {
            "provider_id": provider["provider_id"],
            "status": "ok",
            "last_seen_at": provider["last_seen_at"],
            "schema_version": provider["schema_version"],
            "supports_water_quality": bool(provider["supports_water_quality"]),
            "supports_flow_monitoring": bool(provider["supports_flow_monitoring"]),
            "supports_edge_vision_summary": bool(provider["supports_edge_vision_summary"]),
        }

    def list_providers(self) -> list[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT provider_id, provider_kind, provider_label, node_class,
                       supports_water_quality, supports_flow_monitoring, supports_edge_vision_summary,
                       schema_version, registered_at, last_seen_at
                FROM providers
                ORDER BY registered_at ASC, provider_id ASC
                """
            ).fetchall()
        providers: list[Dict[str, Any]] = []
        for row in rows:
            providers.append(
                {
                    "provider_id": row["provider_id"],
                    "provider_kind": row["provider_kind"],
                    "provider_label": row["provider_label"],
                    "node_class": row["node_class"],
                    "supports_water_quality": bool(row["supports_water_quality"]),
                    "supports_flow_monitoring": bool(row["supports_flow_monitoring"]),
                    "supports_edge_vision_summary": bool(row["supports_edge_vision_summary"]),
                    "schema_version": row["schema_version"],
                    "registered_at": row["registered_at"],
                    "last_seen_at": row["last_seen_at"],
                }
            )
        return providers

    def verify_provider_token(self, provider_id: str, token: str | None) -> bool:
        if not token:
            return False
        provider = self.get_provider(provider_id)
        if provider is None:
            return False
        return provider["write_token_hash"] == hash_token(token)

    def update_provider_seen(self, provider_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE providers SET last_seen_at = ? WHERE provider_id = ?",
                (utc_now_iso(), provider_id),
            )

    def save_observation(self, observation: Dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO observations (provider_id, pond_id, measurement_time, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    observation["provider"]["provider_id"],
                    observation["pond"]["pond_id"],
                    observation["measurement_time"],
                    json.dumps(observation, ensure_ascii=False),
                    utc_now_iso(),
                ),
            )

    def save_event(self, event: Dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO events (provider_id, pond_id, event_time, event_type, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event["provider"]["provider_id"],
                    event["pond"]["pond_id"],
                    event["event_time"],
                    event["event_type"],
                    json.dumps(event, ensure_ascii=False),
                    utc_now_iso(),
                ),
            )

    def save_recommendation(self, recommendation: Dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO recommendations (provider_id, pond_id, analysis_time, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    recommendation["provider_id"],
                    recommendation["pond_id"],
                    recommendation["analysis_time"],
                    json.dumps(recommendation, ensure_ascii=False),
                    utc_now_iso(),
                ),
            )

    def fetch_rows(self, table: str) -> Iterable[sqlite3.Row]:
        with self._connect() as connection:
            rows = connection.execute(f"SELECT * FROM {table} ORDER BY id ASC").fetchall()
        return rows

    def fetch_all_payloads(self, table: str) -> list[Dict[str, Any]]:
        payloads: list[Dict[str, Any]] = []
        for row in self.fetch_rows(table):
            payloads.append(json.loads(row["payload_json"]))
        return payloads
