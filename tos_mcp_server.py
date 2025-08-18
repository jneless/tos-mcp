#!/usr/bin/env python3
"""
TOS (火山引擎对象存储) MCP Server
提供 TOS 对象存储服务的 MCP 工具集成
"""

import os
import sys
import json
import base64
from typing import Any, Dict, List
import asyncio
import logging

import tos
from mcp.server import Server
from mcp.types import Tool, TextContent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 MCP Server
server = Server("tos-mcp")

# TOS 客户端配置
TOS_REGION = os.getenv("TOS_REGION", "cn-beijing")
TOS_ENDPOINT = os.getenv("TOS_ENDPOINT", f"https://tos-{TOS_REGION}.volces.com")
TOS_ACCESS_KEY = os.getenv("TOS_ACCESS_KEY")
TOS_SECRET_KEY = os.getenv("TOS_SECRET_KEY")

if not TOS_ACCESS_KEY or not TOS_SECRET_KEY:
    logger.error("TOS_ACCESS_KEY 和 TOS_SECRET_KEY 环境变量必须设置")
    sys.exit(1)

# 初始化 TOS 客户端
tos_client = tos.TosClientV2(
    ak=TOS_ACCESS_KEY,
    sk=TOS_SECRET_KEY,
    endpoint=TOS_ENDPOINT,
    region=TOS_REGION
)

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

