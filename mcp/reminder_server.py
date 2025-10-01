from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime
import uuid

mcp = FastMCP("Reminder")

@mcp.tool()
def save_reminder(title: str, original_text: str, parsed_time: str) -> dict:
    """
    生成唯一 request_id，并保存AI推算的提醒事项到 reminder.json，结构符合自定义协议。
    - title: 提醒事项标题
    - original_text: 用户说的原始自然语言时间
    - parsed_time: AI推算出的标准ISO时间
    """
    try:
        # 检查parsed_time是否为合法ISO时间
        datetime.fromisoformat(parsed_time)
        now = datetime.now().isoformat(timespec="seconds")
        request_id = str(uuid.uuid4())
        
        new_reminder = {
            "request_id": request_id,
            "type": "reminder",
            "action": "add",
            "payload": {
                "title": title,
                "time": parsed_time,
                "original_text": original_text
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
        existing_data.append(new_reminder)
        
        # 保存回文件
        with open("reminder.json", "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Reminder saved.",
            "data": new_reminder
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"保存失败，错误：{str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport="sse")

