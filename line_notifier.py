import requests
import pandas as pd
import matplotlib.pyplot as plt

def notify_line(token, message, image_path=None):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'message': message
    }
    files = {}
    if image_path:
        files = {
            'imageFile': open(image_path, 'rb')
        }
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data, files=files)
    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def create_usage_graph(data, threshold, image_path):
    data['time'] = pd.to_datetime(data['time'])
    plt.figure(figsize=(10, 5))
    plt.plot(data['time'], data['value'], label='Energy Usage (Wh)')
    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    plt.xlabel('Time')
    plt.ylabel('Energy Usage (Wh)')
    plt.title('Real-time Energy Usage Monitoring')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()