# 桶管理功能实现
async def create_bucket(args: Dict[str, Any]) -> List[TextContent]:
    """创建存储桶"""
    bucket_name = args["bucket_name"]
    acl = args.get("acl", "private")
    
    try:
        tos_client.create_bucket(bucket_name, tos.ACLType.ACL_Private if acl == "private" 
                                       else tos.ACLType.ACL_Public_Read if acl == "public-read"
                                       else tos.ACLType.ACL_Public_Read_Write)
        return [TextContent(type="text", text=f"成功创建存储桶: {bucket_name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"创建存储桶失败: {str(e)}")]

async def list_buckets(_args: Dict[str, Any]) -> List[TextContent]:
    """列举存储桶"""
    try:
        resp = tos_client.list_buckets()
        buckets = []
        for bucket in resp.buckets:
            buckets.append({
                "name": bucket.name,
                "creation_date": str(bucket.creation_date) if bucket.creation_date else None,
                "location": bucket.location
            })
        return [TextContent(type="text", text=json.dumps(buckets, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"列举存储桶失败: {str(e)}")]

async def get_bucket_meta(args: Dict[str, Any]) -> List[TextContent]:
    """获取存储桶元数据"""
    bucket_name = args["bucket_name"]
    
    try:
        resp = tos_client.head_bucket(bucket_name)
        meta = {
            "bucket_name": bucket_name,
            "region": resp.region,
            "storage_class": str(resp.storage_class) if resp.storage_class else None
        }
        return [TextContent(type="text", text=json.dumps(meta, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"获取存储桶元数据失败: {str(e)}")]

async def delete_bucket(args: Dict[str, Any]) -> List[TextContent]:
    """删除存储桶"""
    bucket_name = args["bucket_name"]
    
    try:
        tos_client.delete_bucket(bucket_name)
        return [TextContent(type="text", text=f"成功删除存储桶: {bucket_name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"删除存储桶失败: {str(e)}")]

# 对象管理功能实现
async def put_object(args: Dict[str, Any]) -> List[TextContent]:
    """上传对象"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    content = args["content"]
    content_type = args.get("content_type", "application/octet-stream")
    is_base64 = args.get("is_base64", False)
    
    try:
        if is_base64:
            content_bytes = base64.b64decode(content)
        else:
            content_bytes = content.encode('utf-8')
            
        resp = tos_client.put_object(bucket_name, object_key, 
                                   content=content_bytes, 
                                   content_type=content_type,
                                   content_length=len(content_bytes))
        return [TextContent(type="text", text=f"成功上传对象: {object_key} (ETag: {resp.etag})")]
    except Exception as e:
        return [TextContent(type="text", text=f"上传对象失败: {str(e)}")]

async def get_object(args: Dict[str, Any]) -> List[TextContent]:
    """下载对象"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    return_as_base64 = args.get("return_as_base64", False)
    
    try:
        resp = tos_client.get_object(bucket_name, object_key)
        content = resp.read()
        
        if return_as_base64:
            content_str = base64.b64encode(content).decode('utf-8')
            result = {
                "content": content_str,
                "content_type": resp.content_type,
                "content_length": resp.content_length,
                "encoding": "base64"
            }
        else:
            try:
                content_str = content.decode('utf-8')
                result = {
                    "content": content_str,
                    "content_type": resp.content_type,
                    "content_length": resp.content_length,
                    "encoding": "utf-8"
                }
            except UnicodeDecodeError:
                content_str = base64.b64encode(content).decode('utf-8')
                result = {
                    "content": content_str,
                    "content_type": resp.content_type,
                    "content_length": resp.content_length,
                    "encoding": "base64"
                }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"下载对象失败: {str(e)}")]

async def list_objects(args: Dict[str, Any]) -> List[TextContent]:
    """列举对象"""
    bucket_name = args["bucket_name"]
    prefix = args.get("prefix", "")
    delimiter = args.get("delimiter", "")
    max_keys = args.get("max_keys", 1000)
    
    try:
        resp = tos_client.list_objects_type2(bucket_name, prefix=prefix, delimiter=delimiter, max_keys=max_keys)
        
        result = {
            "objects": [],
            "common_prefixes": [],
            "is_truncated": resp.is_truncated,
            "next_continuation_token": resp.next_continuation_token
        }
        
        for obj in resp.contents:
            result["objects"].append({
                "key": obj.key,
                "last_modified": str(obj.last_modified) if obj.last_modified else None,
                "size": obj.size,
                "etag": obj.etag,
                "storage_class": str(obj.storage_class) if obj.storage_class else None
            })
            
        for prefix in resp.common_prefixes:
            result["common_prefixes"].append(prefix.prefix)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"列举对象失败: {str(e)}")]

async def delete_object(args: Dict[str, Any]) -> List[TextContent]:
    """删除对象"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    
    try:
        tos_client.delete_object(bucket_name, object_key)
        return [TextContent(type="text", text=f"成功删除对象: {object_key}")]
    except Exception as e:
        return [TextContent(type="text", text=f"删除对象失败: {str(e)}")]

# 预签名 URL 功能实现
async def presigned_url(args: Dict[str, Any]) -> List[TextContent]:
    """生成预签名 URL"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    method = args.get("method", "GET")
    expires = args.get("expires", 3600)
    
    try:
        if method == "GET":
            url = tos_client.pre_signed_url(tos.HttpMethodType.Http_Method_Get, bucket_name, object_key, expires)
        elif method == "PUT":
            url = tos_client.pre_signed_url(tos.HttpMethodType.Http_Method_Put, bucket_name, object_key, expires)
        elif method == "POST":
            url = tos_client.pre_signed_url(tos.HttpMethodType.Http_Method_Post, bucket_name, object_key, expires)
        elif method == "DELETE":
            url = tos_client.pre_signed_url(tos.HttpMethodType.Http_Method_Delete, bucket_name, object_key, expires)
        else:
            return [TextContent(type="text", text=f"不支持的HTTP方法: {method}")]
        
        result = {
            "url": url.signed_url,
            "method": method,
            "expires_in": expires,
            "bucket": bucket_name,
            "key": object_key
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"生成预签名URL失败: {str(e)}")]

# 图片处理功能实现
async def image_process(args: Dict[str, Any]) -> List[TextContent]:
    """图片处理（支持持久化）"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    process = args["process"]
    save_bucket = args["save_bucket"]
    save_key = args["save_key"]
    
    try:
        # 使用官方SDK写法，通过save_bucket和save_object参数执行图片处理和持久化
        resp = tos_client.get_object(
            bucket=bucket_name,
            key=object_key,
            process=process,
            save_bucket=base64.b64encode(save_bucket.encode("utf-8")).decode("utf-8"),
            save_object=base64.b64encode(save_key.encode("utf-8")).decode("utf-8")
        )
        
        # 读取处理结果以确保处理完成
        processed_data = resp.read()
        
        # 等待一下确保回写完成
        import time
        time.sleep(1.0)
        
        # 生成处理后对象的预签名 URL
        download_url = tos_client.pre_signed_url(tos.HttpMethodType.Http_Method_Get, save_bucket, save_key, 3600)
        
        result = {
            "presigned_url": download_url.signed_url,
            "source_bucket": bucket_name,
            "source_key": object_key,
            "save_bucket": save_bucket,
            "save_key": save_key,
            "process": process,
            "processed_size": len(processed_data),
            "expires_in": 3600,
            "status": "processed"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"图片处理失败: {str(e)}")]

async def image_info(args: Dict[str, Any]) -> List[TextContent]:
    """获取图片信息"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    
    try:
        # 使用 get_object 方法通过 style 参数获取图片信息
        # 设置处理参数为 image/info
        resp = tos_client.get_object(bucket_name, object_key, process="image/info")
        image_info_data = resp.read().decode('utf-8')
        
        # 尝试解析JSON响应
        try:
            image_info_json = json.loads(image_info_data)
            result = {
                "bucket": bucket_name,
                "key": object_key,
                "image_info": image_info_json,
                "status": "success"
            }
        except json.JSONDecodeError:
            # 如果不是JSON格式，直接返回原始数据
            result = {
                "bucket": bucket_name,
                "key": object_key,
                "image_info": image_info_data,
                "status": "success",
                "note": "返回原始格式数据"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"获取图片信息失败: {str(e)}")]


