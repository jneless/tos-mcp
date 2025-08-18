"""
TOS MCP Server 实现
"""

import json
import base64
import logging
from typing import Any, Dict, List

import tos
from mcp.server import Server
from mcp.types import Tool, TextContent

from .config import tos_config
from .handlers import (
    create_bucket, list_buckets, get_bucket_meta, delete_bucket,
    put_object, get_object, list_objects, delete_object,
    presigned_url, image_process, image_info,
    video_snapshot, video_info
)

# 配置日志
logger = logging.getLogger(__name__)

# 初始化 MCP Server
server = Server("tos-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的工具"""
    return [
        # 桶管理工具
        Tool(
            name="tos_create_bucket",
            description="创建 TOS 存储桶",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "acl": {
                        "type": "string",
                        "description": "访问控制权限",
                        "enum": ["private", "public-read", "public-read-write"],
                        "default": "private"
                    }
                },
                "required": ["bucket_name"]
            }
        ),
        Tool(
            name="tos_list_buckets",
            description="列举 TOS 存储桶",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="tos_get_bucket_meta",
            description="获取存储桶元数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    }
                },
                "required": ["bucket_name"]
            }
        ),
        Tool(
            name="tos_delete_bucket",
            description="删除 TOS 存储桶",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    }
                },
                "required": ["bucket_name"]
            }
        ),
        
        # 对象管理工具
        Tool(
            name="tos_put_object",
            description="上传对象到 TOS",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "对象键名"
                    },
                    "content": {
                        "type": "string",
                        "description": "文件内容（base64编码）或文本内容"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "内容类型",
                        "default": "application/octet-stream"
                    },
                    "is_base64": {
                        "type": "boolean",
                        "description": "内容是否为base64编码",
                        "default": False
                    }
                },
                "required": ["bucket_name", "object_key", "content"]
            }
        ),
        Tool(
            name="tos_get_object",
            description="从 TOS 下载对象",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "对象键名"
                    },
                    "return_as_base64": {
                        "type": "boolean",
                        "description": "是否以base64格式返回内容",
                        "default": False
                    }
                },
                "required": ["bucket_name", "object_key"]
            }
        ),
        Tool(
            name="tos_list_objects",
            description="列举 TOS 对象",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "prefix": {
                        "type": "string",
                        "description": "对象键前缀",
                        "default": ""
                    },
                    "delimiter": {
                        "type": "string",
                        "description": "分隔符",
                        "default": ""
                    },
                    "max_keys": {
                        "type": "integer",
                        "description": "最大返回对象数量",
                        "default": 1000
                    }
                },
                "required": ["bucket_name"]
            }
        ),
        Tool(
            name="tos_delete_object",
            description="删除 TOS 对象",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "对象键名"
                    }
                },
                "required": ["bucket_name", "object_key"]
            }
        ),
        
        # 预签名 URL 工具
        Tool(
            name="tos_presigned_url",
            description="生成预签名 URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "对象键名"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP方法",
                        "enum": ["GET", "PUT", "POST", "DELETE"],
                        "default": "GET"
                    },
                    "expires": {
                        "type": "integer",
                        "description": "过期时间（秒）",
                        "default": 3600
                    }
                },
                "required": ["bucket_name", "object_key"]
            }
        ),
        
        Tool(
            name="tos_image_info",
            description="获取图片信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "图片对象键名"
                    }
                },
                "required": ["bucket_name", "object_key"]
            }
        ),
        # 图片处理工具
        Tool(
            name="tos_image_process",
            description="图片处理（组合操作，支持多种处理参数）",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "图片对象键名"
                    },
                    "process": {
                        "type": "string",
                        "description": "图片处理参数。参数格式通常为 'image/操作,参数'，如: 'image/resize,h_100' 或 'image/format,jpg'。常用操作包括：resize(缩放),format(格式转换),quality(质量),crop(裁剪),rotate(旋转)等。"
                    },
                    "save_bucket": {
                        "type": "string",
                        "description": "保存的存储桶名称"
                    },
                    "save_key": {
                        "type": "string",
                        "description": "保存的对象键名"
                    }
                },
                "required": ["bucket_name", "object_key", "process", "save_bucket", "save_key"]
            }
        ),
        
        # 视频处理工具
        Tool(
            name="tos_video_snapshot",
            description="视频截帧（支持持久化）",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "视频对象键名"
                    },
                    "time": {
                        "type": "number",
                        "description": "截帧时间点（毫秒），如300表示第300毫秒",
                        "default": 300
                    },
                    "format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["jpg", "png"],
                        "default": "jpg"
                    },
                    "save_bucket": {
                        "type": "string",
                        "description": "保存截帧图片的存储桶名称"
                    },
                    "save_key": {
                        "type": "string",
                        "description": "保存截帧图片的对象键名"
                    }
                },
                "required": ["bucket_name", "object_key", "save_bucket", "save_key"]
            }
        ),
        Tool(
            name="tos_video_info",
            description="获取视频信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "存储桶名称"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "视频对象键名"
                    }
                },
                "required": ["bucket_name", "object_key"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "tos_create_bucket":
            return await create_bucket(arguments)
        elif name == "tos_list_buckets":
            return await list_buckets(arguments)
        elif name == "tos_get_bucket_meta":
            return await get_bucket_meta(arguments)
        elif name == "tos_delete_bucket":
            return await delete_bucket(arguments)
        elif name == "tos_put_object":
            return await put_object(arguments)
        elif name == "tos_get_object":
            return await get_object(arguments)
        elif name == "tos_list_objects":
            return await list_objects(arguments)
        elif name == "tos_delete_object":
            return await delete_object(arguments)
        elif name == "tos_presigned_url":
            return await presigned_url(arguments)
        elif name == "tos_image_process":
            return await image_process(arguments)
        elif name == "tos_image_info":
            return await image_info(arguments)
        elif name == "tos_video_snapshot":
            return await video_snapshot(arguments)
        elif name == "tos_video_info":
            return await video_info(arguments)
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    except Exception as e:
        logger.error(f"工具调用错误 {name}: {str(e)}")
        return [TextContent(type="text", text=f"错误: {str(e)}")]

async def run_server(transport: str = "stdio"):
    """运行MCP服务器"""
    if transport == "stdio":
        try:
            from mcp.server.stdio import stdio_server
        except ImportError:
            from mcp.server import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    else:
        raise NotImplementedError(f"Transport {transport} not implemented")