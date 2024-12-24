# main.py

import hmac
import hashlib
from fastapi import FastAPI, Header, HTTPException, Request
from typing import List
from config import GROUP_CONFIGS, GroupConfig
from chat_sender import send_message_to_group
import json
from datetime import datetime

app = FastAPI()


def verify_signature(secret: str, signature: str, body: bytes) -> bool:
    """
    验证GitHub Webhook的签名。
    """
    sha_name, signature = signature.split("=")
    if sha_name != "sha256":
        return False
    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)


def format_message(payload: dict) -> str:
    """
    根据payload构建要发送的纯文本消息内容。
    """
    repository = payload.get("repository", {})
    full_name = repository.get("full_name", "未知仓库")
    html_url = repository.get("html_url", "无链接")

    ref = payload.get("ref", "未知分支")
    branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref

    pusher = payload.get("pusher", {}).get("name", "未知推送者")

    compare = payload.get("compare", "无比较链接")

    commits = payload.get("commits", [])
    commit_count = len(commits)

    # 提取提交详情
    commit_details = []
    for commit in commits:
        commit_id = commit.get("id", "")[:7]
        message = commit.get("message", "").strip().replace("\n", " ")
        url = commit.get("url", "无链接")
        commit_details.append(
            f"  - 提交ID: {commit_id}\n    消息: {message}\n    链接: {url}"
        )
    commit_messages = "\n".join(commit_details) if commit_details else "  无提交详情"

    # 提取推送时间
    timestamp = payload.get("head_commit", {}).get("timestamp", "")
    try:
        push_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z").strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        )
    except (ValueError, TypeError):
        push_time = "未知时间"

    message = (
        f"【GitHub Push 事件通知】\n"
        f"仓库: {full_name}\n"
        f"仓库链接: {html_url}\n"
        f"分支: {branch}\n"
        f"推送者: {pusher}\n"
        f"推送时间: {push_time}\n"
        f"提交数: {commit_count}\n"
        f"提交详情:\n{commit_messages}\n"
        f"比较链接: {compare}"
    )

    return message


@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
):
    if not x_github_event or not x_hub_signature_256:
        raise HTTPException(status_code=400, detail="缺少必要的头信息")

    body = await request.body()

    # 解析payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")

    # 根据payload确定来源
    organization = (
        payload.get("organization", {}).get("login")
        if "organization" in payload
        else None
    )
    repository = (
        payload.get("repository", {}).get("full_name")
        if "repository" in payload
        else None
    )

    # 找到匹配的群聊配置
    matched_groups = []
    for config in GROUP_CONFIGS:
        if config.organization and config.organization == organization:
            matched_groups.append(config)
        if config.repository and config.repository == repository:
            matched_groups.append(config)

    if not matched_groups:
        return {"msg": "未找到匹配的群聊"}

    # 构建消息内容
    message = format_message(payload)

    # 为每个匹配的群聊验证签名并发送消息
    for group in matched_groups:
        if not verify_signature(group.secret, x_hub_signature_256, body):
            raise HTTPException(
                status_code=403, detail=f"群聊 {group.group_id} 的签名验证失败"
            )

        # 发送消息到群聊
        send_message_to_group(group.group_id, message)

    return {"msg": "消息已成功发送"}
