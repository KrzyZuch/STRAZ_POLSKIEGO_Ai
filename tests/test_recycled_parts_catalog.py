import importlib.util
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "PROJEKTY"
    / "13_baza_czesci_recykling"
    / "scripts"
    / "build_catalog_artifacts.py"
)


def load_catalog_module():
    spec = importlib.util.spec_from_file_location("build_catalog_artifacts", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RecycledPartsCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_catalog_module()
        cls.devices, cls.parts = cls.module.load_catalog()

    def test_catalog_source_of_truth_loads(self) -> None:
        self.assertGreaterEqual(len(self.devices), 4)
        self.assertGreaterEqual(len(self.parts), 4)

    def test_exported_artifacts_are_reproducible_from_github_catalog(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            inventory_path = temp_path / "inventory.csv"
            d1_sql_path = temp_path / "recycled_parts_seed.sql"
            mcp_path = temp_path / "mcp_reuse_catalog.json"

            self.module.write_inventory_csv(self.devices, self.parts, inventory_path)
            self.module.write_d1_seed_sql(self.devices, self.parts, d1_sql_path)
            self.module.write_mcp_catalog_json(self.devices, self.parts, mcp_path)

            inventory_text = inventory_path.read_text(encoding="utf-8")
            d1_sql_text = d1_sql_path.read_text(encoding="utf-8")
            mcp_payload = json.loads(mcp_path.read_text(encoding="utf-8"))

            self.assertIn("Component Name,Species,Genus", inventory_text)
            self.assertIn("ESP8266EX", inventory_text)
            self.assertIn("INSERT INTO recycled_devices", d1_sql_text)
            self.assertIn("INSERT INTO recycled_part_aliases", d1_sql_text)
            self.assertEqual(mcp_payload["source_of_truth"], "github")
            self.assertEqual(mcp_payload["device_count"], len(self.devices))
            self.assertTrue(
                any(item["display_name"] == "ATmega328P" for item in mcp_payload["part_index"])
            )


if __name__ == "__main__":
    unittest.main()
