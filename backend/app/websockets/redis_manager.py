import json
import redis.asyncio as aioredis
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from collections import defaultdict

REDIS_URL = "redis://redis:6379"

class RedisConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self.redis = None

    async def startup(self):
        self.redis = await aioredis.from_url(REDIS_URL)

    async def connect(self, websocket: WebSocket, branch_id: str):
        await websocket.accept()
        self.active_connections[branch_id].append(websocket)

    def disconnect(self, websocket: WebSocket, branch_id: str):
        if websocket in self.active_connections[branch_id]:
            self.active_connections[branch_id].remove(websocket)

    async def publish(self, message: dict, branch_id: str):
        await self.redis.publish(f"branch:{branch_id}", json.dumps(message))

    async def broadcast_local(self, message: dict, branch_id: str):
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
    async def add_presence(self, branch_id: str, user_id: str):
        await self.redis.sadd(f"presence:{branch_id}", user_id)
        await self.redis.expire(f"presence:{branch_id}", 3600)

    async def remove_presence(self, branch_id: str, user_id: str):
        await self.redis.srem(f"presence:{branch_id}", user_id)

    async def get_presence(self, branch_id: str) -> list:
        members = await self.redis.smembers(f"presence:{branch_id}")
        return [m.decode() for m in members]
redis_manager = RedisConnectionManager()