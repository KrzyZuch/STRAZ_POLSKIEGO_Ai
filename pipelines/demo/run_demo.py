from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.mock.adapter import (  # noqa: E402
    check_status as mock_check_status,
    fetch_or_receive as mock_fetch_or_receive,
    normalize as mock_normalize,
    send_result as mock_send_result,
    validate as mock_validate,
)
from adapters.provider_a.adapter import (  # noqa: E402
    fetch_or_receive as provider_a_fetch_or_receive,
    normalize as provider_a_normalize,
    validate as provider_a_validate,
)
from models.fish_pond.recommendation_engine import generate_recommendation  # noqa: E402


def run_mock_demo() -> Dict[str, Any]:
    observation = mock_validate(mock_normalize(mock_fetch_or_receive("observation")))
    event = mock_validate(mock_normalize(mock_fetch_or_receive("event")))
    result = generate_recommendation(observation, last_event=event)
    return mock_send_result(result)


def run_provider_a_demo() -> Dict[str, Any]:
    raw_observation = provider_a_fetch_or_receive("observation")
    raw_event = provider_a_fetch_or_receive("event")
    observation = provider_a_validate(provider_a_normalize(raw_observation))
    event = provider_a_validate(provider_a_normalize(raw_event))
    return generate_recommendation(observation, last_event=event)


def main() -> None:
    payload = {
        "mock_provider_status": mock_check_status(),
        "mock_demo_result": run_mock_demo(),
        "provider_a_demo_result": run_provider_a_demo(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
