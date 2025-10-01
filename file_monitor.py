# 创建 file_monitor.py
import asyncio
import json
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, websocket_server):
        self.websocket_server = websocket_server
        self.last_content = {}  # 记录文件最后内容
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # 只监控我们关心的JSON文件
        if event.src_path.endswith(('.json',)) and any(name in event.src_path 
            for name in ['reminder', 'calendar', 'memo', 'timer', 'stopwatch']):
            asyncio.create_task(self.handle_file_change(event.src_path))
    
    async def handle_file_change(self, file_path):
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # 检查内容是否有变化
            if file_path not in self.last_content or self.last_content[file_path] != current_content:
                self.last_content[file_path] = current_content
                
                # 解析JSON并发送到APP
                try:
                    data = json.loads(current_content)
                    # 如果是数组，只发送最新的一条
                    if isinstance(data, list) and data:
                        latest_item = data[-1]
                        await self.websocket_server.forward_to_app(latest_item)
                    elif isinstance(data, dict):
                        await self.websocket_server.forward_to_app(data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON in {file_path}")
                    
        except Exception as e:
            print(f"Error handling file change: {e}")

# 集成到 WebSocket 服务器
class MCPWebSocketServer:
    def __init__(self):
        self.connected_clients = {}
        self.mcp_processes = {}
        self.file_observer = None
        
    async def start_file_monitoring(self):
        """启动文件监控"""
        handler = FileChangeHandler(self)
        self.file_observer = Observer()
        self.file_observer.schedule(handler, path='.', recursive=False)
        self.file_observer.start()
        print("File monitoring started")
    
    async def start_server(self, host="0.0.0.0", port=8080):
        """启动WebSocket服务器和文件监控"""
        await self.start_file_monitoring()
        print(f"Starting WebSocket server on {host}:{port}")
        async with websockets.serve(self.handle_client, host, port):
            print("WebSocket server is running...")
            await asyncio.Future()