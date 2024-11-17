from datetime import datetime
import hashlib
import hmac
import os
from flask import Flask, jsonify, request
import requests
import yaml


app: Flask = Flask(__name__)


config: dict = {}
if os.path.exists("config.yaml"):
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)


GITHUB_WEBHOOK_SECRET = config.get("GITHUB_WEBHOOK_SECRET")
GROUP_MSG_API = config.get("GROUP_MSG_API")
GROUP_ID = config.get("GROUP_ID")

def verify_signure(payload, signature):
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    excepted_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(excepted_signature, signature)

def send_group_msg(group_id, message):
    data = {
        "group_id": group_id,
        "message": message
    }
    try:
        response = requests.post(GROUP_MSG_API, json=data)
        response.raise_for_status()
        print(f"信息发送成功: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"信息发送失败: {e}")

@app.route("/webhook", methods=["POST"])
def github_webhook():
    signature = request.headers.get("X-Hub-Signature-256")

    if signature is None:
        return jsonify({"status": "missing signature"}), 403
    
    payload = request.data

    if not verify_signure(payload, signature):
        return jsonify({"status": "invalid signature"}), 403
    
    if request.is_json:
        payload_json = request.get_json()

        if "commits" in payload_json:
            commits = payload_json["commits"]
            repository = payload_json["repository"]["full_name"]
            message_lines = [f"有新的Push! 仓库: {repository}\n"]

            for commit in commits:
                author = commit["author"]["name"]
                commmit_message = commit["message"]
                url = commit["url"]
                timestamp = datetime.fromisoformat(commit["timestamp"].rstrip("Z")).strftime("%Y-%m-%d %H:%M:%S")
                message_lines.extend([
                    f"用户: {author}",
                    f"时间: {timestamp}",
                    f"信息: {commmit_message}",
                    f"链接: {url}\n",
                ])

            message = "\n".join(message_lines)
            send_group_msg(GROUP_ID, message)

            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "no push event detected"}), 400
    else:
        return jsonify({"status": "invalid request"}), 400
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
