import yaml
from line_notifier import notify_line_bot
from discord_notifier import notify_discord
from slack_notifier import notify_slack

def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

def test_line_notification(config):
    line_config = config["notifications"]["line"]
    message = "LINE通知テストメッセージ"
    image_path = None  # 必要に応じて画像パスを設定
    try:
        notify_line_bot(line_config["token"], message, image_path)
        print("LINE通知テスト成功")
    except Exception as e:
        print(f"LINE通知テスト失敗: {e}")

def test_discord_notification(config):
    discord_config = config["notifications"]["discord"]
    message = "Discord通知テストメッセージ"
    image_path = None  # 必要に応じて画像パスを設定
    try:
        notify_discord(discord_config["webhook_url"], message, image_path)
        print("Discord通知テスト成功")
    except Exception as e:
        print(f"Discord通知テスト失敗: {e}")

def test_slack_notification(config):
    slack_config = config["notifications"]["slack"]
    message = "Slack通知テストメッセージ"
    image_path = "energy_usage.png"
    try:
        notify_slack(
            slack_config["webhook_url"],
            message,
            image_path,
            slack_config["bot_token"],
            slack_config["channel"]
        )
        print("Slack通知テスト成功")
    except Exception as e:
        print(f"Slack通知テスト失敗: {e}")

if __name__ == "__main__":
    config = load_config()
    platforms = config["notifications"]["platforms"]

    if "line" in platforms and config["notifications"]["line"]["enabled"]:
        print("LINE通知テストを実行中...")
        # test_line_notification(config)

    if "discord" in platforms and config["notifications"]["discord"]["enabled"]:
        print("Discord通知テストを実行中...")
        # test_discord_notification(config)

    if "slack" in platforms and config["notifications"]["slack"]["enabled"]:
        print("Slack通知テストを実行中...")
        test_slack_notification(config)
