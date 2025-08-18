#!/usr/bin/env python3
"""
TOS MCP Server 模块入口点
当使用 python -m tos_mcp_server 时会调用此文件
"""

def main():
    from .main import main as main_func
    main_func()

if __name__ == "__main__":
    main()