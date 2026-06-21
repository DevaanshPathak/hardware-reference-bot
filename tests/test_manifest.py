import yaml


def test_manifest_commands_do_not_include_usage_hints() -> None:
    with open("slack-app-manifest.yaml", encoding="utf-8") as file:
        manifest = yaml.safe_load(file)

    commands = manifest["features"]["slash_commands"]

    assert [command["url"] for command in commands] == [
        "https://devaansh.hackclub.app/slack/events",
        "https://devaansh.hackclub.app/slack/events",
        "https://devaansh.hackclub.app/slack/events",
    ]
    assert all("usage_hint" not in command for command in commands)
