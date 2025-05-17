import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

def notify_line_messaging_api(channel_access_token, user_id, message, image_path=None):
    """
    LINE Messaging APIを使用してメッセージと画像を送信する関数。
    """
    headers = {
        "Authorization": f"Bearer {channel_access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [
            {"type": "text", "text": message}
        ]
    }

    # 画像がある場合、画像メッセージを追加
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as file:
            files = {"file": file}
            upload_response = requests.post(
                "https://api-data.line.me/v2/bot/message/upload",
                headers={"Authorization": f"Bearer {channel_access_token}"},
                files=files
            )
            if upload_response.status_code == 200:
                image_url = upload_response.json().get("url")
                if image_url:
                    data["messages"].append({
                        "type": "image",
                        "originalContentUrl": image_url,
                        "previewImageUrl": image_url
                    })
            else:
                print(f"画像アップロードエラー: {upload_response.status_code} - {upload_response.text}")

    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        print("LINE通知の送信に成功しました")
    else:
        print(f"LINE通知の送信に失敗しました: {response.status_code} - {response.text}")

def create_usage_graph(data, threshold, image_path):
    # 既存のコードは変更なし
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
