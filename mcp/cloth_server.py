#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊购物搜索 MCP 服务器
使用 SerpApi 进行亚马逊产品搜索
同时支持 MCP 协议（SSE）和 REST API
"""

from mcp.server.fastmcp import FastMCP
from serpapi import GoogleSearch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# 创建 MCP 服务器
mcp = FastMCP("AmazonShopping", host="0.0.0.0", port=8002)

@mcp.tool()
def search_amazon_products(keyword: str, max_results: int = 1) -> dict:
    """
    Search for products on Amazon and return the results.
    - keyword: Product search keyword (e.g., "Camera", "Laptop", "Coffee")
    - max_results: Maximum number of results to return (default: 1)
    """
    try:
        # 搜索参数
        params = {
            "engine": "amazon",
            "k": keyword,
            "amazon_domain": "amazon.com",
            "gl": "us",
            "api_key": "1e993b0be4a70eb4b1397535203c612ef84dea16e2da7bc91bd874c173089842"
        }
        
        # 执行搜索
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # 获取有机搜索结果
        organic_results = results.get("organic_results", [])
        
        if not organic_results:
            return {"success": False, "message": "未找到产品"}
        
        # 只获取第一个产品的基本信息
        product = organic_results[0]
        return {
            "success": True,
            "data": {
                "title": product.get('title', 'N/A'),
                "price": product.get('price', 'N/A'),
                "link": product.get('link', 'N/A')
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"搜索失败，错误：{str(e)}",
            "data": None
        }

# 创建 FastAPI 应用，提供 REST API
app = FastAPI(title="AmazonShopping MCP Server")

class ToolCallRequest(BaseModel):
    name: str
    arguments: dict

@app.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """REST API 端点：兼容 ESP32 设备端的调用方式"""
    if request.name == "search_amazon_products":
        keyword = request.arguments.get("keyword", "")
        if not keyword:
            raise HTTPException(status_code=400, detail="Missing keyword argument")
        
        max_results = request.arguments.get("max_results", 1)
        
        # 调用 MCP 工具函数
        result = search_amazon_products(keyword, max_results)
        return result
    else:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {request.name}")

@app.get("/")
async def root():
    return {
        "service": "AmazonShopping MCP Server", 
        "status": "running",
        "modes": ["REST API (port 8002)", "MCP SSE (optional)"],
        "endpoints": {
            "rest": "http://192.168.175.31:8002/tools/call",
            "mcp_sse": "http://192.168.175.31:8002/sse (if enabled)"
        },
        "note": "Use REST API for ESP32 devices, MCP SSE for standard MCP clients"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    # 运行 REST API 服务器
    uvicorn.run(app, host="0.0.0.0", port=8002)