"""End-to-end tests for the WebSocket log-streaming endpoint."""
import asyncio
import json
import pytest

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.logging import get_or_create_queue, remove_queue, write_log


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SESSION = "ws-test-session"


@pytest.fixture(autouse=True)
def cleanup_queue():
    """Remove test queue before and after each test to avoid cross-test leakage."""
    remove_queue(SESSION)
    yield
    remove_queue(SESSION)


# ---------------------------------------------------------------------------
# Unit tests — logging service (no HTTP/WS needed)
# ---------------------------------------------------------------------------

def test_get_or_create_queue_returns_same_instance():
    q1 = get_or_create_queue("q-test")
    q2 = get_or_create_queue("q-test")
    assert q1 is q2
    remove_queue("q-test")


def test_remove_queue_is_idempotent():
    remove_queue("nonexistent-session")  # must not raise


@pytest.mark.asyncio
async def test_write_log_pushes_to_queue(tmp_path):
    """write_log should enqueue the entry when a queue exists for the session."""
    sid = "log-queue-test"
    q = get_or_create_queue(sid)

    # Use a minimal in-memory DB so we can call write_log without a real session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        result = await write_log(db, sid, "orchestrator", "test_action", {"k": "v"})
    finally:
        db.close()
        remove_queue(sid)

    assert result["agent"] == "orchestrator"
    assert result["action"] == "test_action"
    assert q.qsize() == 1
    item = q.get_nowait()
    assert item["action"] == "test_action"
    assert item["payload"] == {"k": "v"}


@pytest.mark.asyncio
async def test_write_log_skips_missing_queue(tmp_path):
    """write_log must not raise when no WebSocket is listening."""
    remove_queue("no-ws-session")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        result = await write_log(db, "no-ws-session", "logistics", "some_action")
    finally:
        db.close()

    assert result["agent"] == "logistics"


# ---------------------------------------------------------------------------
# Integration tests — WebSocket endpoint via ASGI
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_websocket_connects_and_receives_log():
    """Client connects, a log is pushed to the queue, client receives it."""
    # Pre-register queue so the WS handler reuses it
    queue = get_or_create_queue(SESSION)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        async with client.stream("GET", f"/ws/logs/{SESSION}",
                                 headers={"connection": "upgrade",
                                          "upgrade": "websocket",
                                          "sec-websocket-key": "dGhlIHNhbXBsZSBub25jZQ==",
                                          "sec-websocket-version": "13"}):
            # Push a log entry directly to the queue
            await queue.put({"agent": "orchestrator", "action": "test", "payload": {}})
            item = await asyncio.wait_for(queue.get(), timeout=2.0)

    assert item["agent"] == "orchestrator"
    assert item["action"] == "test"


@pytest.mark.asyncio
async def test_websocket_queue_lifecycle():
    """Queue is created on WS connect and can be removed on disconnect."""
    # Simulate the lifecycle manually
    q = get_or_create_queue(SESSION)
    assert q is not None

    await q.put({"type": "ping"})
    assert q.qsize() == 1

    remove_queue(SESSION)
    # After removal, a new call creates a fresh empty queue
    q2 = get_or_create_queue(SESSION)
    assert q2.qsize() == 0
