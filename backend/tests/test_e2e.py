"""
End-to-end test suite for the EKO backend.

Covers the complete customer journey:
  health → products → persona → session → cart → chat (5 turns) → checkout
  + seller dashboard / logs

Uses ASGI transport so no live server is needed, but chat tests call the real
Gemini API — mark them with @pytest.mark.integration so they can be skipped in
CI with:  pytest -m "not integration"
"""

import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from app.main import app

BASE = "http://test"

# ---------------------------------------------------------------------------
# Shared ASGI client (module-scoped to avoid re-creating it per test)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="module")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE) as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ok(r, expected_status=200):
    assert r.status_code == expected_status, (
        f"Expected {expected_status}, got {r.status_code}: {r.text[:300]}"
    )
    return r.json()


# ===========================================================================
# 1. SYSTEM HEALTH
# ===========================================================================

@pytest.mark.asyncio
async def test_health(client):
    data = ok(await client.get("/api/health"))
    assert data["status"] == "ok"
    assert "eko" in data["service"]


# ===========================================================================
# 2. PRODUCTS & PERSONAS
# ===========================================================================

@pytest.mark.asyncio
async def test_list_products_returns_seeded_data(client):
    data = ok(await client.get("/api/products"))
    assert isinstance(data, list), "Expected a list"
    assert len(data) >= 10, f"Expected ≥10 products, got {len(data)}"
    ids = {p["id"] for p in data}
    assert "prod-kulaklık-01" in ids
    assert "prod-klavye-02" in ids


@pytest.mark.asyncio
async def test_list_personas_returns_three_customers(client):
    data = ok(await client.get("/api/personas"))
    assert len(data) == 3
    segments = {p["segment"] for p in data}
    assert "new" in segments
    assert "loyal" in segments
    assert "bargain_hunter" in segments


# ===========================================================================
# 3. SESSION LIFECYCLE
# ===========================================================================

@pytest_asyncio.fixture(scope="module")
async def session_id(client):
    """Create a session for Mehmet (loyal customer) — cart is empty at creation."""
    data = ok(await client.post(
        "/api/session/start",
        json={"customer_id": "customer-mehmet-02"},
    ), expected_status=200)
    sid = data["session_id"]
    assert sid, "session_id must be non-empty"
    return sid


@pytest_asyncio.fixture(scope="module")
async def session_with_cart(client):
    """Session for Mehmet with kulaklık + klavye already in cart.

    Used by chat/checkout tests so they work regardless of which test subset runs.
    """
    data = ok(await client.post(
        "/api/session/start",
        json={"customer_id": "customer-mehmet-02"},
    ))
    sid = data["session_id"]
    await client.post(f"/api/cart/{sid}/add", json={"product_id": "prod-kulaklık-01", "quantity": 1})
    await client.post(f"/api/cart/{sid}/add", json={"product_id": "prod-klavye-02", "quantity": 1})
    return sid


@pytest.mark.asyncio
async def test_session_created(session_id):
    assert session_id is not None
    assert len(session_id) > 8  # UUID-like


@pytest.mark.asyncio
async def test_get_session_initial_state(client, session_id):
    data = ok(await client.get(f"/api/session/{session_id}"))
    assert data["customer_id"] == "customer-mehmet-02"
    assert data["cart_items"] == []
    assert data["purchase_confirmed"] is False
    assert data["final_discount"] == 0.0


# ===========================================================================
# 4. CART OPERATIONS
# ===========================================================================

@pytest.mark.asyncio
async def test_empty_cart(client, session_id):
    data = ok(await client.get(f"/api/cart/{session_id}"))
    assert data["items"] == []
    assert data["subtotal"] == 0.0


@pytest.mark.asyncio
async def test_add_headphones_to_cart(client, session_id):
    data = ok(await client.post(
        f"/api/cart/{session_id}/add",
        json={"product_id": "prod-kulaklık-01", "quantity": 1},
    ))
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "prod-kulaklık-01"
    assert data["items"][0]["unit_price"] == 3499.0


@pytest.mark.asyncio
async def test_add_keyboard_to_cart(client, session_id):
    data = ok(await client.post(
        f"/api/cart/{session_id}/add",
        json={"product_id": "prod-klavye-02", "quantity": 1},
    ))
    assert len(data["items"]) == 2
    assert abs(data["subtotal"] - (3499.0 + 1899.0)) < 0.01


