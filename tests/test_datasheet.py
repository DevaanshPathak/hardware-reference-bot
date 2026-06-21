from app.commands.datasheet import build_datasheet_links, build_datasheet_message


def test_builds_datasheet_links() -> None:
    links = build_datasheet_links("STM32G474RET6")

    assert links[0] == (
        "Octopart search",
        "https://octopart.com/search?q=STM32G474RET6",
    )
    assert links[1][0] == "Manufacturer datasheet search"
    assert "STM32G474RET6+manufacturer+datasheet" in links[1][1]
    assert links[2] == (
        "AllDataSheet search",
        "https://www.alldatasheet.com/view.jsp?Searchword=STM32G474RET6",
    )


def test_datasheet_message_has_clickable_links() -> None:
    message = build_datasheet_message("  ESP32-C3  ")

    assert "*Datasheet links for:* `ESP32-C3`" in message
    assert "<https://octopart.com/search?q=ESP32-C3|Octopart search>" in message
    assert "AllDataSheet search" in message


def test_datasheet_message_rejects_empty_input() -> None:
    message = build_datasheet_message("")

    assert "Please include a part number" in message
    assert "/dp-datasheet STM32G474RET6" in message
