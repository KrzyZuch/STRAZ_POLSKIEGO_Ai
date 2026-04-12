from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from api.storage import OperationalStore
from adapters.utils import load_sample_json
from models.fish_pond.recommendation_engine import generate_recommendation
from pipelines.export_knowledge_snapshot import build_snapshot_markdown


class KnowledgeSnapshotTests(unittest.TestCase):
    def test_snapshot_contains_counts_and_reason_codes(self) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "knowledge.db"
            store = OperationalStore(db_path)
            store.register_provider(
                {
                    "provider_id": "community-demo-node-01",
                    "provider_kind": "community",
                    "provider_label": "Community Node",
                    "node_class": "old_smartphone",
                    "supports_water_quality": True,
                    "supports_flow_monitoring": True,
                    "supports_edge_vision_summary": True,
                }
            )

            observation = load_sample_json("fish_pond_observation.json")
            event = load_sample_json("fish_behavior_event.json")
            recommendation = generate_recommendation(observation, last_event=event)

            store.save_observation(observation)
            store.save_event(event)
            store.save_recommendation(recommendation)

            markdown = build_snapshot_markdown(store)

            self.assertIn("Liczba obserwacji: 1", markdown)
            self.assertIn("community-demo-node-01", markdown)
            self.assertIn("SURFACE_ACTIVITY_ANOMALY", markdown)


if __name__ == "__main__":
    unittest.main()
