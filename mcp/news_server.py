#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google 新闻搜索 MCP 服务器
使用 SerpApi 进行新闻搜索
同时支持 MCP 协议（SSE）和 REST API
"""

from mcp.server.fastmcp import FastMCP
from serpapi import GoogleSearch
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import asyncio

# 创建 MCP 服务器（用于 SSE 端点）
mcp = FastMCP("GoogleNews", host="0.0.0.0", port=8004)

@mcp.tool()
def search_google_news(keyword: str) -> dict:
    """
    Search for news articles on Google News and return the results.
    - keyword: News search keyword (e.g., "Coffee", "Technology", "Sports")
    """
    try:
        # 搜索参数
        params = {
            "engine": "google_news_light",
            "q": keyword,
            "google_domain": "google.com",
            "api_key": "1e993b0be4a70eb4b1397535203c612ef84dea16e2da7bc91bd874c173089842"
        }
        
        # 执行搜索
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # 获取新闻结果
        news_results = results.get("news_results", [])
        
        if not news_results:
            return {"success": False, "message": "未找到新闻"}
        
        # 只获取第一条新闻的基本信息
        news = news_results[0]
        return {
            "success": True,
            "data": {
                "title": news.get('title', 'N/A'),
                "source": news.get('source', 'N/A'),
                "link": news.get('link', 'N/A')
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"搜索失败，错误：{str(e)}",
            "data": None
        }

# 创建 FastAPI 应用，提供 REST API
app = FastAPI(title="GoogleNews MCP Server")

class ToolCallRequest(BaseModel):
    name: str
    arguments: dict

@app.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """REST API 端点：兼容 ESP32 设备端的调用方式"""
    if request.name == "search_google_news":
        keyword = request.arguments.get("keyword", "")
        if not keyword:
            raise HTTPException(status_code=400, detail="Missing keyword argument")
        
        # 调用 MCP 工具函数
        result = search_google_news(keyword)
        return result
    else:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {request.name}")

@app.get("/")
async def root():
    return {
        "service": "GoogleNews MCP Server", 
        "status": "running",
        "modes": ["REST API (port 8003)", "MCP SSE (port 8004)"],
        "endpoints": {
            "rest": "http://192.168.175.31:8003/tools/call",
            "mcp_sse": "http://192.168.175.31:8004/sse"
        },
        "note": "Use REST API for ESP32 devices, MCP SSE for standard MCP clients"
    }

if __name__ == "__main__":
    # 运行 REST API 服务器
    uvicorn.run(app, host="0.0.0.0", port=8003)
    
    # 如果需要同时运行 MCP SSE 服务器，可以在另一个终端运行：
    # python -c "from mcp.server.fastmcp import FastMCP; from news_server import mcp; mcp.run(transport='sse')"