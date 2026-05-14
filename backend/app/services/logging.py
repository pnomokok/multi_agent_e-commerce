"""Agent log writer — persists agent actions to DB and broadcasts via WebSocket."""
import asyncio
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session as DBSession

from app.models.agent_log import AgentLog

# session_id → asyncio.Queue used by the WebSocket endpoint
_log_queues: dict[str, asyncio.Queue] = {}


def get_or_create_queue(session_id: str) -> asyncio.Queue:
    if session_id not in _log_queues:
        _log_queues[session_id] = asyncio.Queue()
    return _log_queues[session_id]


def remove_queue(session_id: str) -> None:
    _log_queues.pop(session_id, None)


async def write_log(
    db: DBSession,
    session_id: str,
    agent_name: str,
    action: str,
    payload: dict[str, Any] | None = None,
) -> dict:
    ts = datetime.utcnow()
    entry = AgentLog(
        session_id=session_id,
        timestamp=ts,
        agent_name=agent_name,
        action=action,
        payload=payload or {},
    )
    db.add(entry)
    db.commit()

    log_dict = {
        "timestamp": ts.strftime("%H:%M:%S"),
        "agent": agent_name,
        "action": action,
        "payload": payload or {},
    }

    # push to live WebSocket queue if someone is listening
    q = _log_queues.get(session_id)
    if q:
        await q.put(log_dict)

    return log_dict
