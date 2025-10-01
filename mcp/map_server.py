from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime
import uuid

mcp = FastMCP("ToWhereByWhat")

@mcp.tool()
def save_guidemap(destination: str, mode: str, parsed_time: str) -> dict:
    """
    生成唯一 request_id，并保存AI推算的地点出行方式到 reminder.json，结构符合自定义协议。
    - destination: destination address or place name
    - mode: Travel modes such as driving, walking, cycling, public transportation, etc
    """
    try:
        # 检查parsed_time是否为合法ISO时间
        datetime.fromisoformat(parsed_time)
        now = datetime.now().isoformat(timespec="seconds")
        request_id = str(uuid.uuid4())
        
        new_maprequest = {
            "request_id": request_id,
            "type": "guidemap",
            "action": "add",
            "payload": {
                "destination": destination,
                "mode": mode,
            },
            "timestamp": now
        }
        
        # 读取现有数据
        try:
            with open("reminder.json", "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]  # 兼容旧格式
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
        
        # 追加新数据
        existing_data.append(new_maprequest)
        
        # 保存回文件
        with open("reminder.json", "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Guidemap saved.",
            "data": new_maprequest
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"保存失败，错误：{str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport="sse")

