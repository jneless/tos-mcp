#!/usr/bin/env python3
"""
测试脚本：验证修复后的 image_info 和 video_info 功能
"""

import asyncio
import json
from tos_mcp_server import image_info, video_info

async def test_image_info():
    """测试图片信息获取功能"""
    print("测试图片信息获取功能...")
    
    # 测试参数 - 请根据实际情况修改
    test_args = {
        "bucket_name": "test-bucket",  # 请替换为实际的bucket名
        "object_key": "test-image.jpg"  # 请替换为实际的图片文件
    }
    
    try:
        result = await image_info(test_args)
        print("图片信息获取结果:")
        for content in result:
            print(content.text)
            
        # 尝试解析结果
        if result and result[0].text:
            try:
                data = json.loads(result[0].text)
                print("\n解析后的结果:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                
    except Exception as e:
        print(f"测试失败: {e}")

async def test_video_info():
    """测试视频信息获取功能"""
    print("\n" + "="*50)
    print("测试视频信息获取功能...")
    
    # 测试参数 - 请根据实际情况修改
    test_args = {
        "bucket_name": "test-bucket",  # 请替换为实际的bucket名
        "object_key": "test-video.mp4"  # 请替换为实际的视频文件
    }
    
    try:
        result = await video_info(test_args)
        print("视频信息获取结果:")
        for content in result:
            print(content.text)
            
        # 尝试解析结果
        if result and result[0].text:
            try:
                data = json.loads(result[0].text)
                print("\n解析后的结果:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                
    except Exception as e:
        print(f"测试失败: {e}")

async def main():
    """主测试函数"""
    print("开始测试 TOS MCP 图片和视频信息功能")
    print("="*50)
    
    await test_image_info()
    await test_video_info()
    
    print("\n" + "="*50)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(main())