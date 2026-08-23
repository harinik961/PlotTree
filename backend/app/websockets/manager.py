from collections import defaultdict
from fastapi import WebSocket
from starlette.websockets import WebSocketState

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, branch_id: str):
        await websocket.accept()
        self.active_connections[branch_id].append(websocket)

    def disconnect(self, websocket: WebSocket, branch_id: str):
        if websocket in self.active_connections[branch_id]:
            self.active_connections[branch_id].remove(websocket)

    async def broadcast(self, message: dict, branch_id: str):
        dead = []
        for connection in self.active_connections[branch_id]:
            if connection.client_state == WebSocketState.CONNECTED:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead.append(connection)
            else:
                dead.append(connection)
        for d in dead:
            self.active_connections[branch_id].remove(d)

manager = ConnectionManager()