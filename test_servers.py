#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 MCP 服务器"""

import asyncio
import aiohttp
import json

async def test_cloth_server():
    """测试亚马逊购物搜索"""
    print("\n" + "="*60)
    print("测试 Cloth Server (Amazon Shopping) - 端口 8002")
    print("="*60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 测试服务是否在线
            async with session.get("http://127.0.0.1:8002") as response:
                if response.status != 200:
                    raise Exception(f"服务器返回状态码: {response.status}")
                print("\n✅ 服务器在线")
            
            # 测试工具调用
            print("\n🔍 搜索亚马逊产品: 'laptop'...")
            data = {
                "name": "search_amazon_products",
                "arguments": {
                    "keyword": "laptop",
                    "max_results": 2
                }
            }
            async with session.post("http://127.0.0.1:8002/tools/call", json=data) as response:
                if response.status != 200:
                    raise Exception(f"工具调用失败，状态码: {response.status}")
                result = await response.json()
                print(f"\n📦 搜索结果:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
                
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("   请先运行: python mcp/cloth_server.py")

async def test_news_server():
    """测试谷歌新闻搜索"""
    print("\n" + "="*60)
    print("测试 News Server (Google News) - 端口 8003")
    print("="*60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 测试服务是否在线
            async with session.get("http://192.168.175.31:8003") as response:
                if response.status != 200:
                    raise Exception(f"服务器返回状态码: {response.status}")
                print("\n✅ 服务器在线")
            
            # 测试工具调用
            print("\n🔍 搜索新闻: 'technology'...")
            data = {
                "name": "search_google_news",
                "arguments": {
                    "keyword": "technology"
                }
            }
            async with session.post("http://192.168.175.31:8003/tools/call", json=data) as response:
                if response.status != 200:
                    raise Exception(f"工具调用失败，状态码: {response.status}")
                result = await response.json()
                print(f"\n📰 搜索结果:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
                
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("   请先运行: python mcp/news_server.py")

async def main():
    await test_cloth_server()
    await asyncio.sleep(1)
    await test_news_server()
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
