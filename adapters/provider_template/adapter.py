from __future__ import annotations

from typing import Any, Dict


def fetch_or_receive(resource: str = "observation") -> Dict[str, Any]:
    raise NotImplementedError("Zaimplementuj pobieranie lub odbiór danych providera.")


def normalize(payload: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError("Zaimplementuj mapowanie formatu providera na schemat Straży Przyszłości.")


def validate(payload: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError("Zaimplementuj walidację po normalizacji do wspólnego schematu.")


def send_result(result: Dict[str, Any]) -> Dict[str, Any]:
    raise NotImplementedError("Zaimplementuj zwrot wyniku do providera.")


def check_status() -> Dict[str, Any]:
    raise NotImplementedError("Zaimplementuj diagnostykę stanu integracji providera.")
