#!/bin/bash

# TOS MCP Server 启动脚本

# 检查环境变量
if [ -z "$TOS_ACCESS_KEY" ]; then
    echo "错误: 请设置 TOS_ACCESS_KEY 环境变量"
    exit 1
fi

if [ -z "$TOS_SECRET_KEY" ]; then
    echo "错误: 请设置 TOS_SECRET_KEY 环境变量"
    exit 1
fi

# 设置默认值
export TOS_REGION=${TOS_REGION:-"cn-beijing"}
export TOS_ENDPOINT=${TOS_ENDPOINT:-"tos-${TOS_REGION}.volces.com"}

echo "启动 TOS MCP Server..."
echo "Region: $TOS_REGION"
echo "Endpoint: $TOS_ENDPOINT"

# 启动服务器
python3 tos_mcp_server.py