from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.redis_manager import redis_manager
from app.database import SessionLocal
from app.services.sentence_service import create_sentence
import asyncio
import json

router = APIRouter()

@router.websocket("/ws/{branch_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    branch_id: str,
    token: str = None
):
    await redis_manager.connect(websocket, branch_id)
    pubsub = redis_manager.redis.pubsub()
    await pubsub.subscribe(f"branch:{branch_id}")

    async def listen_to_redis():
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await redis_manager.broadcast_local(data, branch_id)

    redis_task = asyncio.create_task(listen_to_redis())

    try:
        while True:
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
                # when writer connects
                if data.get("type") == "join":
                    user_id = data.get("user_id")
                    await redis_manager.add_presence(branch_id, user_id)
                    present = await redis_manager.get_presence(branch_id)
                    await redis_manager.publish({
                        "type": "presence_update",
                        "users": present,
                        "branch_id": branch_id
                    }, branch_id)
                    # when writer disconnects (in except WebSocketDisconnect)

                    await redis_manager.remove_presence(branch_id, user_id)
                    present = await redis_manager.get_presence(branch_id)
                    await redis_manager.publish({
                        "type": "presence_update", 
                        "users": present,
                        "branch_id": branch_id
                    }, branch_id)
                
                # handle different message types
                elif data.get("type") == "new_sentence":
                    db = SessionLocal()
                    try:
                        sentence = create_sentence(
                            db=db,
                            branch_id=branch_id,
                            author_id=data.get("author_id"),
                            content=data.get("content")
                        )
                        # broadcast the saved sentence to everyone
                        await redis_manager.publish({
                            "type": "new_sentence",
                            "id": str(sentence.id),
                            "content": sentence.content,
                            "author_id": str(sentence.author_id),
                            "branch_id": branch_id
                        }, branch_id)
                    finally:
                        db.close()

                elif data.get("type") == "presence":
                    # broadcast who's in the room
                    await redis_manager.publish({
                        "type": "presence",
                        "user_id": data.get("user_id"),
                        "branch_id": branch_id
                    }, branch_id)

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        if user_id:  # use it here
            await redis_manager.remove_presence(branch_id, user_id)
        redis_manager.disconnect(websocket, branch_id)
        redis_task.cancel()
        await pubsub.unsubscribe(f"branch:{branch_id}")
        await redis_manager.publish({
            "type": "user_left",
            "branch_id": branch_id
        }, branch_id)