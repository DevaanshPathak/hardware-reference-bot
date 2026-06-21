from urllib.parse import quote_plus

from slack_bolt import App


USAGE = "Usage: `/dp-datasheet STM32G474RET6`"


def normalize_part_number(text: str) -> str:
    return " ".join(text.split())


def build_datasheet_links(part_number: str) -> list[tuple[str, str]]:
    query = quote_plus(part_number)
    manufacturer_query = quote_plus(f"{part_number} manufacturer datasheet")

    return [
        ("Octopart search", f"https://octopart.com/search?q={query}"),
        (
            "Manufacturer datasheet search",
            f"https://www.google.com/search?q={manufacturer_query}",
        ),
        (
            "AllDataSheet search",
            f"https://www.alldatasheet.com/view.jsp?Searchword={query}",
        ),
    ]


def build_datasheet_message(text: str) -> str:
    part_number = normalize_part_number(text)
    if not part_number:
        return f":warning: Please include a part number. {USAGE}"

    links = "\n".join(
        f"- <{url}|{label}>" for label, url in build_datasheet_links(part_number)
    )
    return f"*Datasheet links for:* `{part_number}`\n{links}"


def register(app: App) -> None:
    @app.command("/dp-datasheet")
    def handle_datasheet(ack, command, respond, logger):
        ack()
        message = build_datasheet_message(command.get("text", ""))
        try:
            respond(response_type="ephemeral", text=message)
        except Exception:
            logger.exception("Failed to send /dp-datasheet response")
