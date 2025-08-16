# TOS MCP Server 使用说明

## 简介

TOS MCP Server 是一个基于 Model Context Protocol (MCP) 的火山引擎对象存储 (TOS) 工具服务器，提供了完整的 TOS 操作功能。

## 安装

1. 安装依赖：
```bash
pip install -r requirements.txt
```

或者使用 setup.py 安装：
```bash
pip install -e .
```

## 环境变量配置

在使用之前，需要设置以下环境变量：

```bash
export TOS_ACCESS_KEY="your_access_key"
export TOS_SECRET_KEY="your_secret_key"
export TOS_REGION="cn-beijing"  # 可选，默认为 cn-beijing
export TOS_ENDPOINT="tos-cn-beijing.volces.com"  # 可选，会根据 region 自动生成
```

## 启动服务器

```bash
python3 tos_mcp_server.py
```

## MCP 客户端配置

在你的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "tos": {
      "command": "python3",
      "args": ["/path/to/tos_mcp_server.py"],
      "env": {
        "TOS_ACCESS_KEY": "your_access_key",
        "TOS_SECRET_KEY": "your_secret_key",
        "TOS_REGION": "cn-beijing"
      }
    }
  }
}
```

## 可用工具

### 桶管理

1. **tos_create_bucket** - 创建存储桶
   - `bucket_name`: 存储桶名称
   - `acl`: 访问控制权限 (private/public-read/public-read-write)

2. **tos_list_buckets** - 列举存储桶
   - 无参数

3. **tos_get_bucket_meta** - 获取存储桶元数据
   - `bucket_name`: 存储桶名称

4. **tos_delete_bucket** - 删除存储桶
   - `bucket_name`: 存储桶名称

### 对象管理

5. **tos_put_object** - 上传对象
   - `bucket_name`: 存储桶名称
   - `object_key`: 对象键名
   - `content`: 文件内容
   - `content_type`: 内容类型 (可选)
   - `is_base64`: 内容是否为base64编码 (可选)

6. **tos_get_object** - 下载对象
   - `bucket_name`: 存储桶名称
   - `object_key`: 对象键名
   - `return_as_base64`: 是否以base64格式返回 (可选)

7. **tos_list_objects** - 列举对象
   - `bucket_name`: 存储桶名称
   - `prefix`: 对象键前缀 (可选)
   - `delimiter`: 分隔符 (可选)
   - `max_keys`: 最大返回数量 (可选)

8. **tos_delete_object** - 删除对象
   - `bucket_name`: 存储桶名称
   - `object_key`: 对象键名

### 预签名 URL

9. **tos_presigned_url** - 生成预签名 URL
   - `bucket_name`: 存储桶名称
   - `object_key`: 对象键名
   - `method`: HTTP方法 (GET/PUT/POST/DELETE)
   - `expires`: 过期时间（秒）

### 图片处理

10. **tos_image_process** - 基础图片处理
    - `bucket_name`: 存储桶名称
    - `object_key`: 图片对象键名
    - `process`: 图片处理参数

11. **tos_image_info** - 获取图片信息
    - `bucket_name`: 存储桶名称
    - `object_key`: 图片对象键名

12. **tos_image_persist** - 图片处理持久化
    - `bucket_name`: 存储桶名称
    - `object_key`: 图片对象键名
    - `process`: 图片处理参数
    - `save_bucket`: 保存的存储桶名称
    - `save_key`: 保存的对象键名

### 视频处理

13. **tos_video_snapshot** - 视频截帧
    - `bucket_name`: 存储桶名称
    - `object_key`: 视频对象键名
    - `time`: 截帧时间点（秒）
    - `format`: 输出格式 (jpg/png)

14. **tos_video_info** - 获取视频信息
    - `bucket_name`: 存储桶名称
    - `object_key`: 视频对象键名

## 使用示例

### 创建存储桶
```json
{
  "tool": "tos_create_bucket",
  "arguments": {
    "bucket_name": "my-test-bucket",
    "acl": "private"
  }
}
```

### 上传文件
```json
{
  "tool": "tos_put_object",
  "arguments": {
    "bucket_name": "my-test-bucket",
    "object_key": "test.txt",
    "content": "Hello, TOS!",
    "content_type": "text/plain"
  }
}
```

### 生成下载链接
```json
{
  "tool": "tos_presigned_url",
  "arguments": {
    "bucket_name": "my-test-bucket",
    "object_key": "test.txt",
    "method": "GET",
    "expires": 3600
  }
}
```

### 图片处理
```json
{
  "tool": "tos_image_process",
  "arguments": {
    "bucket_name": "my-test-bucket",
    "object_key": "image.jpg",
    "process": "resize,w_100,h_100"
  }
}
```

## 注意事项

1. 确保 TOS_ACCESS_KEY 和 TOS_SECRET_KEY 环境变量已正确设置
2. 存储桶名称需要符合 TOS 命名规范
3. 图片和视频处理功能需要 TOS 服务端支持
4. 大文件上传建议使用分片上传（可在后续版本中添加）

## 错误处理

所有工具都包含异常处理，会返回详细的错误信息帮助调试。常见错误包括：

- 认证失败：检查 ACCESS_KEY 和 SECRET_KEY
- 权限不足：检查账户权限配置
- 存储桶不存在：确保存储桶名称正确
- 网络连接问题：检查网络和端点配置

## 参考文档

- [TOS Python SDK 文档](https://www.volcengine.com/docs/6349/92785)
- [MCP 协议文档](https://modelcontextprotocol.io/)