from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.storage import DEFAULT_DB_PATH, OperationalStore  # noqa: E402


def build_snapshot_markdown(store: OperationalStore) -> str:
    observations = store.fetch_all_payloads("observations")
    events = store.fetch_all_payloads("events")
    recommendations = store.fetch_all_payloads("recommendations")

    provider_counts = Counter(item["provider"]["provider_id"] for item in observations)
    pond_counts = Counter(item["pond"]["pond_id"] for item in observations)
    reason_counts = Counter()
    for recommendation in recommendations:
        reason_counts.update(recommendation.get("reason_codes", []))

    lines = [
        "# Snapshot wiedzy operacyjnej",
        "",
        "Ten raport jest eksportem wiedzy z bazy operacyjnej. Nie zawiera pełnego dumpa surowych danych providerów.",
        "",
        "## Podsumowanie",
        "",
        f"- Liczba obserwacji: {len(observations)}",
        f"- Liczba zdarzeń: {len(events)}",
        f"- Liczba rekomendacji: {len(recommendations)}",
        "",
        "## Providerzy",
        "",
    ]

    if provider_counts:
        for provider_id, count in provider_counts.most_common():
            lines.append(f"- `{provider_id}`: {count} obserwacji")
    else:
        lines.append("- Brak danych operacyjnych")

    lines.extend(["", "## Stawy", ""])
    if pond_counts:
        for pond_id, count in pond_counts.most_common():
            lines.append(f"- `{pond_id}`: {count} obserwacji")
    else:
        lines.append("- Brak danych operacyjnych")

    lines.extend(["", "## Najczęstsze reason_codes", ""])
    if reason_counts:
        for code, count in reason_counts.most_common():
            lines.append(f"- `{code}`: {count}")
    else:
        lines.append("- Brak rekomendacji do analizy")

    if recommendations:
        lines.extend(["", "## Ostatnia rekomendacja", ""])
        lines.append("```json")
        lines.append(json.dumps(recommendations[-1], indent=2, ensure_ascii=False))
        lines.append("```")

    return "\n".join(lines) + "\n"


def main() -> None:
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB_PATH
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    store = OperationalStore(db_path)
    markdown = build_snapshot_markdown(store)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
