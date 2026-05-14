"""Green Logistics Agent — offers consolidated delivery with carbon savings."""
from app.agents.llm import call_gemini
from app.agents.prompts import LOGISTICS_SYSTEM, LOGISTICS_USER_TEMPLATE
from app.agents.state import AgentState
from app.services.segmentation import format_history_for_prompt


async def logistics_node(state: AgentState) -> dict:
    logs = list(state.get("agent_logs", []))
    logs.append({
        "timestamp": _ts(),
        "agent": "orchestrator",
        "action": "routing → Yeşil Lojistik Ajanı",
        "payload": {},
    })

    delivery = state.get("delivery_data", {})
    logs.append({
        "timestamp": _ts(),
        "agent": "logistics",
        "action": "data_agent → get_delivery_data",
        "payload": delivery,
    })

    # Hafıza: müşteri geçmişini çek
    customer_data = state.get("customer_data", {})
    interaction_history = customer_data.get("interaction_history", [])
    customer_memory = format_history_for_prompt(interaction_history)
    logs.append({
        "timestamp": _ts(),
        "agent": "logistics",
        "action": "data_agent → get_customer_history",
        "payload": {"history_entries": len(interaction_history), "memory": customer_memory},
    })

    user_content = LOGISTICS_USER_TEMPLATE.format(
        customer_memory=customer_memory,
        express_date=delivery.get("express_date", "Yarın"),
        consolidated_date=delivery.get("consolidated_date", "4 gün sonra"),
        discount_amount=delivery.get("discount_amount", 30),
        co2_saved_kg=delivery.get("co2_saved_kg", 0.5),
        tree_equivalent=delivery.get("tree_equivalent", ""),
    )

    try:
        result = await call_gemini(LOGISTICS_SYSTEM, user_content)
    except Exception as e:
        result = {
            "response_text": (
                f"Harika haber! Siparişinizi birkaç gün erteleyerek "
                f"{delivery.get('discount_amount', 30):.0f} TL indirim kazanabilir, "
                f"aynı zamanda {delivery.get('co2_saved_kg', 0.5):.2f} kg CO₂ tasarrufu sağlayabilirsiniz. "
                f"İsterseniz standart teslimatla da devam edebilirsiniz."
            ),
            "discount_amount": delivery.get("discount_amount", 30),
            "co2_saved_kg": delivery.get("co2_saved_kg", 0.5),
            "tree_equivalent": delivery.get("tree_equivalent", ""),
            "alternative_offered": True,
        }

    logs.append({
        "timestamp": _ts(),
        "agent": "logistics",
        "action": f"teklif: {result.get('discount_amount')} TL indirim + {result.get('co2_saved_kg')} kg CO₂ tasarrufu",
        "payload": {},
    })
    logs.append({
        "timestamp": _ts(),
        "agent": "logistics",
        "action": "Eko → response_ready",
        "payload": {},
    })

    carbon_data = {
        "co2_saved_kg": result.get("co2_saved_kg", delivery.get("co2_saved_kg", 0.0)),
        "discount_amount": result.get("discount_amount", delivery.get("discount_amount", 0.0)),
        "express_date": delivery.get("express_date", ""),
        "consolidated_date": delivery.get("consolidated_date", ""),
        "tree_equivalent": result.get("tree_equivalent", delivery.get("tree_equivalent", "")),
    }

    return {
        "response_text": result.get("response_text", ""),
        "agent_used": "logistics",
        "carbon_data": carbon_data,
        "carbon_saved_kg": carbon_data["co2_saved_kg"],
        "purchase_confirmed": True,
        "delivery_preference": "pending_customer_choice",
        "agent_logs": logs,
    }


def _ts() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%H:%M:%S")
