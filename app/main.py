import logging

from fastapi import FastAPI, Request
from slack_bolt import App as SlackApp
from slack_bolt.adapter.fastapi import SlackRequestHandler

from app.commands import register_commands
from app.config import settings


logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

if not settings.slack_bot_token or not settings.slack_signing_secret:
    logger.warning(
        "SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET must be set before Slack can call the app."
    )

bolt_app = SlackApp(
    token=settings.slack_bot_token,
    signing_secret=settings.slack_signing_secret,
    process_before_response=True,
)
register_commands(bolt_app)

app = FastAPI(title="Hardware Reference Bot")
slack_handler = SlackRequestHandler(bolt_app)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/slack/events")
async def slack_events(request: Request):
    return await slack_handler.handle(request)
