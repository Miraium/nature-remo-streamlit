import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def notify_slack(webhook_url, message, image_path=None, bot_token=None, channel=None):
    # 画像アップロード (bot_tokenとchannelが指定されている場合)
    if image_path and bot_token and channel:
        client = WebClient(token=bot_token)
        try:
            # デバッグ用: チャンネルIDをログ出力
            print(f"アップロード先チャンネルID: {channel}")

            # ファイルをアップロードしてチャンネルに共有
            response = client.files_upload_v2(
                file=image_path,
                title="Energy Usage Graph",
                channels=[channel],
                initial_comment=message
            )
            if not response["ok"]:
                print(f"Slack画像アップロードエラー: {response}")
            return  # 画像送信時はここで終了
        except SlackApiError as e:
            print(f"Slack APIエラー: {e.response['error']}")
        except Exception as e:
            print(f"画像アップロード中にエラーが発生しました: {e}")

    # 通常のメッセージ送信 (画像がない場合のみ)
    if webhook_url:
        try:
            response = requests.post(webhook_url, json={"text": message})
            if response.status_code != 200:
                print(f"Slack通知エラー: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Slack Webhook通知中にエラーが発生しました: {e}")
