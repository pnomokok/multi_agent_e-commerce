"""LangGraph state graph — wires all agents together."""
from langgraph.graph import END, StateGraph

from app.agents.state import AgentState
from app.agents.orchestrator import orchestrator_node
from app.agents.negotiator import negotiator_node
from app.agents.logistics import logistics_node
from app.agents.llm import call_gemini
from app.agents.prompts import (
    GENERAL_RESPONSE_SYSTEM,
    GENERAL_WITH_PRODUCTS_SYSTEM,
    GENERAL_WITH_PRODUCTS_USER_TEMPLATE,
)


async def delivery_choice_node(state: AgentState) -> dict:
    """Saves delivery preference and confirms to the user."""
    intent = state.get("intent", "")
    is_consolidated = intent == "delivery_choice_consolidated"
    preference = "consolidated" if is_consolidated else "express"

    logs = list(state.get("agent_logs", []))
    logs.append({
        "timestamp": _ts(),
        "agent": "orchestrator",
        "action": f"routing → delivery_choice ({preference})",
        "payload": {},
    })

    if is_consolidated:
        carbon = state.get("carbon_saved_kg", 0.0)
        delivery_data = state.get("delivery_data", {})
        discount = delivery_data.get("discount_amount", 0)
        new_final_discount = round(state.get("final_discount", 0.0) + discount, 2)
        text = (
            f"Harika tercih! Konsolide teslimatı seçtiniz. "
            f"{discount:.0f} TL indiriminiz sepetinize uygulandı ve "
            f"{carbon:.2f} kg CO₂ tasarrufu sağladınız. "
            f"Siparişiniz {delivery_data.get('consolidated_date', 'birkaç gün içinde')} teslim edilecek."
        )
        return {
            "response_text": text,
            "agent_used": "logistics",
            "delivery_preference": preference,
            "final_discount": new_final_discount,
            "agent_logs": logs,
        }
    else:
        text = (
            "Standart teslimatı seçtiniz. "
            "Siparişiniz yarın kapınızda olacak. İyi alışveriler!"
        )

    return {
        "response_text": text,
        "agent_used": "logistics",
        "delivery_preference": preference,
        "agent_logs": logs,
    }


async def general_node(state: AgentState) -> dict:
    """Fallback: orchestrator handles general/unknown intents directly."""
    logs = list(state.get("agent_logs", []))
    logs.append({
        "timestamp": _ts(),
        "agent": "orchestrator",
        "action": "routing → direct_response (general)",
        "payload": {},
    })

    product_data = state.get("product_data", {})
    cart_items = state.get("cart_items", [])

    # Build a concise product summary for items actually in the cart
    product_lines = []
    for item in cart_items:
        pid = item.get("product_id", "")
        p = product_data.get(pid)
        if p:
            product_lines.append(
                f"- {p.get('name', pid)} | Fiyat: {p.get('list_price', '?')} TL"
                f" | Kategori: {p.get('category', '?')}"
            )

    try:
        if product_lines:
            product_summary = "\n".join(product_lines)
            result = await call_gemini(
                GENERAL_WITH_PRODUCTS_SYSTEM,
                GENERAL_WITH_PRODUCTS_USER_TEMPLATE.format(
                    product_summary=product_summary,
                    user_message=state["user_message"],
                ),
            )
        else:
            result = await call_gemini(
                GENERAL_RESPONSE_SYSTEM,
                f"Müşteri mesajı: \"{state['user_message']}\"",
            )
        text = result.get("response_text", "Size nasıl yardımcı olabileceğimi biraz daha açar mısınız?")
    except Exception:
        text = "Size nasıl yardımcı olabileceğimi biraz daha açar mısınız?"

    return {
        "response_text": text,
        "agent_used": "orchestrator",
        "agent_logs": logs,
    }


def route_after_orchestrator(state: AgentState) -> str:
    intent = state.get("intent", "general")
    if state.get("agent_used") == "orchestrator" and state.get("response_text"):
        # orchestrator already produced a response (e.g. greeting)
        return END
    if intent == "price_objection":
        return "negotiator"
    if intent == "purchase_decision":
        return "logistics"
    if intent in ("delivery_choice_consolidated", "delivery_choice_express"):
        return "delivery_choice"
    return "general"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("negotiator", negotiator_node)
    graph.add_node("logistics", logistics_node)
    graph.add_node("delivery_choice", delivery_choice_node)
    graph.add_node("general", general_node)

    graph.set_entry_point("orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "negotiator": "negotiator",
            "logistics": "logistics",
            "delivery_choice": "delivery_choice",
            "general": "general",
            END: END,
        },
    )

    graph.add_edge("negotiator", END)
    graph.add_edge("logistics", END)
    graph.add_edge("delivery_choice", END)
    graph.add_edge("general", END)

    return graph.compile()


# Singleton compiled graph
eko_graph = build_graph()


def _ts() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%H:%M:%S")
