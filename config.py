import json
from typing import List, Optional, Tuple
from pydantic import BaseModel


class GroupConfig(BaseModel):
    group_id: str  # 群聊ID
    secret: str  # Webhook Secret
    organization: Optional[str] = None  # 组织名称
    repository: Optional[str] = None  # 仓库名称


def load_group_configs(
    config_file: str = "config.json",
) -> Tuple[List[GroupConfig], str]:
    """
    从配置文件中加载群聊绑定信息。
    """
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            return [GroupConfig(**group) for group in data.get("groups", [])], data.get(
                "api_url", ""
            )
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"无法加载配置文件: {e}")


# 加载配置
GROUP_CONFIGS, API_URL = load_group_configs()
