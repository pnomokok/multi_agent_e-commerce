"""Orchestrator Agent — detects intent and routes to the right sub-agent."""
from app.agents.llm import call_gemini
from app.agents.prompts import (
    ORCHESTRATOR_SYSTEM,
    ORCHESTRATOR_USER_TEMPLATE,
    GREETING_RESPONSE,
    GREETING_RETURNING_SYSTEM,
    GREETING_RETURNING_USER_TEMPLATE,
)
from app.agents.state import AgentState
from app.services.segmentation import format_history_for_prompt


async def orchestrator_node(state: AgentState) -> dict:
    """Detect user intent. Returns updated state fields."""
    logs = state.get("agent_logs", [])
    logs.append({
        "timestamp": _ts(),
        "agent": "orchestrator",
        "action": "intent_detection → start",
        "payload": {"message": state["user_message"]},
    })

    result = {}
    intent = "general"
    confidence = 0.5

    try:
        result = await call_gemini(
            ORCHESTRATOR_SYSTEM,
            ORCHESTRATOR_USER_TEMPLATE.format(message=state["user_message"]),
        )
        intent = result.get("intent", "general")
        confidence = result.get("intent_confidence", result.get("confidence", 0.8))
    except Exception as e:
        result = {"error": str(e)}

    logs.append({
        "timestamp": _ts(),
        "agent": "orchestrator",
        "action": f"intent_detection → result: \"{intent}\" (confidence: {confidence:.2f})",
        "payload": result,
    })

    if intent == "greeting":
        greeting_text = await _build_greeting(state, logs)
        logs.append({
            "timestamp": _ts(),
            "agent": "orchestrator",
            "action": "routing → direct_response (greeting)",
            "payload": {},
        })
        return {
            "intent": intent,
            "intent_confidence": confidence,
            "response_text": greeting_text,
            "agent_used": "orchestrator",
            "agent_logs": logs,
        }

    return {
        "intent": intent,
        "intent_confidence": confidence,
        "agent_logs": logs,
    }


async def _build_greeting(state: AgentState, logs: list) -> str:
    """Return a personalized greeting for returning customers, static for new ones."""
    customer_data = state.get("customer_data", {})
    history = customer_data.get("interaction_history", [])

    if not history:
        return GREETING_RESPONSE

    customer_name = customer_data.get("name", "Müşterimiz")
    customer_memory = format_history_for_prompt(history)
    logs.append({
        "timestamp": _ts(),
        "agent": "orchestrator",
        "action": "greeting → personalized (returning customer)",
        "payload": {"name": customer_name},
    })
    try:
        res = await call_gemini(
            GREETING_RETURNING_SYSTEM,
            GREETING_RETURNING_USER_TEMPLATE.format(
                customer_name=customer_name,
                customer_memory=customer_memory,
                user_message=state["user_message"],
            ),
        )
        return res.get("response_text", GREETING_RESPONSE)
    except Exception:
        return GREETING_RESPONSE


def _ts() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%H:%M:%S")
