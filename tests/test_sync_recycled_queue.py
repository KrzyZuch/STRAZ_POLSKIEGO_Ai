import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pipelines.sync_recycled_queue import (
    Submission,
    apply_queue_to_devices,
    apply_queue_to_parts_and_links,
    infer_brand_model,
    load_jsonl,
    parse_json_payload_from_wrangler,
)


class SyncRecycledQueueTests(unittest.TestCase):
    def test_parse_json_payload_from_wrangler_with_noise(self) -> None:
        output = """
npm warn Unknown env config "devdir". This will stop working.

 ⛅️ wrangler 4.69.0
[
  {
    "results": [
      {
        "id": 7,
        "query_text": "Sonoff Basic"
      }
    ],
    "success": true
  }
]
"""
        payload = parse_json_payload_from_wrangler(output)
        self.assertIsInstance(payload, list)
        self.assertEqual(payload[0]["results"][0]["id"], 7)

    def test_infer_brand_model_prefers_recognized_and_payload(self) -> None:
        submission = Submission(
            id=101,
            lookup_kind="device_media",
            query_text="router wr740n",
            recognized_brand="TP-Link",
            recognized_model="TL-WR740N",
            matched_device_id=None,
            matched_part_name="",
            matched_part_number="",
            master_part_id=None,
            attachment_file_id="",
            attachment_mime_type="",
            raw_payload_json={"brand": "Ignored", "model": "Ignored"},
            created_at="",
        )
        brand, model = infer_brand_model(submission)
        self.assertEqual(brand, "TP-Link")
        self.assertEqual(model, "TL-WR740N")

    def test_apply_queue_to_devices_adds_only_non_duplicates(self) -> None:
        with TemporaryDirectory() as temp_dir:
            devices_path = Path(temp_dir) / "devices.jsonl"
            devices_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "device_slug": "sonoff-basic",
                                "brand": "Sonoff",
                                "model": "Basic",
                                "canonical_name": "Sonoff Basic",
                                "device_category": "smart_switch",
                                "description": "existing",
                                "known_aliases": [],
                                "serial_markers": [],
                                "donor_rank": 0.88,
                                "teardown_url": "",
                                "source_url": "",
                                "notes": "",
                            },
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                        ""
                    ]
                ),
                encoding="utf-8",
            )

            queued = [
                Submission(
                    id=1,
                    lookup_kind="device_media",
                    query_text="Sonoff Basic",
                    recognized_brand="Sonoff",
                    recognized_model="Basic",
                    matched_device_id=None,
                    matched_part_name="",
                    matched_part_number="",
                    master_part_id=None,
                    attachment_file_id="",
                    attachment_mime_type="",
                    raw_payload_json={},
                    created_at="2026-04-15T00:00:00Z",
                ),
                Submission(
                    id=2,
                    lookup_kind="device_media",
                    query_text="HP LaserJet P1102",
                    recognized_brand="HP",
                    recognized_model="LaserJet P1102",
                    matched_device_id=None,
                    matched_part_name="",
                    matched_part_number="",
                    master_part_id=None,
                    attachment_file_id="abc",
                    attachment_mime_type="image/jpeg",
                    raw_payload_json={"confidence": 0.77},
                    created_at="2026-04-15T00:01:00Z",
                ),
            ]

            new_devices, curated_ids, duplicate_ids = apply_queue_to_devices(
                queued,
                devices_path=devices_path,
            )

            self.assertEqual(len(new_devices), 1)
            self.assertEqual(curated_ids, [2])
            self.assertEqual(duplicate_ids, [1])

            devices = load_jsonl(devices_path)
            self.assertEqual(len(devices), 2)
            self.assertEqual(devices[-1]["brand"], "HP")
            self.assertEqual(devices[-1]["model"], "LaserJet P1102")
            self.assertEqual(devices[-1]["donor_rank"], 0.77)

    def test_apply_queue_to_parts_and_links_adds_part_master_and_relation(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            devices_path = temp_path / "devices.jsonl"
            parts_path = temp_path / "parts_master.jsonl"
            links_path = temp_path / "device_parts.jsonl"

            devices_path.write_text(
                json.dumps(
                    {
                        "device_slug": "hp-laserjet-p1102",
                        "brand": "HP",
                        "model": "LaserJet P1102",
                        "canonical_name": "HP LaserJet P1102",
                        "device_category": "printer",
                        "description": "existing",
                        "known_aliases": [],
                        "serial_markers": [],
                        "donor_rank": 0.81,
                        "teardown_url": "",
                        "source_url": "",
                        "notes": "",
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n",
                encoding="utf-8",
            )
            parts_path.write_text("", encoding="utf-8")
            links_path.write_text("", encoding="utf-8")

            submissions = [
                Submission(
                    id=11,
                    lookup_kind="datasheet_pdf_ingest",
                    query_text="HP LaserJet P1102",
                    recognized_brand="HP",
                    recognized_model="LaserJet P1102",
                    matched_device_id=None,
                    matched_part_name="TDA7294",
                    matched_part_number="TDA7294",
                    master_part_id=None,
                    attachment_file_id="pdf-file",
                    attachment_mime_type="application/pdf",
                    raw_payload_json={"category": "amplifier_ic", "parameters": {"Supply": "10-40V"}},
                    created_at="2026-04-15T00:02:00Z",
                )
            ]

            added_parts, added_links, touched_ids = apply_queue_to_parts_and_links(
                submissions,
                devices_path=devices_path,
                parts_path=parts_path,
                links_path=links_path,
            )

            self.assertEqual(touched_ids, [11])
            self.assertEqual(len(added_parts), 1)
            self.assertEqual(len(added_links), 1)

            parts = load_jsonl(parts_path)
            links = load_jsonl(links_path)
            self.assertEqual(parts[0]["part_number"], "TDA7294")
            self.assertEqual(parts[0]["datasheet_file_id"], "pdf-file")
            self.assertEqual(links[0]["device_slug"], "hp-laserjet-p1102")
            self.assertEqual(links[0]["part_slug"], parts[0]["part_slug"])


if __name__ == "__main__":
    unittest.main()
