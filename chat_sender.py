import requests

from config import API_URL


def send_group_msg(group_id: str, message: str):
    """
    发送消息到指定的群聊。
    """
    print(f"发送消息到 {group_id}:\n{message}\n{'-'*50}")

    data = {"group_id": group_id, "message": message}
    try:
        response = requests.post(f"{API_URL}/send_group_msg", json=data)
        response.raise_for_status()
        print(f"信息发送成功: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"信息发送失败: {e}")


def send_group_forward_msg(group_id: str, message: dict):
    """
    发送消息到指定的群聊。
    """
    print(f"发送消息到 {group_id}:\n{message}\n{'-'*50}")

    message["group_id"] = group_id
    try:
        response = requests.post(f"{API_URL}/send_group_forward_msg", json=message)
        response.raise_for_status()
        print(f"信息发送成功: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"信息发送失败: {e}")
