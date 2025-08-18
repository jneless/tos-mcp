# 火山引擎 对象存储 TOS 非官方 MCP工具

* TOS 非官方 MCP 工具

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境变量配置

```bash
export TOS_ACCESS_KEY="your_access_key"
export TOS_SECRET_KEY="your_secret_key"
export TOS_REGION="cn-beijing"  # 可选，默认为 cn-beijing
```

### 启动服务器

使用启动脚本：
```bash
./start_server.sh
```

或直接运行：
```bash
python3 tos_mcp_server.py
```

## 项目文件说明

| 文件名 | 作用 |
|--------|------|
| `tos_mcp_server.py` | 主服务器文件，实现所有TOS操作的MCP工具 |
| `start_server.sh` | 启动脚本，检查环境变量并启动服务器 |
| `requirements.txt` | Python依赖包列表 |
| `setup.py` | Python包安装配置文件 |
| `mcp_config.json` | MCP客户端配置示例文件 |
| `USAGE.md` | 详细使用说明文档 |
| `LICENSE` | 项目许可证文件 |

## 主要功能

- **桶管理**: 创建、列举、删除存储桶，获取桶元数据
- **对象管理**: 上传、下载、列举、删除对象
- **预签名URL**: 生成各种HTTP方法的预签名访问链接
- **图片处理**: 基础图片处理、获取图片信息、处理结果持久化
- **视频处理**: 视频截帧、获取视频信息

详细使用方法请参考 [USAGE.md](USAGE.md) 文件。

## API 测试状态

| API 名称 | 功能描述 | 分类 | 测试状态 | 测试环境 | 备注 |
|---------|---------|------|---------|---------|------|
| `tos_create_bucket` | 创建存储桶 | 桶管理 | ✅ 已测试 | trae | - |
| `tos_list_buckets` | 列举存储桶 | 桶管理 | ✅ 已测试 | trae | - |
| `tos_get_bucket_meta` | 获取存储桶元数据 | 桶管理 | ✅ 已测试 | trae | - |
| `tos_delete_bucket` | 删除存储桶 | 桶管理 | ✅ 已测试 | trae | - |
| `tos_put_object` | 上传对象 | 对象管理 | ✅ 已测试 | trae | - |
| `tos_get_object` | 下载对象 | 对象管理 | ✅ 已测试 | trae | - |
| `tos_list_objects` | 列举对象 | 对象管理 | ✅ 已测试 | trae | - |
| `tos_delete_object` | 删除对象 | 对象管理 | ✅ 已测试 | trae | - |
| `tos_presigned_url` | 生成预签名URL | 预签名 | ✅ 已测试 | trae | - |
| `tos_image_process` | 基础图片处理 | 图片处理 | ⏳ 待测试 | - | - |
| `tos_image_info` | 获取图片信息 | 图片处理 | ⏳ 待测试 | - | 已修复私有访问bug |
| `tos_image_persist` | 图片处理持久化 | 图片处理 | ⏳ 待测试 | - | - |
| `tos_video_snapshot` | 视频截帧 | 视频处理 | ⏳ 待测试 | - | - |
| `tos_video_info` | 获取视频信息 | 视频处理 | ⏳ 待测试 | - | 已修复私有访问bug |



## TOS 文档
Python SDK 简介:https://www.volcengine.com/docs/6349/92785
安装 Python SDK:https://www.volcengine.com/docs/6349/93479
初始化客户端（Python SDK）:https://www.volcengine.com/docs/6349/93483
快速入门（Python SDK）:https://www.volcengine.com/docs/6349/92786
普通预签名（Python SDK）:https://www.volcengine.com/docs/6349/135725
创建桶(PythonSDK):https://www.volcengine.com/docs/6349/92793
列举桶(PythonSDK):https://www.volcengine.com/docs/6349/92794
获取桶元数据(PythonSDK):https://www.volcengine.com/docs/6349/92795
删除桶(PythonSDK):https://www.volcengine.com/docs/6349/92796
普通上传（Python SDK）:https://www.volcengine.com/docs/6349/92800
普通下载（Python SDK）:https://www.volcengine.com/docs/6349/92803
列举对象 V2（Python SDK）:https://www.volcengine.com/docs/6349/173820
删除对象（Python SDK）:https://www.volcengine.com/docs/6349/92805
基础图片处理（Python SDK）:https://www.volcengine.com/docs/6349/1157332
获取图片信息（Python SDK）:https://www.volcengine.com/docs/6349/1157336
图片处理持久化（Python SDK）:https://www.volcengine.com/docs/6349/1157338
视频截帧（Python SDK）:https://www.volcengine.com/docs/6349/1157340
获取视频信息（Python SDK）:https://www.volcengine.com/docs/6349/1157341
获取视频信息（Python SDK）:https://www.volcengine.com/docs/6349/1157343