import json
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from http.client import HTTPConnection

from api.server import create_server
from adapters.utils import load_sample_json


class APIServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.db_path = Path(cls.temp_dir.name) / "fish_pond_test.db"
        cls.server = create_server("127.0.0.1", 18080, db_path=cls.db_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=1)
        cls.temp_dir.cleanup()

    def post_json(self, path: str, payload: dict, token: str | None = None) -> tuple[int, dict]:
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["X-Provider-Token"] = token
        connection = HTTPConnection("127.0.0.1", 18080, timeout=5)
        connection.request(
            "POST",
            path,
            body=json.dumps(payload).encode("utf-8"),
            headers=headers,
        )
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        connection.close()
        return response.status, data

    def post_json_to_port(
        self,
        port: int,
        path: str,
        payload: dict,
        token: str | None = None,
    ) -> tuple[int, dict]:
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["X-Provider-Token"] = token
        connection = HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request(
            "POST",
            path,
            body=json.dumps(payload).encode("utf-8"),
            headers=headers,
        )
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        connection.close()
        return response.status, data

    def get_json(self, path: str) -> tuple[int, dict]:
        connection = HTTPConnection("127.0.0.1", 18080, timeout=5)
        connection.request("GET", path)
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        connection.close()
        return response.status, data

    def test_provider_registration_and_status(self) -> None:
        payload = {
            "provider_id": "community-demo-test-01",
            "provider_kind": "community",
            "provider_label": "Test Community Node",
            "node_class": "old_smartphone",
            "supports_water_quality": True,
            "supports_flow_monitoring": True,
            "supports_edge_vision_summary": True,
        }
        status, data = self.post_json("/v1/providers/register", payload)
        self.assertEqual(status, 201)
        self.assertEqual(data["registration_status"], "registered")
        self.assertIn("write_token", data)

        status, data = self.get_json("/v1/providers/community-demo-test-01/status")
        self.assertEqual(status, 200)
        self.assertEqual(data["provider_id"], "community-demo-test-01")

    def test_duplicate_provider_registration_returns_conflict(self) -> None:
        payload = {
            "provider_id": "community-demo-duplicate-01",
            "provider_kind": "community",
            "provider_label": "Duplicate Provider",
        }
        first_status, _ = self.post_json("/v1/providers/register", payload)
        second_status, second_data = self.post_json("/v1/providers/register", payload)
        self.assertEqual(first_status, 201)
        self.assertEqual(second_status, 409)
        self.assertIn("error", second_data)

    def test_recommendation_endpoint(self) -> None:
        register_status, register_data = self.post_json(
            "/v1/providers/register",
            {
                "provider_id": "community-demo-node-01",
                "provider_kind": "community",
                "provider_label": "Community Old Smartphone Gateway",
                "node_class": "old_smartphone",
                "supports_water_quality": True,
                "supports_flow_monitoring": True,
                "supports_edge_vision_summary": True,
            },
        )
        self.assertEqual(register_status, 201)
        token = register_data["write_token"]

        observation = load_sample_json("fish_pond_observation.json")
        event = load_sample_json("fish_behavior_event.json")
        status, data = self.post_json(
            "/v1/recommendations/fish-pond",
            {"observation": observation, "last_behavior_event": event},
            token=token,
        )
        self.assertEqual(status, 200)
        self.assertEqual(data["schema_version"], "v1")
        self.assertIn("recommendation", data)
        self.assertIn("reason_codes", data)

    def test_observation_requires_provider_token(self) -> None:
        self.post_json(
            "/v1/providers/register",
            {
                "provider_id": "community-demo-auth-01",
                "provider_kind": "community",
                "provider_label": "Community Auth Test",
            },
        )
        observation = load_sample_json("fish_pond_observation.json")
        observation["provider"]["provider_id"] = "community-demo-auth-01"
        status, data = self.post_json("/v1/observations", observation)
        self.assertEqual(status, 401)
        self.assertIn("error", data)

    def test_provider_token_rotation_invalidates_old_token(self) -> None:
        register_status, register_data = self.post_json(
            "/v1/providers/register",
            {
                "provider_id": "community-demo-rotate-01",
                "provider_kind": "community",
                "provider_label": "Community Rotate Test",
            },
        )
        self.assertEqual(register_status, 201)
        old_token = register_data["write_token"]

        rotate_status, rotate_data = self.post_json(
            "/v1/providers/community-demo-rotate-01/tokens/rotate",
            {},
            token=old_token,
        )
        self.assertEqual(rotate_status, 200)
        self.assertEqual(rotate_data["rotation_status"], "rotated")
        new_token = rotate_data["write_token"]
        self.assertNotEqual(old_token, new_token)

        observation = load_sample_json("fish_pond_observation.json")
        observation["provider"]["provider_id"] = "community-demo-rotate-01"

        invalid_status, _ = self.post_json("/v1/observations", observation, token=old_token)
        self.assertEqual(invalid_status, 401)

        valid_status, valid_data = self.post_json("/v1/observations", observation, token=new_token)
        self.assertEqual(valid_status, 202)
        self.assertEqual(valid_data["provider_id"], "community-demo-rotate-01")

    def test_token_rotation_for_missing_provider_returns_not_found(self) -> None:
        status, data = self.post_json(
            "/v1/providers/missing-provider/tokens/rotate",
            {},
            token="invalid-token",
        )
        self.assertEqual(status, 404)
        self.assertIn("error", data)

    def test_invalid_provider_id_returns_bad_request(self) -> None:
        status, data = self.post_json(
            "/v1/providers/register",
            {
                "provider_id": "CommunityNode01",
                "provider_kind": "community",
                "provider_label": "Invalid Provider Id",
            },
        )
        self.assertEqual(status, 400)
        self.assertIn("error", data)

    def test_environment_policy_rejects_provider_for_wrong_deployment(self) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "fish_pond_prod.db"
            server = create_server(
                "127.0.0.1",
                0,
                db_path=db_path,
                deployment_environment="prod",
                allowed_provider_environments={"prod"},
            )
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            time.sleep(0.05)
            try:
                status, data = self.post_json_to_port(
                    port,
                    "/v1/providers/register",
                    {
                        "provider_id": "community-demo-node-77",
                        "provider_kind": "community",
                        "provider_label": "Wrong Environment Node",
                    },
                )
                self.assertEqual(status, 403)
                self.assertIn("error", data)

                status, data = self.post_json_to_port(
                    port,
                    "/v1/providers/register",
                    {
                        "provider_id": "community-prod-node-77",
                        "provider_kind": "community",
                        "provider_label": "Prod Environment Node",
                    },
                )
                self.assertEqual(status, 201)
                self.assertIn("write_token", data)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=1)


if __name__ == "__main__":
    unittest.main()
