#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_13_ROOT = REPO_ROOT / "PROJEKTY" / "13_baza_czesci_recykling"
DEVICES_JSONL = PROJECT_13_ROOT / "data" / "devices.jsonl"
PARTS_MASTER_JSONL = PROJECT_13_ROOT / "data" / "parts_master.jsonl"
DEVICE_PARTS_JSONL = PROJECT_13_ROOT / "data" / "device_parts.jsonl"
BUILD_SCRIPT = PROJECT_13_ROOT / "scripts" / "build_catalog_artifacts.py"


@dataclass(frozen=True)
class Submission:
    id: int
    lookup_kind: str
    query_text: str
    recognized_brand: str
    recognized_model: str
    matched_device_id: int | None
    matched_part_name: str
    matched_part_number: str
    master_part_id: int | None
    attachment_file_id: str
    attachment_mime_type: str
    raw_payload_json: dict[str, Any]
    created_at: str


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_key(value: str) -> str:
    return normalize_space(value).casefold()


def slugify(value: str) -> str:
    normalized = normalize_space(value).lower()
    normalized = normalized.replace("ą", "a").replace("ć", "c").replace("ę", "e")
    normalized = normalized.replace("ł", "l").replace("ń", "n").replace("ó", "o")
    normalized = normalized.replace("ś", "s").replace("ź", "z").replace("ż", "z")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "unknown-device"


def normalize_part_number(value: str) -> str:
    return re.sub(r"[^A-Z0-9._+\-/]", "", normalize_space(value).upper())


