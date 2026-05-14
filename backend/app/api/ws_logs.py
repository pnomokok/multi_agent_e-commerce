"""WebSocket endpoint — streams live agent logs to frontend (Wow 3)."""
import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.logging import get_or_create_queue, remove_queue

router = APIRouter()


@router.websocket("/ws/logs/{session_id}")
async def ws_agent_logs(websocket: WebSocket, session_id: str):
    await websocket.accept()
    queue = get_or_create_queue(session_id)
    try:
        while True:
            try:
                # Wait up to 30s for a log entry; send ping if idle
                log_entry = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_text(json.dumps(log_entry))
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        remove_queue(session_id)
