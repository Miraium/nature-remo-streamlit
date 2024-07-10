import requests
import sqlite3
from datetime import datetime
import time
import yaml

# 設定ファイルを読み込む
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

ACCESS_TOKEN = config['access_token']
DB_FILE = config['database_file']

def get_energy_usage():
    url = 'https://api.nature.global/1/appliances'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
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

def save_energy_usage():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS energy_usage (time TEXT, value REAL)''')
    conn.commit()
    
    while True:
        energy_usage = get_energy_usage()
        if energy_usage is not None:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO energy_usage (time, value) VALUES (?, ?)", (current_time, energy_usage))
            conn.commit()
        time.sleep(10)
    
    conn.close()

if __name__ == "__main__":
    save_energy_usage()
