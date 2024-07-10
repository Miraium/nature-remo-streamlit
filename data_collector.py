import requests
import sqlite3
from datetime import datetime
import time
import yaml
import sys

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
                        return property['val']
    else:
        print(f"Error: {response.status_code}")
        return None

def save_energy_usage(db_file, access_token, interval):
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

    save_energy_usage(db_file, access_token, interval)

if __name__ == "__main__":
    main()
