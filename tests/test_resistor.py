from decimal import Decimal

import pytest

from app.commands.resistor import (
    ResistorInputError,
    build_resistor_message,
    calculate_resistor,
    format_resistance,
)


def test_calculates_four_band_resistor() -> None:
    result = calculate_resistor("brown black red gold")

    assert result.resistance_ohms == Decimal("1000")
    assert result.tolerance_percent == Decimal("5")


def test_calculates_five_band_resistor() -> None:
    result = calculate_resistor("brown black black red brown")

    assert result.resistance_ohms == Decimal("10000")
    assert result.tolerance_percent == Decimal("1")


def test_formats_scaled_resistance() -> None:
    assert format_resistance(Decimal("1000")) == "1 kΩ"
    assert format_resistance(Decimal("4700000")) == "4.7 MΩ"
    assert format_resistance(Decimal("47")) == "47 Ω"


def test_rejects_bad_band_count() -> None:
    with pytest.raises(ResistorInputError, match="exactly 4 or 5"):
        calculate_resistor("brown black red")


def test_rejects_unknown_color_in_message() -> None:
    message = build_resistor_message("brown black pink gold")

    assert "Unknown color" in message
    assert "/dp-resistor brown black red gold" in message
