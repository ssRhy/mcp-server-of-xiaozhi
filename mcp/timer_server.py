from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime
import uuid

mcp = FastMCP("Timer")

@mcp.tool()
def add_timer(duration_seconds: int, title: str = "", now: str = None) -> dict:
    """
    添加倒计时，保存到timer.json
    - duration_seconds: 倒计时时长（秒）
    - title: 事件标题
    """
    try:
        request_id = str(uuid.uuid4())
        now_time = now or datetime.now().isoformat(timespec="seconds")
        data = {
            "request_id": request_id,
            "type": "timer",
            "action": "start",
            "payload": {
                "title": title,
                "duration_seconds": duration_seconds,
            },
            "timestamp": now_time
        }
        with open("timer.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {
            "success": True,
            "message": "Timer saved.",
            "data": data
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"保存失败，错误：{str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport="sse")