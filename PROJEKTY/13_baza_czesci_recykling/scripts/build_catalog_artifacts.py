#!/usr/bin/env python3
"""Build GitHub-tracked artifacts for the recycled parts catalog."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DEVICES_PATH = DATA_DIR / "devices.jsonl"
PARTS_PATH = DATA_DIR / "device_parts.jsonl"
INVENTORY_PATH = DATA_DIR / "inventory.csv"
D1_SQL_PATH = DATA_DIR / "recycled_parts_seed.sql"
MCP_JSON_PATH = DATA_DIR / "mcp_reuse_catalog.json"
SEED_TIMESTAMP = "2026-04-15T00:00:00Z"

ECOEDA_HEADERS = [
    "Component Name",
    "Species",
    "Genus",
    "SMD vs THT",
    "Value",
    "Keywords",
    "Description",
    "Symbol-KICAD-URL",
    "Footprint-KICAD-URL",
    "Datasheet",
    "Source",
    "Teardown Link",
    "Quantity",
    "PCB Designator",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def load_catalog() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    devices = read_jsonl(DEVICES_PATH)
    parts = read_jsonl(PARTS_PATH)
    validate_catalog(devices, parts)
    return devices, parts


def validate_catalog(devices: list[dict[str, Any]], parts: list[dict[str, Any]]) -> None:
    device_slugs = [device["device_slug"] for device in devices]
    duplicates = sorted({slug for slug in device_slugs if device_slugs.count(slug) > 1})
    if duplicates:
        raise ValueError(f"Duplicate device_slug entries: {', '.join(duplicates)}")

    known_devices = {device["device_slug"] for device in devices}
    missing_device_links = sorted(
        {
            part["device_slug"]
            for part in parts
            if part["device_slug"] not in known_devices
        }
    )
    if missing_device_links:
        raise ValueError(
            "Parts reference missing devices: " + ", ".join(missing_device_links)
        )

    for device in devices:
        if not isinstance(device.get("known_aliases"), list):
            raise ValueError(f"Device {device['device_slug']} must define known_aliases list")
        if not isinstance(device.get("serial_markers"), list):
            raise ValueError(f"Device {device['device_slug']} must define serial_markers list")

    for part in parts:
        if not isinstance(part.get("keywords"), list):
            raise ValueError(f"Part {part['part_name']} must define keywords list")
        if not isinstance(part.get("designators"), list):
            raise ValueError(f"Part {part['part_name']} must define designators list")
        if not isinstance(part.get("part_aliases"), list):
            raise ValueError(f"Part {part['part_name']} must define part_aliases list")


def build_device_index(devices: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {device["device_slug"]: device for device in devices}


def write_inventory_csv(
    devices: list[dict[str, Any]],
    parts: list[dict[str, Any]],
    output_path: Path = INVENTORY_PATH,
) -> None:
    device_index = build_device_index(devices)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ECOEDA_HEADERS)
        writer.writeheader()
        for part in parts:
            device = device_index[part["device_slug"]]
            writer.writerow(
                {
                    "Component Name": part["part_name"],
                    "Species": part["species"],
                    "Genus": part["genus"],
                    "SMD vs THT": part["mounting"],
                    "Value": part["value"],
                    "Keywords": ", ".join(part["keywords"]),
                    "Description": part["description"],
                    "Symbol-KICAD-URL": part["kicad_symbol"],
                    "Footprint-KICAD-URL": part["kicad_footprint"],
                    "Datasheet": part["datasheet_url"],
                    "Source": device["canonical_name"],
                    "Teardown Link": device["teardown_url"] or part["source_url"],
                    "Quantity": part["quantity"],
                    "PCB Designator": ", ".join(part["designators"]),
                }
            )


def sql_quote(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def write_d1_seed_sql(
    devices: list[dict[str, Any]],
    parts: list[dict[str, Any]],
    output_path: Path = D1_SQL_PATH,
) -> None:
    device_index = build_device_index(devices)
    lines = [
        "-- Generated from PROJEKTY/13_baza_czesci_recykling/data/*.jsonl",
        "BEGIN TRANSACTION;",
        "DELETE FROM recycled_device_submissions;",
        "DELETE FROM recycled_device_evidence;",
        "DELETE FROM recycled_part_aliases;",
        "DELETE FROM recycled_device_aliases;",
        "DELETE FROM recycled_parts;",
        "DELETE FROM recycled_devices;",
        "",
    ]

    for device in devices:
        lines.append(
            "INSERT INTO recycled_devices (model, brand, description, teardown_url, created_at, device_category, source_url, donor_rank) "
            f"VALUES ({sql_quote(device['model'])}, {sql_quote(device['brand'])}, {sql_quote(device['description'])}, "
            f"{sql_quote(device['teardown_url'])}, {sql_quote(SEED_TIMESTAMP)}, {sql_quote(device['device_category'])}, "
            f"{sql_quote(device['source_url'])}, {sql_quote(device['donor_rank'])});"
        )
        for alias in device["known_aliases"]:
            lines.append(
                "INSERT INTO recycled_device_aliases (device_id, alias, alias_type, source, created_at) "
                f"VALUES ((SELECT id FROM recycled_devices WHERE model = {sql_quote(device['model'])}), "
                f"{sql_quote(alias)}, 'device_alias', {sql_quote(device['source_url'])}, {sql_quote(SEED_TIMESTAMP)});"
            )
        for marker in device["serial_markers"]:
            lines.append(
                "INSERT INTO recycled_device_aliases (device_id, alias, alias_type, source, created_at) "
                f"VALUES ((SELECT id FROM recycled_devices WHERE model = {sql_quote(device['model'])}), "
                f"{sql_quote(marker)}, 'serial_marker', {sql_quote(device['source_url'])}, {sql_quote(SEED_TIMESTAMP)});"
            )
        lines.append("")

    for part in parts:
        device = device_index[part["device_slug"]]
        designator_text = ", ".join(part["designators"])
        lines.append(
            "INSERT INTO recycled_parts (device_id, part_name, species, value, designator, description, created_at, genus, mounting, keywords, "
            "kicad_symbol, kicad_footprint, datasheet_url, quantity, source_url, confidence) "
            f"VALUES ((SELECT id FROM recycled_devices WHERE model = {sql_quote(device['model'])}), {sql_quote(part['part_name'])}, "
            f"{sql_quote(part['species'])}, {sql_quote(part['value'])}, {sql_quote(designator_text)}, {sql_quote(part['description'])}, "
            f"{sql_quote(SEED_TIMESTAMP)}, {sql_quote(part['genus'])}, {sql_quote(part['mounting'])}, {sql_quote(', '.join(part['keywords']))}, "
            f"{sql_quote(part['kicad_symbol'])}, {sql_quote(part['kicad_footprint'])}, {sql_quote(part['datasheet_url'])}, "
            f"{sql_quote(part['quantity'])}, {sql_quote(part['source_url'] or device['source_url'])}, {sql_quote(part['confidence'])});"
        )
        for alias in part["part_aliases"]:
            lines.append(
                "INSERT INTO recycled_part_aliases (part_id, alias, alias_type, source, created_at) "
                f"VALUES ((SELECT rp.id FROM recycled_parts rp JOIN recycled_devices rd ON rd.id = rp.device_id "
                f"WHERE rd.model = {sql_quote(device['model'])} AND rp.part_name = {sql_quote(part['part_name'])}), "
                f"{sql_quote(alias)}, 'part_alias', {sql_quote(part['source_url'] or device['source_url'])}, {sql_quote(SEED_TIMESTAMP)});"
            )
        lines.append("")

    lines.append("COMMIT;")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_mcp_catalog(
    devices: list[dict[str, Any]],
    parts: list[dict[str, Any]],
) -> dict[str, Any]:
    device_index = build_device_index(devices)
    part_groups: dict[str, dict[str, Any]] = {}

    for part in parts:
        key = part["part_name"].lower()
        device = device_index[part["device_slug"]]
        donor_entry = {
            "device_slug": device["device_slug"],
            "canonical_name": device["canonical_name"],
            "quantity": part["quantity"],
            "designators": part["designators"],
            "teardown_url": device["teardown_url"],
            "source_url": part["source_url"] or device["source_url"],
            "confidence": part["confidence"],
        }
        if key not in part_groups:
            part_groups[key] = {
                "display_name": part["part_name"],
                "species": part["species"],
                "genus": part["genus"],
                "mounting": part["mounting"],
                "value": part["value"],
                "aliases": sorted(set(part["part_aliases"])),
                "kicad_symbol": part["kicad_symbol"],
                "kicad_footprint": part["kicad_footprint"],
                "datasheet_url": part["datasheet_url"],
                "donor_devices": [],
            }
        else:
            part_groups[key]["aliases"] = sorted(
                set(part_groups[key]["aliases"]) | set(part["part_aliases"])
            )
        part_groups[key]["donor_devices"].append(donor_entry)

    return {
        "catalog_version": 1,
        "source_of_truth": "github",
        "generated_from": [
            "PROJEKTY/13_baza_czesci_recykling/data/devices.jsonl",
            "PROJEKTY/13_baza_czesci_recykling/data/device_parts.jsonl",
        ],
        "device_count": len(devices),
        "part_count": len(parts),
        "devices": devices,
        "part_index": [
            {
                "lookup_key": key,
                **value,
            }
            for key, value in sorted(part_groups.items())
        ],
    }


def write_mcp_catalog_json(
    devices: list[dict[str, Any]],
    parts: list[dict[str, Any]],
    output_path: Path = MCP_JSON_PATH,
) -> None:
    payload = build_mcp_catalog(devices, parts)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def export_all() -> None:
    devices, parts = load_catalog()
    write_inventory_csv(devices, parts)
    write_d1_seed_sql(devices, parts)
    write_mcp_catalog_json(devices, parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["validate", "export-all", "export-ecoeda", "export-d1-sql", "export-mcp"],
        help="Action to execute",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    devices, parts = load_catalog()

    if args.command == "validate":
        return 0
    if args.command == "export-all":
        write_inventory_csv(devices, parts)
        write_d1_seed_sql(devices, parts)
        write_mcp_catalog_json(devices, parts)
        return 0
    if args.command == "export-ecoeda":
        write_inventory_csv(devices, parts)
        return 0
    if args.command == "export-d1-sql":
        write_d1_seed_sql(devices, parts)
        return 0
    if args.command == "export-mcp":
        write_mcp_catalog_json(devices, parts)
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
