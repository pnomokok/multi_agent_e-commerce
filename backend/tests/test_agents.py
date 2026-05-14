"""Mock-based tests for orchestrator intent detection and graph routing."""
import pytest
from unittest.mock import AsyncMock, patch

from app.agents.orchestrator import orchestrator_node
from app.agents.graph import route_after_orchestrator
from langgraph.graph import END


# ---------------------------------------------------------------------------
# Minimal AgentState for testing (only required fields)
# ---------------------------------------------------------------------------

def _make_state(message: str, **overrides) -> dict:
    base = {
        "session_id": "test-session",
        "customer_id": "cust-1",
        "seller_id": "seller-1",
        "user_message": message,
        "cart_items": [{"product_id": "p1", "quantity": 1}],
        "cart_total": 1000.0,
        "intent": "",
        "intent_confidence": 0.0,
        "negotiation_history": [],
        "final_discount": 0.0,
        "final_gifts": [],
        "negotiation_quota_used": 0,
        "customer_segment": "new",
        "purchase_confirmed": False,
        "delivery_preference": "express",
        "carbon_saved_kg": 0.0,
        "response_text": "",
        "agent_used": "",
        "offer_details": None,
        "carbon_data": None,
        "agent_logs": [],
        "product_data": {},
        "customer_data": {},
        "delivery_data": {},
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Orchestrator intent detection tests (Gemini is mocked)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_orchestrator_detects_price_objection():
    mock_response = {"intent": "price_objection", "confidence": 0.95, "user_message_summary": "Pahalı"}
    with patch("app.agents.orchestrator.call_gemini", new=AsyncMock(return_value=mock_response)):
        result = await orchestrator_node(_make_state("Bu ürünler çok pahalı, indirim yapabilir misiniz?"))

    assert result["intent"] == "price_objection"
    assert result["intent_confidence"] >= 0.9
    assert "response_text" not in result or result.get("agent_used") != "orchestrator"


@pytest.mark.asyncio
async def test_orchestrator_detects_purchase_decision():
    mock_response = {"intent": "purchase_decision", "confidence": 0.9, "user_message_summary": "Satın alıyorum"}
    with patch("app.agents.orchestrator.call_gemini", new=AsyncMock(return_value=mock_response)):
        result = await orchestrator_node(_make_state("Tamam, satın alıyorum!"))

    assert result["intent"] == "purchase_decision"


@pytest.mark.asyncio
async def test_orchestrator_detects_greeting_and_responds_directly():
    mock_response = {"intent": "greeting", "confidence": 0.99, "user_message_summary": "Merhaba"}
    with patch("app.agents.orchestrator.call_gemini", new=AsyncMock(return_value=mock_response)):
        result = await orchestrator_node(_make_state("Merhaba!"))

    assert result["intent"] == "greeting"
    assert result["agent_used"] == "orchestrator"
    # Greeting should produce a response directly — no further routing needed
    assert len(result.get("response_text", "")) > 0


@pytest.mark.asyncio
async def test_orchestrator_detects_delivery_consolidated():
    mock_response = {"intent": "delivery_choice_consolidated", "confidence": 0.88, "user_message_summary": "Konsolide"}
    with patch("app.agents.orchestrator.call_gemini", new=AsyncMock(return_value=mock_response)):
        result = await orchestrator_node(_make_state("Konsolide teslimatı seçiyorum, bekleyebilirim."))

    assert result["intent"] == "delivery_choice_consolidated"


@pytest.mark.asyncio
async def test_orchestrator_falls_back_on_llm_error():
    with patch("app.agents.orchestrator.call_gemini", new=AsyncMock(side_effect=Exception("503"))):
        result = await orchestrator_node(_make_state("Bir şey sormak istiyorum"))

    # Must not raise — should degrade to "general" with low confidence
    assert result["intent"] == "general"
    assert result["intent_confidence"] <= 0.5


@pytest.mark.asyncio
async def test_orchestrator_logs_are_populated():
    mock_response = {"intent": "general", "confidence": 0.7, "user_message_summary": "Soru"}
    with patch("app.agents.orchestrator.call_gemini", new=AsyncMock(return_value=mock_response)):
        result = await orchestrator_node(_make_state("Sorum var"))

    assert len(result["agent_logs"]) >= 2
    agents = {log["agent"] for log in result["agent_logs"]}
    assert "orchestrator" in agents


# ---------------------------------------------------------------------------
# Graph routing tests (no LLM calls — pure state inspection)
# ---------------------------------------------------------------------------

def test_route_price_objection_goes_to_negotiator():
    state = _make_state("", intent="price_objection")
    assert route_after_orchestrator(state) == "negotiator"


def test_route_purchase_decision_goes_to_logistics():
    state = _make_state("", intent="purchase_decision")
    assert route_after_orchestrator(state) == "logistics"


def test_route_delivery_consolidated_goes_to_delivery_choice():
    state = _make_state("", intent="delivery_choice_consolidated")
    assert route_after_orchestrator(state) == "delivery_choice"


def test_route_delivery_express_goes_to_delivery_choice():
    state = _make_state("", intent="delivery_choice_express")
    assert route_after_orchestrator(state) == "delivery_choice"


def test_route_general_goes_to_general_node():
    state = _make_state("", intent="general")
    assert route_after_orchestrator(state) == "general"


def test_route_ends_when_orchestrator_already_responded():
    state = _make_state("", intent="greeting", agent_used="orchestrator", response_text="Merhaba!")
    assert route_after_orchestrator(state) == END
