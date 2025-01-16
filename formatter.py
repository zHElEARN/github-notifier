from datetime import datetime


def format_to_text(payload: dict) -> str:
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
            f"  - 提交ID: {commit_id}\n    消息: {message}"
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


def format_to_json(payload: dict) -> dict:
    """
    根据 GitHub Webhook Payload 格式化推送事件为复杂 JSON 消息。
    """
    repository = payload.get("repository", {})
    repo_name = repository.get("full_name", "未知仓库")
    repo_url = repository.get("html_url", "无链接")

    ref = payload.get("ref", "未知分支")
    branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref

    pusher = payload.get("pusher", {})
    pusher_name = pusher.get("name", "未知推送者")
    pusher_email = pusher.get("email", "未知邮箱")

    compare_url = payload.get("compare", "无比较链接")

    commits = payload.get("commits", [])
    commit_count = len(commits)

    # 获取推送时间
    timestamp = payload.get("head_commit", {}).get("timestamp", "")
    try:
        push_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z").strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        )
    except (ValueError, TypeError):
        push_time = "未知时间"

    # 构建消息内容
    messages = [
        {
            "type": "node",
            "data": {
                "user_id": "",
                "nickname": "GitHub Bot",
                "content": [
                    {
                        "type": "text",
                        "data": {
                            "text": (
                                f"仓库: {repo_name}\n"
                                f"分支: {branch}\n"
                                f"推送者: {pusher_name} ({pusher_email})\n"
                                f"推送时间: {push_time}\n"
                                f"提交数: {commit_count}\n"
                            )
                        },
                    }
                ],
            },
        }
    ]

    news = []
    for commit in commits:
        commit_id = commit.get("id", "")[:7]
        message = commit.get("message", "无提交信息").strip()
        auther = commit.get("author", {})
        auther_name = auther.get("name", "未知作者")
        auther_email = auther.get("email", "未知邮箱")
        url = commit.get("url", "无链接")
        # 添加详细信息消息
        messages.append(
            {
                "type": "node",
                "data": {
                    "user_id": "",
                    "nickname": "GitHub Bot",
                    "content": [
                        {
                            "type": "text",
                            "data": {
                                "text": f"提交ID: {commit_id}\n消息: {message}\n提交者: {auther_name} ({auther_email})\n链接: {url}"
                            },
                        }
                    ],
                },
            }
        )
        # 添加简要新闻
        news.append({"text": f"{commit_id}: {message}"})

    messages.append(
        {
            "type": "node",
            "data": {
                "user_id": "",
                "nickname": "GitHub Bot",
                "content": [
                    {
                        "type": "text",
                        "data": {
                            "text": f"仓库链接: {repo_url}\n比较链接: {compare_url}"
                        },
                    }
                ],
            },
        }
    )

    return {
        "prompt": "GitHub Push 事件通知",
        "summary": f"仓库: {repo_name}",
        "source": "GitHub Push 事件通知",
        "messages": messages,
        "news": news,
    }
