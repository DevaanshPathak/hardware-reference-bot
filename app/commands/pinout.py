import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from slack_bolt import App


USAGE = "Usage: `/dp-pinout STM32G474`"
MCU_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "mcus.json"


def normalize_mcu_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


@lru_cache
def load_mcus() -> dict[str, dict[str, Any]]:
    with MCU_DATA_PATH.open(encoding="utf-8") as file:
        data = json.load(file)
    return data["mcus"]


def available_mcus() -> list[str]:
    return sorted(mcu["display_name"] for mcu in load_mcus().values())


def find_mcu(text: str) -> dict[str, Any] | None:
    requested = normalize_mcu_name(text)
    if not requested:
        return None

    for key, mcu in load_mcus().items():
        names = [key, mcu["display_name"], *mcu.get("aliases", [])]
        if requested in {normalize_mcu_name(name) for name in names}:
            return mcu
    return None


def _format_items(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _format_peripherals(peripherals: dict[str, list[str]]) -> str:
    return "\n".join(
        f"- *{name}:* {'; '.join(entries)}" for name, entries in peripherals.items()
    )


def build_pinout_message(text: str) -> str:
    requested = text.strip()
    if not requested:
        available = ", ".join(f"`{name}`" for name in available_mcus())
        return f":warning: Please include an MCU name. Available MCUs: {available}. {USAGE}"

    mcu = find_mcu(requested)
    if mcu is None:
        available = ", ".join(f"`{name}`" for name in available_mcus())
        return (
            f":warning: I don't have a pinout for `{requested}`. "
            f"Available MCUs: {available}. {USAGE}"
        )

    lines = [
        f"*Pinout: {mcu['display_name']}*",
        f"_{mcu['note']}_",
        "",
        "*Power / Ground*",
        _format_items(mcu["power_ground"]),
        "",
        "*Key Peripherals*",
        _format_peripherals(mcu["peripherals"]),
        "",
        "*Standout Pins*",
        _format_items(mcu["standout_pins"]),
    ]
    return "\n".join(lines)


def register(app: App) -> None:
    @app.command("/dp-pinout")
    def handle_pinout(ack, command, respond, logger):
        ack()
        message = build_pinout_message(command.get("text", ""))
        try:
            respond(response_type="ephemeral", text=message)
        except Exception:
            logger.exception("Failed to send /dp-pinout response")