@pytest.mark.asyncio
async def test_add_nonexistent_product_returns_404(client, session_id):
    r = await client.post(
        f"/api/cart/{session_id}/add",
        json={"product_id": "prod-yok-00", "quantity": 1},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_remove_item_from_cart(client, session_id):
    # Add a throwaway item then remove it
    await client.post(
        f"/api/cart/{session_id}/add",
        json={"product_id": "prod-mouse-03", "quantity": 1},
    )
    data = ok(await client.post(
        f"/api/cart/{session_id}/remove",
        json={"product_id": "prod-mouse-03", "quantity": 1},
    ))
    ids = {i["product_id"] for i in data["items"]}
    assert "prod-mouse-03" not in ids


@pytest.mark.asyncio
async def test_cart_weight_calculated(client, session_id):
    data = ok(await client.get(f"/api/cart/{session_id}"))
    # kulaklık 0.25 kg + klavye 0.81 kg = 1.06 kg
    assert abs(data["total_weight_kg"] - 1.06) < 0.05


# ===========================================================================
# 5. CHAT — GUARD CASES (no Gemini call needed)
# ===========================================================================

@pytest.mark.asyncio
async def test_chat_unknown_session_returns_404(client):
    r = await client.post(
        "/api/chat/does-not-exist",
        json={"message": "Merhaba"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_chat_empty_cart_returns_friendly_message(client):
    """A fresh session with no cart items should get a helpful nudge."""
    empty = ok(await client.post(
        "/api/session/start",
        json={"customer_id": "customer-ayse-01"},
    ))
    r = ok(await client.post(
        f"/api/chat/{empty['session_id']}",
        json={"message": "indirim var mı?"},
    ))
    assert "sepet" in r["response_text"].lower() or "ürün" in r["response_text"].lower()
    assert r["agent_used"] == "orchestrator"


# ===========================================================================
# 6. CHAT — FULL AGENT FLOW  (calls real Gemini, marked integration)
# ===========================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_greeting(client, session_with_cart):
    data = ok(await client.post(
        f"/api/chat/{session_with_cart}",
        json={"message": "Merhaba, nasılsın?"},
    ))
    assert len(data["response_text"]) > 10
    assert data["agent_used"] == "orchestrator"
    # Greeting should NOT produce an offer
    assert data["offer_details"] is None
    # Logs must be populated
    assert len(data["agent_logs"]) >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_price_objection_triggers_negotiator(client, session_with_cart):
    data = ok(await client.post(
        f"/api/chat/{session_with_cart}",
        json={"message": "Bu ürünler çok pahalı, hiç indirim yapamaz mısınız?"},
    ))
    assert len(data["response_text"]) > 20
    assert data["agent_used"] == "negotiator"
    # negotiator should log at least intent + negotiation actions
    agent_names = {log["agent"] for log in data["agent_logs"]}
    assert "orchestrator" in agent_names
    assert "negotiator" in agent_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_negotiation_history_persisted(client, session_with_cart):
    """After a negotiation turn the session must have history."""
    sess = ok(await client.get(f"/api/session/{session_with_cart}"))
    assert len(sess["negotiation_history"]) >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_purchase_decision_triggers_logistics(client, session_with_cart):
    data = ok(await client.post(
        f"/api/chat/{session_with_cart}",
        json={"message": "Tamam, bu fiyata alıyorum!"},
    ))
    assert len(data["response_text"]) > 20
    assert data["agent_used"] == "logistics"
    # Logistics should return carbon data
    assert data["carbon_data"] is not None
    assert data["carbon_data"]["co2_saved_kg"] >= 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_delivery_choice_consolidated(client, session_with_cart):
    data = ok(await client.post(
        f"/api/chat/{session_with_cart}",
        json={"message": "Konsolide teslimatı seçiyorum, bekleyebilirim."},
    ))
    assert len(data["response_text"]) > 10
    assert data["agent_used"] == "logistics"
    # Session must have been updated
    sess = ok(await client.get(f"/api/session/{session_with_cart}"))
    assert sess["delivery_preference"] == "consolidated"


# ===========================================================================
# 7. SELLER POLICY
# ===========================================================================

SELLER = "seller-techstore-01"


@pytest.mark.asyncio
async def test_seller_get_policy(client):
    data = ok(await client.get(f"/api/seller/{SELLER}/policy"))
    assert data["seller_id"] == SELLER
    assert isinstance(data["negotiation_active"], bool)
    assert data["monthly_negotiation_budget"] > 0


@pytest.mark.asyncio
async def test_seller_update_policy_toggle_negotiation(client):
    # Disable negotiation
    data = ok(await client.put(
        f"/api/seller/{SELLER}/policy",
        json={"negotiation_active": False},
    ))
    assert data["negotiation_active"] is False

    # Re-enable negotiation
    data = ok(await client.put(
        f"/api/seller/{SELLER}/policy",
        json={"negotiation_active": True},
    ))
    assert data["negotiation_active"] is True


@pytest.mark.asyncio
async def test_seller_chat_blocked_when_negotiation_inactive(client):
    """While negotiation_active=False, chat should return a policy message."""
    # Disable
    await client.put(f"/api/seller/{SELLER}/policy", json={"negotiation_active": False})
    try:
        # Create a fresh session with items
        sess = ok(await client.post("/api/session/start", json={"customer_id": "customer-can-03"}))
        sid = sess["session_id"]
        await client.post(f"/api/cart/{sid}/add", json={"product_id": "prod-kulaklık-01", "quantity": 1})
        r = ok(await client.post(f"/api/chat/{sid}", json={"message": "indirim istiyorum"}))
        assert "pazarlık" in r["response_text"].lower() or "aktif" in r["response_text"].lower()
        assert r["agent_used"] == "orchestrator"
    finally:
        # Always re-enable
        await client.put(f"/api/seller/{SELLER}/policy", json={"negotiation_active": True})


# ===========================================================================
# 8. CHECKOUT
# ===========================================================================

@pytest.mark.asyncio
async def test_checkout_empty_cart_returns_400(client):
    sess = ok(await client.post("/api/session/start", json={"customer_id": "customer-ayse-01"}))
    r = await client.post(f"/api/checkout/{sess['session_id']}", json={"delivery_preference": "express"})
    assert r.status_code == 400


@pytest.mark.integration
@pytest.mark.asyncio
async def test_checkout_full_flow(client, session_with_cart):
    data = ok(await client.post(
        f"/api/checkout/{session_with_cart}",
        json={"delivery_preference": "consolidated"},
    ))
    assert data["order_id"].startswith("ORD-")
    assert data["summary"]["purchase_confirmed"] is True
    assert data["summary"]["delivery_preference"] == "consolidated"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_session_confirmed_after_checkout(client, session_with_cart):
    sess = ok(await client.get(f"/api/session/{session_with_cart}"))
    assert sess["purchase_confirmed"] is True


# ===========================================================================
# 9. SELLER DASHBOARD & LOGS
# ===========================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_seller_dashboard(client):
    data = ok(await client.get(f"/api/seller/{SELLER}/dashboard"))
    assert "policy" in data
    assert "stats" in data
    assert data["stats"]["seller_id"] == SELLER


@pytest.mark.integration
@pytest.mark.asyncio
async def test_seller_logs_populated_after_chat(client):
    data = ok(await client.get(f"/api/seller/{SELLER}/logs?limit=10"))
    assert isinstance(data, list)
    assert len(data) >= 1
    log = data[0]
    assert "agent_name" in log
    assert "action" in log
    assert "session_id" in log


# ===========================================================================
# 10. YENİ: quota_remaining, session logs, post-purchase guard, order
# ===========================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_returns_quota_remaining(client):
    """quota_remaining must be included in every ChatOut response (fresh session)."""
    sess = ok(await client.post("/api/session/start", json={"customer_id": "customer-can-03"}))
    sid = sess["session_id"]
    await client.post(f"/api/cart/{sid}/add", json={"product_id": "prod-kulaklık-01", "quantity": 1})
    data = ok(await client.post(f"/api/chat/{sid}", json={"message": "Merhaba"}))
    assert data["quota_remaining"] is not None
    assert isinstance(data["quota_remaining"], int)
    assert data["quota_remaining"] >= 0


@pytest.mark.asyncio
async def test_session_logs_endpoint(client, session_id):
    """GET /api/sessions/{id}/logs must exist and return a list."""
    data = ok(await client.get(f"/api/sessions/{session_id}/logs"))
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_session_logs_unknown_session_returns_404(client):
    r = await client.get("/api/sessions/nonexistent-999/logs")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_session_initial_state_has_awaiting_delivery_choice(client, session_id):
    """Fresh session must have awaiting_delivery_choice=False."""
    data = ok(await client.get(f"/api/session/{session_id}"))
    assert data["awaiting_delivery_choice"] is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_order_persisted_after_checkout(client, session_with_cart):
    """GET /api/orders/{session_id} must return the order after checkout."""
    # checkout ran in test_checkout_full_flow (same module-scoped session_with_cart)
    data = ok(await client.get(f"/api/orders/{session_with_cart}"))
    assert data["order_id"].startswith("ORD-")
    assert data["delivery_preference"] == "consolidated"
    assert "net_amount" in data
    assert data["net_amount"] >= 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_post_purchase_chat_blocked(client, session_with_cart):
    """After checkout, chat endpoint must refuse new messages."""
    # session_with_cart has purchase_confirmed=True at this point (after checkout test)
    data = ok(await client.post(
        f"/api/chat/{session_with_cart}",
        json={"message": "Başka bir indirim var mı?"},
    ))
    assert "tamamlandı" in data["response_text"].lower() or "sipariş" in data["response_text"].lower()
    assert data["agent_used"] == "orchestrator"
