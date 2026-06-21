import hashlib
import hmac
import os
import time
from types import SimpleNamespace
from urllib.parse import urlencode

from fastapi.testclient import TestClient

os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test-token")
os.environ.setdefault("SLACK_SIGNING_SECRET", "test-signing-secret")

from app.main import app


def _signed_headers(body: str) -> dict[str, str]:
    timestamp = str(int(time.time()))
    base = f"v0:{timestamp}:{body}".encode()
    digest = hmac.new(
        os.environ["SLACK_SIGNING_SECRET"].encode(),
        base,
        hashlib.sha256,
    ).hexdigest()
    return {
        "content-type": "application/x-www-form-urlencoded",
        "x-slack-request-timestamp": timestamp,
        "x-slack-signature": f"v0={digest}",
    }


def _slash_command_body(command: str, text: str) -> str:
    return urlencode(
        {
            "token": "legacy-verification-token",
            "team_id": "T123",
            "team_domain": "test",
            "channel_id": "C123",
            "channel_name": "bot-testing",
            "user_id": "U123",
            "user_name": "tester",
            "command": command,
            "text": text,
            "response_url": "https://hooks.slack.com/commands/T123/B123/test",
            "trigger_id": "123.456",
        }
    )


def test_slack_endpoint_dispatches_all_commands(monkeypatch) -> None:
    sent_messages: list[dict] = []

    class FakeWebhookClient:
        def __init__(self, url, proxy=None, ssl=None):
            self.url = url

        def send_dict(self, body):
            sent_messages.append(body)
            return SimpleNamespace(status_code=200, body="ok")

    monkeypatch.setattr(
        "slack_bolt.context.respond.respond.WebhookClient",
        FakeWebhookClient,
    )

    client = TestClient(app)
    commands = [
        ("/dp-resistor", "brown black red gold", "Resistance"),
        ("/dp-datasheet", "STM32G474RET6", "Datasheet links"),
        ("/dp-pinout", "ESP32-C3", "Pinout"),
    ]

    for command, text, expected in commands:
        before = len(sent_messages)
        body = _slash_command_body(command, text)
        response = client.post("/slack/events", content=body, headers=_signed_headers(body))

        assert response.status_code == 200
        for _ in range(50):
            if len(sent_messages) > before:
                break
            time.sleep(0.05)
        assert len(sent_messages) == before + 1
        assert sent_messages[-1]["response_type"] == "ephemeral"
        assert expected in sent_messages[-1]["text"]
