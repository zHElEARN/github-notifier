# GitHub Notifier

**GitHub Notifier** 是一个基于 Python 和 FastAPI 构建的聊天机器人，用于接收 GitHub 的 Webhook 推送事件，并将相关信息推送到指定的聊天群。

## 安装

1. 克隆项目仓库

   ```bash
   git clone https://github.com/zHElEARN/github-notifier.git
   cd github-notifier
   ```

2. 创建并激活虚拟环境（推荐）

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # 对于 Windows 用户使用 `venv\Scripts\activate`
   ```

3. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

## 配置

### 配置文件格式

项目使用 `config.json` 文件来管理群聊绑定和相关配置信息

`config.json` 示例：

```json
{
  "api_url": "http://localhost:3000",
  "groups": [
    {
      "group_id": "123456789",
      "secret": "secret_org_A",
      "organization": "OrganizationA"
    },
    {
      "group_id": "987654321",
      "secret": "secret_org_B",
      "organization": "OrganizationB"
    },
    {
      "group_id": "88888888",
      "secret": "secret_repo_C",
      "repository": "User/Repository"
    }
  ]
}
```

字段说明：

- `group_id`：群聊的唯一标识符。
- `secret`：用于验证 GitHub Webhook 请求的 Secret。
- `organization`（可选）：绑定的 GitHub 组织名称。如果配置了 `organization`，则此群聊将接收该组织下所有仓库的推送事件。
- `repository`（可选）：绑定的 GitHub 仓库全名（如 `username/repository`）。如果配置了 `repository`，则此群聊将仅接收该仓库的推送事件。
- `api_url`：用于发送消息到群聊的 API 端点。

注意事项：

- 每个群聊配置必须至少包含 `group_id`和`secret`。
- `organization` 和 `repository` 可选，且不可同时配置。如果同时配置，将优先匹配 `repository`。
- 确保 `secret` 的安全性，不要泄露给未经授权的人员。

## 运行

启动 FastAPI 服务器以监听 GitHub Webhook 请求。

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 配置 GitHub Webhook

在 GitHub 仓库或组织中配置 Webhook，以便在推送事件发生时通知您的服务器。

1. 进入 GitHub 仓库或组织设置

2. 导航到 `Settings` > `Webhooks`

3. 点击 `Add webhook`

4. 配置 Webhook：

   - Payload URL: `http://your-server-address:8000/webhook`
   - Content type: `application/json`
   - Secret: 配置文件中对应群聊的 `secret` 值（确保每个仓库或组织使用不同的 Secret）
   - Which events would you like to trigger this webhook?: 选择 `Just the push event.`

5. 保存 Webhook

**注意**：

- 如果绑定的是组织，请确保组织下的所有仓库都配置了相应的 Webhook 或使用 GitHub 的组织级 Webhook 功能。
- 确保服务器地址对 GitHub 可访问，且端口未被防火墙阻挡。

## 示例消息格式

以下是推送事件通知的示例消息格式。

```
发送消息到 群聊C:
【GitHub Push 事件通知】
仓库: zHElEARN/counter
仓库链接: https://github.com/zHElEARN/counter
分支: main
推送者: zHElEARN
推送时间: 2024-12-24 23:59:06 +0800
提交数: 1
提交详情:
  - 提交ID: e865eb1
    消息: 2
    链接: https://github.com/zHElEARN/counter/commit/e865eb1
比较链接: https://github.com/zHElEARN/counter/compare/2f9c5b86c77b...e865eb1
```

## 许可

本项目采用 [MIT 许可证](LICENSE)。
