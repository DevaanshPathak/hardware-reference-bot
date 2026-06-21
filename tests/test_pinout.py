from app.commands.pinout import available_mcus, build_pinout_message, find_mcu


def test_finds_mcu_by_alias() -> None:
    mcu = find_mcu("STM32G474RET6")

    assert mcu is not None
    assert mcu["display_name"] == "STM32G474"


def test_pinout_message_contains_key_sections() -> None:
    message = build_pinout_message("esp32-c3")

    assert "*Pinout: ESP32-C3*" in message
    assert "*Power / Ground*" in message
    assert "*Key Peripherals*" in message
    assert "UART0 GPIO21 TX / GPIO20 RX" in message
    assert "TWAI controller" in message


def test_unknown_mcu_lists_available_entries() -> None:
    message = build_pinout_message("rp2040")

    assert "I don't have a pinout" in message
    assert "`ESP32-C3`" in message
    assert "`STM32G474`" in message


def test_available_mcus_are_display_names() -> None:
    assert available_mcus() == ["ESP32-C3", "STM32G474"]