# 视频处理功能实现
async def video_snapshot(args: Dict[str, Any]) -> List[TextContent]:
    """视频截帧（支持持久化）"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    time = args.get("time", 300)
    format = args.get("format", "jpg")
    save_bucket = args["save_bucket"]
    save_key = args["save_key"]
    
    try:
        # 构建视频截帧处理参数，时间单位为毫秒
        process = f"video/snapshot,t_{int(time)},f_{format}"
        
        # 使用官方SDK写法，通过save_bucket和save_object参数执行视频截帧和持久化
        resp = tos_client.get_object(
            bucket=bucket_name,
            key=object_key,
            process=process,
            save_bucket=base64.b64encode(save_bucket.encode("utf-8")).decode("utf-8"),
            save_object=base64.b64encode(save_key.encode("utf-8")).decode("utf-8")
        )
        
        # 读取处理结果以确保截帧完成
        processed_data = resp.read()
        
        # 等待一下确保回写完成
        import time as time_module
        time_module.sleep(1.0)
        
        # 生成截帧图片的预签名 URL
        download_url = tos_client.pre_signed_url(tos.HttpMethodType.Http_Method_Get, save_bucket, save_key, 3600)
        
        result = {
            "presigned_url": download_url.signed_url,
            "source_bucket": bucket_name,
            "source_key": object_key,
            "save_bucket": save_bucket,
            "save_key": save_key,
            "time": time,
            "format": format,
            "processed_size": len(processed_data),
            "expires_in": 3600,
            "status": "processed"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"视频截帧失败: {str(e)}")]

async def video_info(args: Dict[str, Any]) -> List[TextContent]:
    """获取视频信息"""
    bucket_name = args["bucket_name"]
    object_key = args["object_key"]
    
    try:
        # 使用 get_object 方法通过 style 参数获取视频信息
        # 设置处理参数为 video/info
        resp = tos_client.get_object(bucket_name, object_key, process="video/info")
        video_info_data = resp.read().decode('utf-8')
        
        # 尝试解析JSON响应
        try:
            video_info_json = json.loads(video_info_data)
            result = {
                "bucket": bucket_name,
                "key": object_key,
                "video_info": video_info_json,
                "status": "success"
            }
        except json.JSONDecodeError:
            # 如果不是JSON格式，直接返回原始数据
            result = {
                "bucket": bucket_name,
                "key": object_key,
                "video_info": video_info_data,
                "status": "success",
                "note": "返回原始格式数据"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"获取视频信息失败: {str(e)}")]

async def main():
    """主函数"""
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

if __name__ == "__main__":
    asyncio.run(main())