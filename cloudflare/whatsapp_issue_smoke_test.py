from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def normalize_base_url(base_url: str) -> str:
    normalized = base_url.strip()
    if not normalized:
        raise ValueError("Base URL nie może być pusty.")
    if not normalized.startswith(("http://", "https://")):
        normalized = f"https://{normalized}"
    return normalized.rstrip("/")


def build_text_message_payload(sender: str, message: str) -> dict[str, Any]:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test-waba-id",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "48123456789",
                                "phone_number_id": "test-phone-number-id",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test Sender"},
                                    "wa_id": sender,
                                }
                            ],
                            "messages": [
                                {
                                    "from": sender,
                                    "id": "wamid.TEST_MESSAGE_ID",
                                    "timestamp": "1712908800",
                                    "text": {"body": message},
                                    "type": "text",
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def sign_payload(payload_json: str, app_secret: str) -> str:
    digest = hmac.new(
        app_secret.encode("utf-8"),
        payload_json.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def http_request(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 15,
) -> tuple[int, str]:
    final_headers = headers.copy() if headers else {}
    body: bytes | None = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        final_headers.setdefault("Content-Type", "application/json")

    request = Request(url, data=body, headers=final_headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def run_smoke_test(
    base_url: str,
    sender: str,
    message: str,
    app_secret: str | None = None,
    verify_token: str | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    normalized_base_url = normalize_base_url(base_url)
    webhook_url = f"{normalized_base_url}/integrations/whatsapp/webhook"

    result: dict[str, Any] = {
        "base_url": normalized_base_url,
        "webhook_url": webhook_url,
    }

    if verify_token:
        query = urlencode(
            {
                "hub.mode": "subscribe",
                "hub.challenge": "123456789",
                "hub.verify_token": verify_token,
            }
        )
        status, body = http_request("GET", f"{webhook_url}?{query}", timeout=timeout)
        result["verify"] = {"status": status, "body": body}

    payload = build_text_message_payload(sender, message)
    headers: dict[str, str] = {}
    if app_secret:
        payload_json = json.dumps(payload)
        headers["X-Hub-Signature-256"] = sign_payload(payload_json, app_secret)
        status, body = http_request(
            "POST",
            webhook_url,
            payload=json.loads(payload_json),
            headers=headers,
            timeout=timeout,
        )
    else:
        status, body = http_request(
            "POST",
            webhook_url,
            payload=payload,
            headers=headers,
            timeout=timeout,
        )

    try:
        parsed_body: Any = json.loads(body)
    except json.JSONDecodeError:
        parsed_body = body

    result["post"] = {
        "status": status,
        "body": parsed_body,
    }
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smoke test dla mostu WhatsApp -> GitHub Issues."
    )
    parser.add_argument(
        "base_url",
        help="Bazowy adres wdrożonego Worker'a, np. https://fish-pond-api-v1.<subdomain>.workers.dev",
    )
    parser.add_argument(
        "--sender",
        default="48500100200",
        help="Numer testowego nadawcy w formacie międzynarodowym bez spacji.",
    )
    parser.add_argument(
        "--message",
        default="Pomysl: test webhooka WhatsApp do Issues",
        help="Treść wiadomości testowej.",
    )
    parser.add_argument(
        "--app-secret",
        default=None,
        help="Opcjonalny WHATSAPP_APP_SECRET do podpisania payloadu jak Meta.",
    )
    parser.add_argument(
        "--verify-token",
        default=None,
        help="Opcjonalny token do testu weryfikacji GET webhooka.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout pojedynczego żądania w sekundach.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_smoke_test(
            args.base_url,
            sender=args.sender,
            message=args.message,
            app_secret=args.app_secret,
            verify_token=args.verify_token,
            timeout=args.timeout,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
