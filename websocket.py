import asyncio
import websockets
import socket
import json
from pathlib import Path
import functools

class ReminderWebSocketServer:
    def __init__(self, reminder_file_path="reminder.json"):
        self.reminder_file_path = Path(reminder_file_path)
        self.clients = set()
        
    def load_reminders(self):
        """加载提醒数据"""
        try:
            if self.reminder_file_path.exists():
                with open(self.reminder_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"加载提醒数据出错: {e}")
            return []
    
    def save_reminders(self, reminders):
        """保存提醒数据"""
        try:
            with open(self.reminder_file_path, 'w', encoding='utf-8') as f:
                json.dump(reminders, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存提醒数据出错: {e}")
            return False
    
    def delete_reminder_by_id(self, request_id):
        """通过request_id删除提醒"""
        reminders = self.load_reminders()
        # 过滤掉匹配的request_id
        reminders = [r for r in reminders if r.get('request_id') != request_id]
        self.save_reminders(reminders)
    
    async def handle_client_message(self, websocket, message):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            
            # 检查是否是删除请求
            if (data.get('action') == 'result' and 
                data.get('type') == 'reminder' and
                data.get('status') in ['success', 'skipped']):
                
                request_id = data.get('request_id')
                if request_id:
                    self.delete_reminder_by_id(request_id)
                    
        except Exception as e:
            print(f"处理客户端消息出错: {e}")
    
    async def handle_client(self, websocket):
        """处理客户端连接"""
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"处理客户端时出错: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def broadcast_first_reminder(self):
        """广播第一个提醒"""
        while True:
            try:
                reminders = self.load_reminders()
                
                # 有内容就推第一条，没有就不推
                if reminders:
                    first_reminder = reminders[0]
                    
                    # 广播给所有连接的客户端
                    if self.clients:
                        clients_copy = self.clients.copy()
                        for client in clients_copy:
                            try:
                                await client.send(json.dumps(first_reminder, ensure_ascii=False))
                            except:
                                self.clients.discard(client)
                
            except Exception as e:
                print(f"广播提醒时出错: {e}")
            
            # 等待1秒
            await asyncio.sleep(1)
    
    async def start_server(self, host="0.0.0.0", port=8080):
        """启动WebSocket服务器"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "本机ip获取失败"
        print(f"启动WebSocket服务器在 ws://{host}:{port}")
        print(f"局域网内其他设备请使用 ws://{local_ip}:{port}连接")
        
        # 启动广播任务
        broadcast_task = asyncio.create_task(self.broadcast_first_reminder())
        
        # 启动WebSocket服务器
        async def handler_wrapper(websocket):
            await self.handle_client(websocket)
            
        server = await websockets.serve(
            handler_wrapper, host, port
        )
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            broadcast_task.cancel()
            server.close()

def main():
    server = ReminderWebSocketServer("reminder.json")
    asyncio.run(server.start_server())

if __name__ == "__main__":
    main()