import requests

from config import API_URL


def send_message_to_group(group_id: str, message: str):
    """
    发送消息到指定的群聊。
    """
    print(f"发送消息到 {group_id}:\n{message}\n{'-'*50}")

    data = {"group_id": group_id, "message": message}
    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        print(f"信息发送成功: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"信息发送失败: {e}")
