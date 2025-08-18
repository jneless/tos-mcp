"""
TOS MCP Server 功能处理器
"""

import json
import base64
import logging
from typing import Any, Dict, List

import tos
from mcp.types import TextContent

from .config import tos_config

logger = logging.getLogger(__name__)

# 初始化 TOS 客户端
tos_client = tos.TosClientV2(
    ak=tos_config.access_key,
    sk=tos_config.secret_key,
    endpoint=tos_config.endpoint,
    region=tos_config.region
)

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