def run_command(command: list[str], cwd: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        command,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stderr:
        print(result.stderr.strip())
    return result.stdout


def parse_json_payload_from_wrangler(stdout: str) -> Any:
    decoder = json.JSONDecoder()
    best_value: Any = None
    best_span = -1
    for index, char in enumerate(stdout):
        if char not in "[{":
            continue
        try:
            parsed, end_index = decoder.raw_decode(stdout[index:])
        except json.JSONDecodeError:
            continue
        if end_index > best_span:
            best_value = parsed
            best_span = end_index
    if best_value is None:
        raise ValueError("Nie udało się odczytać JSON z outputu wrangler.")
    return best_value


def run_d1_query(
    sql: str,
    *,
    d1_binding: str,
    remote: bool,
    cwd: Path = REPO_ROOT / "cloudflare",
) -> list[dict[str, Any]]:
    command = ["npx", "wrangler", "d1", "execute", d1_binding]
    if remote:
        command.append("--remote")
    command.extend(["--command", sql])
    stdout = run_command(command, cwd=cwd)
    payload = parse_json_payload_from_wrangler(stdout)
    if not isinstance(payload, list) or not payload:
        return []
    first = payload[0]
    if not isinstance(first, dict):
        return []
    results = first.get("results", [])
    if not isinstance(results, list):
        return []
    return [row for row in results if isinstance(row, dict)]


def parse_raw_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {}
    return {}


def fetch_queued_submissions(
    *,
    d1_binding: str,
    remote: bool,
    limit: int,
) -> list[Submission]:
    rows = run_d1_query(
        f"""
        SELECT
          id,
          COALESCE(lookup_kind, '') AS lookup_kind,
          COALESCE(query_text, '') AS query_text,
          COALESCE(recognized_brand, '') AS recognized_brand,
          COALESCE(recognized_model, '') AS recognized_model,
          matched_device_id,
          COALESCE(matched_part_name, '') AS matched_part_name,
          COALESCE(matched_part_number, '') AS matched_part_number,
          master_part_id,
          COALESCE(attachment_file_id, '') AS attachment_file_id,
          COALESCE(attachment_mime_type, '') AS attachment_mime_type,
          COALESCE(raw_payload_json, '{{}}') AS raw_payload_json,
          COALESCE(created_at, '') AS created_at
        FROM recycled_device_submissions
        WHERE status IN ('queued', 'approved')
        ORDER BY id ASC
        LIMIT {int(limit)}
        """,
        d1_binding=d1_binding,
        remote=remote,
    )
    submissions: list[Submission] = []
    for row in rows:
        submissions.append(
            Submission(
                id=int(row.get("id", 0)),
                lookup_kind=normalize_space(row.get("lookup_kind", "")),
                query_text=normalize_space(row.get("query_text", "")),
                recognized_brand=normalize_space(row.get("recognized_brand", "")),
                recognized_model=normalize_space(row.get("recognized_model", "")),
                matched_device_id=int(row["matched_device_id"]) if row.get("matched_device_id") not in (None, "") else None,
                matched_part_name=normalize_space(row.get("matched_part_name", "")),
                matched_part_number=normalize_space(row.get("matched_part_number", "")),
                master_part_id=int(row["master_part_id"]) if row.get("master_part_id") not in (None, "") else None,
                attachment_file_id=normalize_space(row.get("attachment_file_id", "")),
                attachment_mime_type=normalize_space(row.get("attachment_mime_type", "")),
                raw_payload_json=parse_raw_payload(row.get("raw_payload_json")),
                created_at=normalize_space(row.get("created_at", "")),
            )
        )
    return submissions


def infer_brand_model(submission: Submission) -> tuple[str, str]:
    payload = submission.raw_payload_json
    brand = normalize_space(
        submission.recognized_brand
        or payload.get("brand", "")
    )
    model = normalize_space(
        submission.recognized_model
        or payload.get("model", "")
    )
    if brand and model:
        return brand, model

    query = normalize_space(submission.query_text)
    if query and not model:
        if " " in query:
            first, rest = query.split(" ", 1)
            if not brand:
                brand = first
            model = rest
        else:
            model = query
    if not brand:
        brand = "Unknown"
    if not model:
        model = f"Unknown Model {submission.id}"
    return brand, model


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    serialized = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(serialized + "\n", encoding="utf-8")


def build_known_pair_index(devices: list[dict[str, Any]]) -> set[tuple[str, str]]:
    index: set[tuple[str, str]] = set()
    for item in devices:
        brand = normalize_key(item.get("brand", ""))
        model = normalize_key(item.get("model", ""))
        if brand and model:
            index.add((brand, model))
    return index


def build_device_slug_index(devices: list[dict[str, Any]]) -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    for item in devices:
      brand = normalize_key(item.get("brand", ""))
      model = normalize_key(item.get("model", ""))
      slug = normalize_space(item.get("device_slug", ""))
      if brand and model and slug:
          index[(brand, model)] = slug
    return index


def infer_part_identity(submission: Submission) -> tuple[str, str]:
    payload = submission.raw_payload_json
    part_name = normalize_space(
        submission.matched_part_name
        or payload.get("part_name", "")
        or payload.get("name", "")
    )
    part_number = normalize_space(
        submission.matched_part_number
        or payload.get("part_number", "")
        or payload.get("number", "")
        or payload.get("part", "")
    )
    if not part_name:
        part_name = part_number or "Unknown Part"
    if not part_number:
        part_number = part_name
    return part_name, part_number


def generate_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    if base_slug not in existing_slugs:
        return base_slug
    counter = 2
    while True:
        candidate = f"{base_slug}-{counter}"
        if candidate not in existing_slugs:
            return candidate
        counter += 1


def curate_submission_to_device(
    submission: Submission,
    *,
    existing_slugs: set[str],
) -> dict[str, Any]:
    brand, model = infer_brand_model(submission)
    canonical_name = normalize_space(f"{brand} {model}")
    base_slug = slugify(canonical_name)
    device_slug = generate_unique_slug(base_slug, existing_slugs)
    existing_slugs.add(device_slug)

    aliases = sorted(
        {
            value
            for value in [
                submission.query_text,
                submission.recognized_model,
                submission.recognized_brand,
                submission.raw_payload_json.get("model", ""),
                submission.raw_payload_json.get("brand", ""),
            ]
            if normalize_space(value)
            and normalize_key(value) not in {normalize_key(brand), normalize_key(model), normalize_key(canonical_name)}
        }
    )

    confidence_raw = submission.raw_payload_json.get("confidence")
    confidence = 0.35
    if isinstance(confidence_raw, (int, float)):
        confidence = max(0.1, min(0.95, float(confidence_raw)))

    source_url = normalize_space(submission.raw_payload_json.get("source_url", ""))
    teardown_url = normalize_space(submission.raw_payload_json.get("teardown_url", ""))
    note_parts = [
        f"Auto-curated z kolejki Telegram/D1, submission_id={submission.id}.",
    ]
    if submission.created_at:
        note_parts.append(f"created_at={submission.created_at}.")
    if submission.attachment_file_id:
        note_parts.append(f"attachment_file_id={submission.attachment_file_id}.")
    if submission.attachment_mime_type:
        note_parts.append(f"attachment_mime_type={submission.attachment_mime_type}.")

    return {
        "device_slug": device_slug,
        "brand": brand,
        "model": model,
        "canonical_name": canonical_name,
        "device_category": "unknown_device",
        "description": (
            "Auto-curated donor candidate from Telegram queue. "
            "Requires maintainer review and enrichment with verified teardown evidence."
        ),
        "known_aliases": aliases,
        "serial_markers": [],
        "donor_rank": round(confidence, 2),
        "teardown_url": teardown_url,
        "source_url": source_url,
        "notes": " ".join(note_parts),
    }


def build_part_key(part_number: str, part_name: str) -> str:
    normalized = normalize_part_number(part_number)
    if normalized:
        return normalized
    return normalize_key(part_name)


def curate_submission_to_part(submission: Submission) -> dict[str, Any] | None:
    part_name, part_number = infer_part_identity(submission)
    if not normalize_space(part_name) and not normalize_space(part_number):
        return None

    payload = submission.raw_payload_json
    normalized_number = normalize_part_number(part_number)
    part_slug = slugify(normalized_number or part_name) or f"part-{submission.id}"
    description = normalize_space(payload.get("description", "")) or (
        f"Auto-curated z kolejki Telegram/D1, submission_id={submission.id}."
    )
    datasheet_url = normalize_space(payload.get("datasheet_url", ""))
    parameters = payload.get("parameters", {})
    if not isinstance(parameters, dict):
        parameters = {}

    keywords = sorted(
        {
            item
            for item in [
                part_name,
                part_number,
                payload.get("category", ""),
                payload.get("species", ""),
            ]
            if normalize_space(item)
        }
    )

    return {
        "part_slug": part_slug,
        "part_number": part_number,
        "normalized_part_number": normalized_number or normalize_part_number(part_name),
        "part_name": part_name,
        "species": normalize_space(payload.get("species", "")) or "unknown_part",
        "genus": normalize_space(payload.get("genus", "")),
        "mounting": normalize_space(payload.get("mounting", "")),
        "value": normalize_space(payload.get("value", "")),
        "description": description,
        "keywords": keywords,
        "part_aliases": [],
        "datasheet_url": datasheet_url,
        "datasheet_file_id": submission.attachment_file_id if "pdf" in submission.attachment_mime_type.lower() else "",
        "ipn": normalize_space(payload.get("ipn", "")),
        "category": normalize_space(payload.get("category", "")) or "uncategorized",
        "parameters": parameters,
        "kicad_symbol": normalize_space(payload.get("kicad_symbol", "")),
        "kicad_footprint": normalize_space(payload.get("kicad_footprint", "")),
        "kicad_reference": normalize_space(payload.get("kicad_reference", "")),
    }


def infer_device_slug_for_submission(
    submission: Submission,
    devices: list[dict[str, Any]],
    *,
    existing_pairs: set[tuple[str, str]],
    existing_slugs: set[str],
) -> tuple[str | None, list[dict[str, Any]], list[int]]:
    device_slug_index = build_device_slug_index(devices)
    brand, model = infer_brand_model(submission)
    pair = (normalize_key(brand), normalize_key(model))
    new_devices: list[dict[str, Any]] = []
    curated_ids: list[int] = []

    if pair in device_slug_index:
        return device_slug_index[pair], new_devices, curated_ids

    if normalize_space(submission.query_text) or normalize_space(submission.recognized_model):
        curated = curate_submission_to_device(submission, existing_slugs=existing_slugs)
        devices.append(curated)
        new_devices.append(curated)
        curated_ids.append(submission.id)
        existing_pairs.add(pair)
        return curated["device_slug"], new_devices, curated_ids
    return None, new_devices, curated_ids


def apply_queue_to_devices(
    submissions: list[Submission],
    *,
    devices_path: Path = DEVICES_JSONL,
) -> tuple[list[dict[str, Any]], list[int], list[int]]:
    devices = load_jsonl(devices_path)
    existing_pairs = build_known_pair_index(devices)
    existing_slugs = {str(item.get("device_slug", "")).strip() for item in devices if item.get("device_slug")}

    new_devices: list[dict[str, Any]] = []
    curated_ids: list[int] = []
    duplicate_ids: list[int] = []
    for submission in submissions:
        brand, model = infer_brand_model(submission)
        pair = (normalize_key(brand), normalize_key(model))
        if pair in existing_pairs:
            duplicate_ids.append(submission.id)
            continue
        curated = curate_submission_to_device(submission, existing_slugs=existing_slugs)
        devices.append(curated)
        new_devices.append(curated)
        curated_ids.append(submission.id)
        existing_pairs.add(pair)
    if new_devices:
        write_jsonl(devices_path, devices)
    return new_devices, curated_ids, duplicate_ids


def apply_queue_to_parts_and_links(
    submissions: list[Submission],
    *,
    devices_path: Path = DEVICES_JSONL,
    parts_path: Path = PARTS_MASTER_JSONL,
    links_path: Path = DEVICE_PARTS_JSONL,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    devices = load_jsonl(devices_path)
    parts_master = load_jsonl(parts_path)
    device_parts = load_jsonl(links_path)
    existing_pairs = build_known_pair_index(devices)
    existing_slugs = {str(item.get("device_slug", "")).strip() for item in devices if item.get("device_slug")}
    device_slug_index = build_device_slug_index(devices)
    part_index = {
        build_part_key(item.get("part_number", ""), item.get("part_name", "")): item
        for item in parts_master
    }
    existing_links = {
        (
            normalize_space(item.get("device_slug", "")),
            normalize_space(item.get("part_slug", "")),
            normalize_space(",".join(item.get("designators", []))),
        )
        for item in device_parts
    }

    added_parts: list[dict[str, Any]] = []
    added_links: list[dict[str, Any]] = []
    touched_submission_ids: list[int] = []

    for submission in submissions:
        if not (
            submission.matched_part_name
            or submission.matched_part_number
            or submission.lookup_kind.startswith("datasheet")
            or submission.lookup_kind == "part_media"
        ):
            continue

        curated_part = curate_submission_to_part(submission)
        if not curated_part:
            continue

        part_key = build_part_key(curated_part["part_number"], curated_part["part_name"])
        existing_part = part_index.get(part_key)
        if existing_part:
            for field in [
                "description",
                "datasheet_url",
                "datasheet_file_id",
                "category",
                "ipn",
                "kicad_symbol",
                "kicad_footprint",
                "kicad_reference",
            ]:
                if normalize_space(curated_part.get(field, "")) and not normalize_space(existing_part.get(field, "")):
                    existing_part[field] = curated_part[field]
            existing_part["keywords"] = sorted(set(existing_part.get("keywords", []) + curated_part.get("keywords", [])))
            if isinstance(existing_part.get("parameters"), dict):
                existing_part["parameters"].update(curated_part.get("parameters", {}))
            else:
                existing_part["parameters"] = curated_part.get("parameters", {})
            part_slug = existing_part["part_slug"]
        else:
            parts_master.append(curated_part)
            part_index[part_key] = curated_part
            added_parts.append(curated_part)
            part_slug = curated_part["part_slug"]

        device_slug = None
        if submission.query_text or submission.recognized_model:
            device_slug = device_slug_index.get((normalize_key(infer_brand_model(submission)[0]), normalize_key(infer_brand_model(submission)[1])))
            if not device_slug:
                inferred_slug, new_devices, new_device_ids = infer_device_slug_for_submission(
                    submission,
                    devices,
                    existing_pairs=existing_pairs,
                    existing_slugs=existing_slugs,
                )
                if new_devices:
                    device_slug_index.update(build_device_slug_index(devices))
                    touched_submission_ids.extend(new_device_ids)
                device_slug = inferred_slug

        if device_slug:
            designators = []
            raw_designator = normalize_space(submission.raw_payload_json.get("designator", ""))
            if raw_designator:
                designators = [raw_designator]
            link_key = (device_slug, part_slug, normalize_space(",".join(designators)))
            if link_key not in existing_links:
                link = {
                    "device_slug": device_slug,
                    "part_slug": part_slug,
                    "quantity": 1,
                    "designators": designators,
                    "source_url": normalize_space(submission.raw_payload_json.get("source_url", "")),
                    "confidence": max(0.35, min(0.95, float(submission.raw_payload_json.get("confidence", 0.6) or 0.6))),
                    "stock_location": "",
                    "evidence_url": normalize_space(submission.raw_payload_json.get("evidence_url", "")),
                    "evidence_timecode": normalize_space(submission.raw_payload_json.get("evidence_timecode", "")) or None,
                }
                device_parts.append(link)
                existing_links.add(link_key)
                added_links.append(link)

        touched_submission_ids.append(submission.id)

    if added_parts or added_links:
        write_jsonl(parts_path, parts_master)
        write_jsonl(links_path, device_parts)
        write_jsonl(devices_path, devices)
    return added_parts, added_links, sorted(set(touched_submission_ids))


def rebuild_catalog_artifacts() -> None:
    run_command(
        ["python3", str(BUILD_SCRIPT), "validate"],
        cwd=REPO_ROOT,
    )
    run_command(
        ["python3", str(BUILD_SCRIPT), "export-all"],
        cwd=REPO_ROOT,
    )


def update_submission_status(
    *,
    d1_binding: str,
    remote: bool,
    ids: list[int],
    status: str,
) -> None:
    if not ids:
        return
    ids_sql = ",".join(str(int(item)) for item in ids)
    sql = f"""
    UPDATE recycled_device_submissions
    SET status = '{status}'
    WHERE id IN ({ids_sql});
    """
    run_d1_query(sql, d1_binding=d1_binding, remote=remote)


def ensure_git_clean() -> None:
    status = run_command(["git", "status", "--porcelain"], cwd=REPO_ROOT).strip()
    if status:
        raise RuntimeError("Repozytorium nie jest czyste. Zacommituj lub stashuj zmiany przed sync.")


def create_git_commit_and_optional_pr(
    *,
    mode: str,
    push: bool,
    create_pr: bool,
    base_branch: str,
    branch_prefix: str,
) -> str:
    if mode == "none":
        return ""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    branch_name = f"{branch_prefix}{timestamp}"
    run_command(["git", "checkout", "-b", branch_name], cwd=REPO_ROOT)
    run_command(
        [
            "git",
            "add",
            str(DEVICES_JSONL.relative_to(REPO_ROOT)),
            str(PARTS_MASTER_JSONL.relative_to(REPO_ROOT)),
            str(DEVICE_PARTS_JSONL.relative_to(REPO_ROOT)),
            str((PROJECT_13_ROOT / "data" / "inventory.csv").relative_to(REPO_ROOT)),
            str((PROJECT_13_ROOT / "data" / "recycled_parts_seed.sql").relative_to(REPO_ROOT)),
            str((PROJECT_13_ROOT / "data" / "mcp_reuse_catalog.json").relative_to(REPO_ROOT)),
            str((PROJECT_13_ROOT / "data" / "inventree_import.jsonl").relative_to(REPO_ROOT)),
        ],
        cwd=REPO_ROOT,
    )
    run_command(
        [
            "git",
            "commit",
            "-m",
            "Auto-kuracja queued zgłoszeń Telegram do katalogu donorów GitHub-first.",
        ],
        cwd=REPO_ROOT,
    )
    if push:
        run_command(["git", "push", "-u", "origin", branch_name], cwd=REPO_ROOT)
    if create_pr:
        run_command(
            [
                "gh",
                "pr",
                "create",
                "--base",
                base_branch,
                "--title",
                f"Auto-curation recycled queue {timestamp}",
                "--body",
                (
                    "## Summary\n"
                    "- Auto-curated queued Telegram submissions into devices catalog.\n"
                    "- Rebuilt ecoEDA/D1/MCP artifacts from canonical JSONL.\n\n"
                    "## Test plan\n"
                    "- [x] python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py validate\n"
                    "- [x] python3 PROJEKTY/13_baza_czesci_recykling/scripts/build_catalog_artifacts.py export-all\n"
                ),
            ],
            cwd=REPO_ROOT,
        )
    return branch_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronizuje queued zgłoszenia z recycled_device_submissions do katalogu JSONL (GitHub-first)."
    )
    parser.add_argument("--d1-binding", default="DB", help="Binding D1 w wrangler (domyślnie: DB).")
    parser.add_argument("--remote", action="store_true", default=True, help="Czy wykonywać zapytania na zdalnym D1.")
    parser.add_argument("--local", action="store_true", help="Nadpisz i użyj lokalnego D1 (bez --remote).")
    parser.add_argument("--limit", type=int, default=25, help="Limit rekordów queued do pobrania.")
    parser.add_argument("--apply", action="store_true", help="Zapisz zmiany do devices.jsonl i przebuduj artefakty.")
    parser.add_argument(
        "--git-mode",
        choices=["none", "commit", "pr"],
        default="none",
        help="Tryb git po udanym --apply.",
    )
    parser.add_argument("--push", action="store_true", help="Wypchnij branch przy --git-mode commit/pr.")
    parser.add_argument("--create-pr", action="store_true", help="Utwórz PR przez gh po pushu.")
    parser.add_argument("--base-branch", default="main", help="Gałąź bazowa dla PR.")
    parser.add_argument(
        "--branch-prefix",
        default="curation/recycled-parts-",
        help="Prefix automatycznej gałęzi.",
    )
    parser.add_argument(
        "--sync-d1-status",
        action="store_true",
        help="Zaktualizuj statusy w D1 po udanym --apply (curated_github / curated_duplicate).",
    )
    parser.add_argument(
        "--status-curated",
        default="curated_github",
        help="Status D1 dla nowych rekordów po sync.",
    )
    parser.add_argument(
        "--status-duplicate",
        default="curated_duplicate",
        help="Status D1 dla duplikatów znalezionych w katalogu.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    remote = False if args.local else bool(args.remote)
    submissions = fetch_queued_submissions(
        d1_binding=args.d1_binding,
        remote=remote,
        limit=args.limit,
    )

    if not submissions:
        print(json.dumps({"status": "ok", "message": "Brak rekordów queued."}, ensure_ascii=False))
        return 0

    preview: list[dict[str, Any]] = []
    for item in submissions:
        brand, model = infer_brand_model(item)
        preview.append(
            {
                "submission_id": item.id,
                "brand": brand,
                "model": model,
                "query_text": item.query_text,
            }
        )

    if not args.apply:
        print(
            json.dumps(
                {
                    "status": "dry_run",
                    "queued_count": len(submissions),
                    "preview": preview,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.git_mode != "none":
        ensure_git_clean()

    new_devices, curated_ids, duplicate_ids = apply_queue_to_devices(submissions)
    added_parts, added_links, touched_part_submission_ids = apply_queue_to_parts_and_links(submissions)
    if new_devices or added_parts or added_links:
        rebuild_catalog_artifacts()
        create_git_commit_and_optional_pr(
            mode=args.git_mode,
            push=args.push,
            create_pr=args.create_pr or args.git_mode == "pr",
            base_branch=args.base_branch,
            branch_prefix=args.branch_prefix,
        )

    if args.sync_d1_status:
        update_submission_status(
            d1_binding=args.d1_binding,
            remote=remote,
            ids=sorted(set(curated_ids + touched_part_submission_ids)),
            status=args.status_curated,
        )
        update_submission_status(
            d1_binding=args.d1_binding,
            remote=remote,
            ids=duplicate_ids,
            status=args.status_duplicate,
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "queued_count": len(submissions),
                "curated_count": len(curated_ids),
                "duplicate_count": len(duplicate_ids),
                "curated_submission_ids": curated_ids,
                "part_submission_ids": touched_part_submission_ids,
                "duplicate_submission_ids": duplicate_ids,
                "added_devices": [item["device_slug"] for item in new_devices],
                "added_parts": [item["part_slug"] for item in added_parts],
                "added_device_links": [
                    f"{item['device_slug']}->{item['part_slug']}" for item in added_links
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
