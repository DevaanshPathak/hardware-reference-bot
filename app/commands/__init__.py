from slack_bolt import App

from app.commands import datasheet
from app.commands import pinout
from app.commands import resistor


def register_commands(app: App) -> None:
    """Register all Slack slash command handlers."""
    resistor.register(app)
    datasheet.register(app)
    pinout.register(app)
