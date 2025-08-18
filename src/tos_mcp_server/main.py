#!/usr/bin/env python3
"""
TOS MCP Server 主入口文件
"""

import asyncio
import logging
import argparse
from .server import run_server

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="TOS MCP Server")
    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "sse"],
        default="stdio",
        help="传输协议 (stdio 或 sse)"
    )
    
    args = parser.parse_args()
    
    try:
        logger.info(f"启动 TOS MCP Server，传输协议: {args.transport}")
        asyncio.run(run_server(args.transport))
    except Exception as e:
        logger.error(f"启动 TOS MCP Server 失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()