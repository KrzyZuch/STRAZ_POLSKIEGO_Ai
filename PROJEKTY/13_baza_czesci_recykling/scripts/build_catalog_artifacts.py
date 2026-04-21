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
PARTS_MASTER_PATH = DATA_DIR / "parts_master.jsonl"
DEVICE_PARTS_PATH = DATA_DIR / "device_parts.jsonl"
INVENTORY_PATH = DATA_DIR / "inventory.csv"
D1_SQL_PATH = DATA_DIR / "recycled_parts_seed.sql"
MCP_JSON_PATH = DATA_DIR / "mcp_reuse_catalog.json"
INVENTREE_PATH = DATA_DIR / "inventree_import.jsonl"
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def load_catalog() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    devices = read_jsonl(DEVICES_PATH)
    parts_master = read_jsonl(PARTS_MASTER_PATH)
    device_parts = read_jsonl(DEVICE_PARTS_PATH)
    validate_catalog(devices, parts_master, device_parts)
    return devices, parts_master, device_parts


def validate_catalog(
    devices: list[dict[str, Any]],
    parts_master: list[dict[str, Any]],
    device_parts: list[dict[str, Any]],
) -> None:
    device_slugs = [device["device_slug"] for device in devices]
    duplicate_device_slugs = sorted({slug for slug in device_slugs if device_slugs.count(slug) > 1})
    if duplicate_device_slugs:
        raise ValueError(f"Duplicate device_slug entries: {', '.join(duplicate_device_slugs)}")

    part_slugs = [part["part_slug"] for part in parts_master]
    duplicate_part_slugs = sorted({slug for slug in part_slugs if part_slugs.count(slug) > 1})
    if duplicate_part_slugs:
        raise ValueError(f"Duplicate part_slug entries: {', '.join(duplicate_part_slugs)}")

    known_devices = {device["device_slug"] for device in devices}
    known_parts = {part["part_slug"] for part in parts_master}

    missing_device_links = sorted(
        {
            item["device_slug"]
            for item in device_parts
            if item["device_slug"] not in known_devices
        }
    )
    if missing_device_links:
        raise ValueError("Device part links reference missing devices: " + ", ".join(missing_device_links))

    missing_part_links = sorted(
        {
            item["part_slug"]
            for item in device_parts
            if item["part_slug"] not in known_parts
        }
    )
    if missing_part_links:
        raise ValueError("Device part links reference missing parts: " + ", ".join(missing_part_links))

    for device in devices:
        if not isinstance(device.get("known_aliases"), list):
            raise ValueError(f"Device {device['device_slug']} must define known_aliases list")
        if not isinstance(device.get("serial_markers"), list):
            raise ValueError(f"Device {device['device_slug']} must define serial_markers list")

    for part in parts_master:
        if not isinstance(part.get("keywords"), list):
            raise ValueError(f"Part {part['part_slug']} must define keywords list")
        if not isinstance(part.get("part_aliases"), list):
            raise ValueError(f"Part {part['part_slug']} must define part_aliases list")
        if not isinstance(part.get("parameters"), dict):
            raise ValueError(f"Part {part['part_slug']} must define parameters object")

    for link in device_parts:
        if not isinstance(link.get("designators"), list):
            raise ValueError(
                f"Device part link {link['device_slug']}->{link['part_slug']} must define designators list"
            )


def build_device_index(devices: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {device["device_slug"]: device for device in devices}


def build_part_index(parts_master: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {part["part_slug"]: part for part in parts_master}


def iter_joined_device_parts(
    devices: list[dict[str, Any]],
    parts_master: list[dict[str, Any]],
    device_parts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    device_index = build_device_index(devices)
    part_index = build_part_index(parts_master)
    rows: list[dict[str, Any]] = []
    for link in device_parts:
        rows.append(
            {
                "device": device_index[link["device_slug"]],
                "part": part_index[link["part_slug"]],
                "link": link,
            }
        )
    return rows


def write_inventory_csv(
    devices: list[dict[str, Any]],
    parts_master: list[dict[str, Any]],
    device_parts: list[dict[str, Any]],
    output_path: Path = INVENTORY_PATH,
) -> None:
    joined_rows = iter_joined_device_parts(devices, parts_master, device_parts)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ECOEDA_HEADERS)
        writer.writeheader()
        for row in joined_rows:
            part = row["part"]
            device = row["device"]
            link = row["link"]
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
                    "Teardown Link": device["teardown_url"] or link["source_url"],
                    "Quantity": link["quantity"],
                    "PCB Designator": ", ".join(link["designators"]),
                }
            )


