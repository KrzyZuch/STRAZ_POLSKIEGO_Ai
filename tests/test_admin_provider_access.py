from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from api.admin_provider_access import (
    list_providers_text,
    provider_status_text,
    rotate_provider_token_text,
)
from api.storage import OperationalStore, ProviderNotFoundError


class AdminProviderAccessTests(unittest.TestCase):
    def test_admin_views_and_rotation_work(self) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "providers.db"
            store = OperationalStore(db_path)
            registration = store.register_provider(
                {
                    "provider_id": "community-demo-admin-01",
                    "provider_kind": "community",
                    "provider_label": "Community Admin Node",
                    "node_class": "old_smartphone",
                    "supports_water_quality": True,
                    "supports_flow_monitoring": False,
                    "supports_edge_vision_summary": True,
                }
            )

            listing = list_providers_text(store)
            self.assertIn("community-demo-admin-01", listing)
            self.assertIn("Community Admin Node", listing)

            status = provider_status_text(store, "community-demo-admin-01")
            self.assertIn("provider_kind: `community`", status)
            self.assertIn("schema_version: `v1`", status)

            old_token = registration["write_token"]
            rotated_payload = json.loads(
                rotate_provider_token_text(store, "community-demo-admin-01")
            )
            new_token = rotated_payload["write_token"]
            self.assertNotEqual(old_token, new_token)
            self.assertFalse(store.verify_provider_token("community-demo-admin-01", old_token))
            self.assertTrue(store.verify_provider_token("community-demo-admin-01", new_token))

    def test_status_for_missing_provider_raises(self) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "providers.db"
            store = OperationalStore(db_path)
            with self.assertRaises(ProviderNotFoundError):
                provider_status_text(store, "missing-provider")


if __name__ == "__main__":
    unittest.main()
