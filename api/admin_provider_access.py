from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.storage import (  # noqa: E402
    DEFAULT_DB_PATH,
    OperationalStore,
    ProviderNotFoundError,
)


def render_provider_list(providers: list[dict]) -> str:
    lines = ["# Providerzy operacyjni", ""]
    if not providers:
        lines.append("- Brak zarejestrowanych providerów.")
        return "\n".join(lines) + "\n"

    for provider in providers:
        capabilities: list[str] = []
        if provider["supports_water_quality"]:
            capabilities.append("water_quality")
        if provider["supports_flow_monitoring"]:
            capabilities.append("flow")
        if provider["supports_edge_vision_summary"]:
            capabilities.append("edge_vision")
        capability_text = ", ".join(capabilities) if capabilities else "brak"
        node_class = provider["node_class"] or "unspecified"
        lines.extend(
            [
                f"- `{provider['provider_id']}`",
                f"  typ: {provider['provider_kind']}",
                f"  etykieta: {provider['provider_label']}",
                f"  node_class: {node_class}",
                f"  capabilities: {capability_text}",
                f"  registered_at: {provider['registered_at']}",
                f"  last_seen_at: {provider['last_seen_at']}",
            ]
        )
    return "\n".join(lines) + "\n"


def render_provider_status(provider: dict) -> str:
    node_class = provider["node_class"] or "unspecified"
    capabilities: list[str] = []
    if provider["supports_water_quality"]:
        capabilities.append("water_quality")
    if provider["supports_flow_monitoring"]:
        capabilities.append("flow")
    if provider["supports_edge_vision_summary"]:
        capabilities.append("edge_vision")
    capability_text = ", ".join(capabilities) if capabilities else "brak"

    lines = [
        "# Status providera",
        "",
        f"- provider_id: `{provider['provider_id']}`",
        f"- provider_kind: `{provider['provider_kind']}`",
        f"- provider_label: `{provider['provider_label']}`",
        f"- node_class: `{node_class}`",
        f"- schema_version: `{provider['schema_version']}`",
        f"- registered_at: `{provider['registered_at']}`",
        f"- last_seen_at: `{provider['last_seen_at']}`",
        f"- capabilities: `{capability_text}`",
    ]
    return "\n".join(lines) + "\n"


def list_providers_text(store: OperationalStore) -> str:
    return render_provider_list(store.list_providers())


def provider_status_text(store: OperationalStore, provider_id: str) -> str:
    provider = store.get_provider(provider_id)
    if provider is None:
        raise ProviderNotFoundError("Provider nie istnieje.")
    return render_provider_status(provider)


def rotate_provider_token_text(store: OperationalStore, provider_id: str) -> str:
    response = store.rotate_provider_token(provider_id)
    return json.dumps(response, indent=2, ensure_ascii=False) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Narzędzia administracyjne dla providerów API Straży Przyszłości."
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="Ścieżka do operacyjnej bazy SQLite.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="Wyświetla zarejestrowanych providerów.")

    status_parser = subparsers.add_parser(
        "status", help="Wyświetla szczegóły pojedynczego providera."
    )
    status_parser.add_argument("provider_id")

    rotate_parser = subparsers.add_parser(
        "rotate-token",
        help="Obraca token providera i zwraca nowy write_token.",
    )
    rotate_parser.add_argument("provider_id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = OperationalStore(args.db_path)

    try:
        if args.command == "list":
            print(list_providers_text(store), end="")
            return 0
        if args.command == "status":
            print(provider_status_text(store, args.provider_id), end="")
            return 0
        if args.command == "rotate-token":
            print(rotate_provider_token_text(store, args.provider_id), end="")
            return 0
    except ProviderNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.error("Nieobsługiwane polecenie.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
