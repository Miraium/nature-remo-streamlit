import requests
import sqlite3
from datetime import datetime
import time
import yaml
import sys
from line_notifier import notify_line, create_usage_graph
import pandas as pd

def get_energy_usage(access_token):
    url = 'https://api.nature.global/1/appliances'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        appliances = response.json()
        for appliance in appliances:
            if 'smart_meter' in appliance and 'echonetlite_properties' in appliance['smart_meter']:
                for property in appliance['smart_meter']['echonetlite_properties']:
                    if property['name'] == 'measured_instantaneous':
                        print(property)
                        return int(property['val'])
    else:
        print(f"Error: {response.status_code}")
        return None

def save_energy_usage(db_file, access_token, interval, threshold, line_token, notify_enabled, notify_message):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS energy_usage (time TEXT, value REAL)''')
    conn.commit()
    
    try:
        while True:
            energy_usage = get_energy_usage(access_token)
            if energy_usage is not None:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO energy_usage (time, value) VALUES (?, ?)", (current_time, energy_usage))
                conn.commit()
                
                # しきい値を超えた場合の処理
                if energy_usage > threshold and notify_enabled:
                    print("Line Notification")
                    # グラフを生成してLINEに送信
                    data = pd.read_sql_query("SELECT * FROM energy_usage ORDER BY time DESC LIMIT 100", conn)
                    image_path = 'energy_usage.png'
                    create_usage_graph(data, threshold, image_path)
                    notify_line(line_token, notify_message, 'energy_usage.png')
                    
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopping...")
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
    threshold = config.get('threshold', 3000)  # デフォルトは5000Wh
    line_token = config['line_token']
    notify_enabled = config.get('notify_enabled', True)
    notify_message = config.get('notify_message', 'Energy usage exceeded the threshold')

    save_energy_usage(db_file, access_token, interval, threshold, line_token, notify_enabled, notify_message)

if __name__ == "__main__":
    main()
