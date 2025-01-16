# main.py

import hmac
import hashlib
from fastapi import FastAPI, Header, HTTPException, Request
from config import GROUP_CONFIGS
from chat_sender import send_group_forward_msg
import json

from formatter import format_to_json

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
    message = format_to_json(payload)

    # 为每个匹配的群聊验证签名并发送消息
    for group in matched_groups:
        if not verify_signature(group.secret, x_hub_signature_256, body):
            raise HTTPException(
                status_code=403, detail=f"群聊 {group.group_id} 的签名验证失败"
            )

        # 发送消息到群聊
        send_group_forward_msg(group.group_id, message)

    return {"msg": "消息已成功发送"}
