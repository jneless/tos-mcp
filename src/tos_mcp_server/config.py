"""配置管理模块"""

import os
import sys
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class TosConfig:
    """TOS MCP Server 配置类"""
    access_key: str
    secret_key: str
    region: str
    endpoint: str
    
    @classmethod
    def from_env(cls) -> "TosConfig":
        """从环境变量加载配置"""
        access_key = os.getenv("TOS_ACCESS_KEY")
        secret_key = os.getenv("TOS_SECRET_KEY")
        region = os.getenv("TOS_REGION", "cn-beijing")
        endpoint = os.getenv("TOS_ENDPOINT", f"https://tos-{region}.volces.com")
        
        if not access_key or not secret_key:
            logger.error("TOS_ACCESS_KEY 和 TOS_SECRET_KEY 环境变量必须设置")
            sys.exit(1)
            
        return cls(
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            endpoint=endpoint
        )

# 全局配置实例
tos_config = TosConfig.from_env()