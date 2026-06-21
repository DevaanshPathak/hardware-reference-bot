from dataclasses import dataclass
from decimal import Decimal

from slack_bolt import App

from app.data.resistor_codes import (
    ALIASES,
    DIGIT_CODES,
    MULTIPLIERS,
    SUPPORTED_COLORS,
    TOLERANCES,
)


USAGE = "Usage: `/dp-resistor brown black red gold`"


class ResistorInputError(ValueError):
    """Raised when resistor color bands cannot be interpreted."""


@dataclass(frozen=True)
class ResistorResult:
    bands: list[str]
    resistance_ohms: Decimal
    tolerance_percent: Decimal


def normalize_color(color: str) -> str:
    normalized = color.strip().lower()
    return ALIASES.get(normalized, normalized)


def calculate_resistor(text: str) -> ResistorResult:
    raw_bands = [part for part in text.split() if part.strip()]

    if len(raw_bands) not in (4, 5):
        raise ResistorInputError(f"I need exactly 4 or 5 color bands. {USAGE}")

    bands = [normalize_color(band) for band in raw_bands]
    known_colors = set(DIGIT_CODES) | set(MULTIPLIERS) | set(TOLERANCES)
    unknown = sorted({band for band in bands if band not in known_colors})
    if unknown:
        supported = ", ".join(SUPPORTED_COLORS)
        unknown_text = ", ".join(f"`{color}`" for color in unknown)
        raise ResistorInputError(
            f"Unknown color(s): {unknown_text}. Supported colors: {supported}. {USAGE}"
        )

    digit_count = 2 if len(bands) == 4 else 3
    digit_bands = bands[:digit_count]
    multiplier_band = bands[digit_count]
    tolerance_band = bands[digit_count + 1]

    for index, band in enumerate(digit_bands, start=1):
        if band not in DIGIT_CODES:
            raise ResistorInputError(
                f"Band {index} (`{band}`) cannot be used as a digit band. {USAGE}"
            )

    if multiplier_band not in MULTIPLIERS:
        raise ResistorInputError(
            f"Band {digit_count + 1} (`{multiplier_band}`) cannot be used as a multiplier band. {USAGE}"
        )

    if tolerance_band not in TOLERANCES:
        raise ResistorInputError(
            f"Band {digit_count + 2} (`{tolerance_band}`) cannot be used as a tolerance band. {USAGE}"
        )

    significant_digits = "".join(str(DIGIT_CODES[band]) for band in digit_bands)
    resistance_ohms = Decimal(int(significant_digits)) * MULTIPLIERS[multiplier_band]

    return ResistorResult(
        bands=bands,
        resistance_ohms=resistance_ohms,
        tolerance_percent=TOLERANCES[tolerance_band],
    )


def _format_decimal(value: Decimal, places: int = 3) -> str:
    rendered = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return rendered or "0"


def format_resistance(ohms: Decimal) -> str:
    if abs(ohms) >= Decimal("1000000"):
        return f"{_format_decimal(ohms / Decimal('1000000'))} MΩ"
    if abs(ohms) >= Decimal("1000"):
        return f"{_format_decimal(ohms / Decimal('1000'))} kΩ"
    return f"{_format_decimal(ohms)} Ω"


def format_tolerance(percent: Decimal) -> str:
    return _format_decimal(percent)


def build_resistor_message(text: str) -> str:
    try:
        result = calculate_resistor(text)
    except ResistorInputError as exc:
        return f":warning: {exc}"

    bands = " ".join(result.bands)
    resistance = format_resistance(result.resistance_ohms)
    tolerance = format_tolerance(result.tolerance_percent)
    return (
        f"*Resistor:* `{bands}`\n"
        f"*Resistance:* `{resistance}`\n"
        f"*Tolerance:* `+/-{tolerance}%`"
    )


def register(app: App) -> None:
    @app.command("/dp-resistor")
    def handle_resistor(ack, command, respond, logger):
        ack()
        message = build_resistor_message(command.get("text", ""))
        try:
            respond(response_type="ephemeral", text=message)
        except Exception:
            logger.exception("Failed to send /dp-resistor response")
