import requests
from requests.exceptions import RequestException
import sqlite3
from datetime import datetime, timedelta
import time
import yaml
import sys
from line_notifier import notify_line_bot, create_usage_graph
from discord_notifier import notify_discord
from slack_notifier import notify_slack
import pandas as pd

def get_energy_usage(access_token):
    try:
        url = 'https://api.nature.global/1/appliances'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        appliances = response.json()
        for appliance in appliances:
            if 'smart_meter' in appliance and 'echonetlite_properties' in appliance['smart_meter']:
                for property in appliance['smart_meter']['echonetlite_properties']:
                    if property['name'] == 'measured_instantaneous':
                        print(property)
                        return int(property['val'])
    except RequestException as e:
        print(f"接続エラー: {e}")
        return None
    return None

def send_notifications(config, message, image_path=None):
    platforms = config["notifications"]["platforms"]

    if "line" in platforms and config["notifications"]["line"]["enabled"]:
        line_config = config["notifications"]["line"]
        notify_line_bot(line_config["token"], message, image_path)

    if "slack" in platforms and config["notifications"]["slack"]["enabled"]:
        slack_config = config["notifications"]["slack"]
        notify_slack(
            slack_config["webhook_url"],
            message,
            image_path,
            slack_config["bot_token"],
            slack_config["channel"]
        )

    if "discord" in platforms and config["notifications"]["discord"]["enabled"]:
        discord_config = config["notifications"]["discord"]
        notify_discord(discord_config["webhook_url"], message, image_path)

def save_energy_usage(db_file, access_token, interval, threshold, config):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS energy_usage (time TEXT, value REAL)''')
    conn.commit()

    last_notification_time = datetime.min
    last_notification_value = None

    max_retries = 10
    retry_delay = 30

    notify_enabled = config.get('notifications', {}).get('enabled', True)
    notify_message = config.get('notifications', {}).get('message', 'Energy usage exceeded the threshold')
    notify_message_below_threshold = config.get('notifications', {}).get('message_below_threshold', 'Energy usage is below the threshold')
    notify_interval = config.get('notify_interval', 180)

    try:
        while True:
            for attempt in range(max_retries):
                energy_usage = get_energy_usage(access_token)
                if energy_usage is not None:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("INSERT INTO energy_usage (time, value) VALUES (?, ?)", (current_time, energy_usage))
                    conn.commit()

                    current_time_dt = datetime.now()

                    if energy_usage > threshold and notify_enabled and last_notification_value is None and current_time_dt - last_notification_time >= timedelta(seconds=notify_interval):
                        print("通知送信中...")
                        data = pd.read_sql_query("SELECT * FROM energy_usage ORDER BY time DESC LIMIT 100", conn)
                        image_path = 'energy_usage.png'
                        create_usage_graph(data, threshold, image_path)
                        send_notifications(config, notify_message, image_path)
                        last_notification_time = current_time_dt
                        last_notification_value = energy_usage

                    if energy_usage < threshold and notify_enabled and last_notification_value is not None:
                        print("通知送信中 (閾値以下)...")
                        data = pd.read_sql_query("SELECT * FROM energy_usage ORDER BY time DESC LIMIT 100", conn)
                        image_path = 'energy_usage.png'
                        create_usage_graph(data, threshold, image_path)
                        send_notifications(config, notify_message_below_threshold, image_path)
                        last_notification_time = current_time_dt
                        last_notification_value = None

                    break
                else:
                    if attempt < max_retries - 1:
                        print(f"データ取得に失敗しました。{retry_delay}秒後に再試行します（試行 {attempt + 1}/{max_retries}）")
                        time.sleep(retry_delay)
                    else:
                        print("最大再試行回数に達しました。次の間隔まで待機します。")

            time.sleep(interval)
    except KeyboardInterrupt:
        print("停止中...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        conn.close()
        sys.exit(0)

def main():
    # 設定ファイルを読み込む
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    access_token = config['access_token']
    db_file = config['database_file']
    interval = config.get('request_interval', 15)
    threshold = config.get('threshold', 3000)

    save_energy_usage(
        db_file, access_token, interval, threshold, config
    )

if __name__ == "__main__":
    main()