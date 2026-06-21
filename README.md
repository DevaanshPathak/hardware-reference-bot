# Hardware Reference Bot

Hardware Reference Bot is a small FastAPI Slack slash-command bot for Hack Club's Stardance YSWS program. It uses the official Slack Bolt Python SDK with the FastAPI adapter, so Slack request signature verification is handled by Bolt. It does not use Socket Mode.

Slack commands:

- `/dp-resistor <bands>` calculates 4-band and 5-band resistor values, for example `/dp-resistor brown black red gold`.
- `/dp-datasheet <part_number>` returns ready-made search links for Octopart, a manufacturer datasheet search, and AllDataSheet.
- `/dp-pinout <mcu>` returns a static curated pinout/peripheral cheatsheet. Seeded MCUs: `STM32G474`, `ESP32-C3`.

## Structure

```text
app/
  main.py
  config.py
  commands/
  data/
tests/
Dockerfile
docker-compose.yml
slack-app-manifest.yaml
.env.example
```

## Environment

Copy `.env.example` to `.env` and fill in real Slack values:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
PORT=8000
LOG_LEVEL=INFO
```

## Slack App Setup

1. Go to `api.slack.com/apps` and create a new app from `slack-app-manifest.yaml`.
2. Replace every `https://REPLACE_WITH_MY_DOMAIN/slack/events` Request URL with your deployed HTTPS URL after Coolify/Cloudflare Tunnel is ready.
3. Install the app to the Hack Club Slack workspace.
4. Copy the Bot User OAuth Token into `.env` as `SLACK_BOT_TOKEN`.
5. Copy the Signing Secret into `.env` as `SLACK_SIGNING_SECRET`.
6. Confirm the three slash commands are exactly `/dp-resistor`, `/dp-datasheet`, and `/dp-pinout`.

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/healthz
```

For Slack to reach local dev, expose `http://localhost:8000/slack/events` with a tunneling tool and update the Slack Request URLs to the public HTTPS tunnel URL.

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The app listens on `PORT`, defaulting to `8000`, and exposes `GET /healthz`.

## Coolify Deployment

1. Create a Coolify app from this repository and build it with the `Dockerfile`.
2. Set `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `PORT`, and `LOG_LEVEL` in Coolify.
3. Expose the container port matching `PORT` (`8000` by default).
4. Point the existing Cloudflare Tunnel domain at the Coolify service and port.
5. Update the Slack slash-command Request URLs to `https://YOUR_DOMAIN/slack/events`.
6. Use `https://YOUR_DOMAIN/healthz` as the health check URL.

## Notes

- Slash command handlers call `ack()` immediately, then send the actual message with Bolt's response-url-backed `respond()` helper.
- `/dp-datasheet` constructs search URLs only. It does not scrape websites or parse PDFs.
- `/dp-pinout` data is static JSON in `app/data/mcus.json`, so adding more MCUs is just a new entry plus aliases.
- MCU data was checked against the ST STM32G474 datasheet and Espressif ESP32-C3 datasheet/GPIO guide.

Sources:

- STM32G474 datasheet: https://www.st.com/resource/en/datasheet/stm32g474cb.pdf
- ESP32-C3 datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf
- ESP32-C3 GPIO guide: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/gpio.html