def sql_quote(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def write_d1_seed_sql(
    devices: list[dict[str, Any]],
    parts_master: list[dict[str, Any]],
    device_parts: list[dict[str, Any]],
    output_path: Path = D1_SQL_PATH,
) -> None:
    device_index = build_device_index(devices)
    part_index = build_part_index(parts_master)
    lines = [
        "-- Generated from PROJEKTY/13_baza_czesci_recykling/data/*.jsonl",
        "BEGIN TRANSACTION;",
        "DELETE FROM recycled_device_parts;",
        "DELETE FROM recycled_part_master;",
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

    for part in parts_master:
        lines.append(
            "INSERT INTO recycled_part_master (part_slug, part_number, normalized_part_number, part_name, species, genus, mounting, value, "
            "description, keywords, datasheet_url, datasheet_file_id, ipn, category, parameters, kicad_symbol, kicad_footprint, "
            "kicad_reference, created_at, updated_at) "
            f"VALUES ({sql_quote(part['part_slug'])}, {sql_quote(part['part_number'])}, {sql_quote(part['normalized_part_number'])}, "
            f"{sql_quote(part['part_name'])}, {sql_quote(part['species'])}, {sql_quote(part['genus'])}, {sql_quote(part['mounting'])}, "
            f"{sql_quote(part['value'])}, {sql_quote(part['description'])}, {sql_quote(', '.join(part['keywords']))}, "
            f"{sql_quote(part['datasheet_url'])}, {sql_quote(part['datasheet_file_id'])}, {sql_quote(part['ipn'])}, "
            f"{sql_quote(part['category'])}, {sql_quote(json.dumps(part['parameters'], ensure_ascii=False, separators=(',', ':')))}, "
            f"{sql_quote(part['kicad_symbol'])}, {sql_quote(part['kicad_footprint'])}, {sql_quote(part['kicad_reference'])}, "
            f"{sql_quote(SEED_TIMESTAMP)}, {sql_quote(SEED_TIMESTAMP)});"
        )
        lines.append("")

    for link in device_parts:
        device = device_index[link["device_slug"]]
        part = part_index[link["part_slug"]]
        designator_text = ", ".join(link["designators"])
        lines.append(
            "INSERT INTO recycled_device_parts (device_id, master_part_id, quantity, designator, source_url, confidence, stock_location, evidence_url, evidence_timecode, created_at) "
            f"VALUES ((SELECT id FROM recycled_devices WHERE model = {sql_quote(device['model'])}), "
            f"(SELECT id FROM recycled_part_master WHERE part_slug = {sql_quote(part['part_slug'])}), "
            f"{sql_quote(link['quantity'])}, {sql_quote(designator_text)}, {sql_quote(link['source_url'])}, "
            f"{sql_quote(link['confidence'])}, {sql_quote(link.get('stock_location', ''))}, "
            f"{sql_quote(link.get('evidence_url', ''))}, {sql_quote(link.get('evidence_timecode'))}, {sql_quote(SEED_TIMESTAMP)});"
        )
        lines.append(
            "INSERT INTO recycled_parts (device_id, part_name, species, value, designator, description, created_at, genus, mounting, keywords, "
            "kicad_symbol, kicad_footprint, datasheet_url, quantity, source_url, confidence, ipn, category, parameters, datasheet_file_id, "
            "kicad_reference, stock_location, master_part_id) "
            f"VALUES ((SELECT id FROM recycled_devices WHERE model = {sql_quote(device['model'])}), {sql_quote(part['part_name'])}, "
            f"{sql_quote(part['species'])}, {sql_quote(part['value'])}, {sql_quote(designator_text)}, {sql_quote(part['description'])}, "
            f"{sql_quote(SEED_TIMESTAMP)}, {sql_quote(part['genus'])}, {sql_quote(part['mounting'])}, "
            f"{sql_quote(', '.join(part['keywords']))}, {sql_quote(part['kicad_symbol'])}, {sql_quote(part['kicad_footprint'])}, "
            f"{sql_quote(part['datasheet_url'])}, {sql_quote(link['quantity'])}, {sql_quote(link['source_url'] or device['source_url'])}, "
            f"{sql_quote(link['confidence'])}, {sql_quote(part['ipn'])}, {sql_quote(part['category'])}, "
            f"{sql_quote(json.dumps(part['parameters'], ensure_ascii=False, separators=(',', ':')))}, {sql_quote(part['datasheet_file_id'])}, "
            f"{sql_quote(part['kicad_reference'])}, {sql_quote(link.get('stock_location', ''))}, "
            f"(SELECT id FROM recycled_part_master WHERE part_slug = {sql_quote(part['part_slug'])}));"
        )
        for alias in part["part_aliases"]:
            lines.append(
                "INSERT INTO recycled_part_aliases (part_id, alias, alias_type, source, created_at) "
                f"VALUES ((SELECT rp.id FROM recycled_parts rp "
                f"JOIN recycled_devices rd ON rd.id = rp.device_id "
                f"WHERE rd.model = {sql_quote(device['model'])} "
                f"AND rp.part_name = {sql_quote(part['part_name'])} LIMIT 1), "
                f"{sql_quote(alias)}, 'part_alias', {sql_quote(link['source_url'] or device['source_url'])}, {sql_quote(SEED_TIMESTAMP)});"
            )
        lines.append("")

    lines.append("COMMIT;")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_mcp_catalog(
    devices: list[dict[str, Any]],
    parts_master: list[dict[str, Any]],
    device_parts: list[dict[str, Any]],
) -> dict[str, Any]:
    device_index = build_device_index(devices)
    part_index = build_part_index(parts_master)
    part_groups: dict[str, dict[str, Any]] = {}

    for part in parts_master:
        part_groups[part["part_slug"]] = {
            "lookup_key": part["part_slug"],
            "display_name": part["part_name"],
            "part_number": part["part_number"],
            "normalized_part_number": part["normalized_part_number"],
            "species": part["species"],
            "genus": part["genus"],
            "mounting": part["mounting"],
            "value": part["value"],
            "aliases": sorted(set(part["part_aliases"])),
            "kicad_symbol": part["kicad_symbol"],
            "kicad_footprint": part["kicad_footprint"],
            "kicad_reference": part["kicad_reference"],
            "datasheet_url": part["datasheet_url"],
            "category": part["category"],
            "ipn": part["ipn"],
            "parameters": part["parameters"],
            "donor_devices": [],
        }

    for link in device_parts:
        device = device_index[link["device_slug"]]
        part = part_index[link["part_slug"]]
        donor_entry = {
            "device_slug": device["device_slug"],
            "canonical_name": device["canonical_name"],
            "quantity": link["quantity"],
            "designators": link["designators"],
            "teardown_url": device["teardown_url"],
            "source_url": link["source_url"] or device["source_url"],
            "confidence": link["confidence"],
            "stock_location": link.get("stock_location", ""),
            "evidence_url": link.get("evidence_url", ""),
            "evidence_timecode": link.get("evidence_timecode"),
        }
        part_groups[part["part_slug"]]["donor_devices"].append(donor_entry)

    return {
        "catalog_version": 2,
        "source_of_truth": "github",
        "generated_from": [
            "PROJEKTY/13_baza_czesci_recykling/data/devices.jsonl",
            "PROJEKTY/13_baza_czesci_recykling/data/parts_master.jsonl",
            "PROJEKTY/13_baza_czesci_recykling/data/device_parts.jsonl",
        ],
        "device_count": len(devices),
        "part_master_count": len(parts_master),
        "device_part_count": len(device_parts),
        "devices": devices,
        "part_index": [part_groups[key] for key in sorted(part_groups.keys())],
    }


def write_mcp_catalog_json(
    devices: list[dict[str, Any]],
    parts_master: list[dict[str, Any]],
    device_parts: list[dict[str, Any]],
    output_path: Path = MCP_JSON_PATH,
) -> None:
    payload = build_mcp_catalog(devices, parts_master, device_parts)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_inventree_import(
    parts_master: list[dict[str, Any]],
    output_path: Path = INVENTREE_PATH,
) -> None:
    rows = []
    for part in parts_master:
        rows.append(
            {
                "part_slug": part["part_slug"],
                "name": part["part_name"],
                "part_number": part["part_number"],
                "description": part["description"],
                "ipn": part["ipn"],
                "category": part["category"],
                "parameters": part["parameters"],
                "datasheet_url": part["datasheet_url"],
                "datasheet_file_id": part["datasheet_file_id"],
                "kicad_symbol": part["kicad_symbol"],
                "kicad_footprint": part["kicad_footprint"],
                "kicad_reference": part["kicad_reference"],
                "aliases": part["part_aliases"],
                "keywords": part["keywords"],
                "mounting": part["mounting"],
                "species": part["species"],
                "genus": part["genus"],
                "value": part["value"],
            }
        )
    write_jsonl(output_path, rows)


def export_all() -> None:
    devices, parts_master, device_parts = load_catalog()
    write_inventory_csv(devices, parts_master, device_parts)
    write_d1_seed_sql(devices, parts_master, device_parts)
    write_mcp_catalog_json(devices, parts_master, device_parts)
    write_inventree_import(parts_master)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "validate",
            "export-all",
            "export-ecoeda",
            "export-d1-sql",
            "export-mcp",
            "export-inventree",
        ],
        help="Action to execute",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    devices, parts_master, device_parts = load_catalog()

    if args.command == "validate":
        return 0
    if args.command == "export-all":
        write_inventory_csv(devices, parts_master, device_parts)
        write_d1_seed_sql(devices, parts_master, device_parts)
        write_mcp_catalog_json(devices, parts_master, device_parts)
        write_inventree_import(parts_master)
        return 0
    if args.command == "export-ecoeda":
        write_inventory_csv(devices, parts_master, device_parts)
        return 0
    if args.command == "export-d1-sql":
        write_d1_seed_sql(devices, parts_master, device_parts)
        return 0
    if args.command == "export-mcp":
        write_mcp_catalog_json(devices, parts_master, device_parts)
        return 0
    if args.command == "export-inventree":
        write_inventree_import(parts_master)
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
