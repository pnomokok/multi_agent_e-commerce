"""Negotiator Agent — conducts price negotiations within seller policy."""
import json

from app.agents.data_agent import check_negotiation_quota, calculate_max_cart_discount
from app.agents.llm import call_gemini
from app.agents.prompts import NEGOTIATOR_SYSTEM, NEGOTIATOR_USER_TEMPLATE
from app.agents.state import AgentState
from app.services.segmentation import format_history_for_prompt


async def negotiator_node(state: AgentState) -> dict:
    logs = list(state.get("agent_logs", []))
    logs.append({
        "timestamp": _ts(),
        "agent": "orchestrator",
        "action": "routing → Pazarlık Ajanı",
        "payload": {},
    })

    customer_data = state.get("customer_data", {})
    seller_data = state.get("product_data", {}).get("_seller", {})
    cart_products = {
        k: v for k, v in state.get("product_data", {}).items() if not k.startswith("_")
    }

    quota_remaining = check_negotiation_quota(customer_data, state.get("negotiation_quota_used", 0))

    logs.append({
        "timestamp": _ts(),
        "agent": "negotiator",
        "action": "data_agent → get_product_data",
        "payload": {pid: {"base_price": p.get("base_price"), "margin": p.get("margin"), "stock": p.get("stock")}
                    for pid, p in cart_products.items()},
    })
    logs.append({
        "timestamp": _ts(),
        "agent": "data",
        "action": "response → customer_segment",
        "payload": {"segment": customer_data.get("segment")},
    })

    # Hafıza: müşteri geçmişini çek
    interaction_history = customer_data.get("interaction_history", [])
    customer_memory = format_history_for_prompt(interaction_history)
    logs.append({
        "timestamp": _ts(),
        "agent": "negotiator",
        "action": "data_agent → get_customer_history",
        "payload": {"history_entries": len(interaction_history), "memory": customer_memory},
    })

    # Quota exhausted
    if quota_remaining <= 0:
        resp = (
            "Pazarlık limitine ulaştık maalesef. "
            "Bu sipariş için daha fazla indirim yapamıyorum, ama harika bir ürün aldığınızdan eminim!"
        )
        logs.append({
            "timestamp": _ts(),
            "agent": "negotiator",
            "action": "quota_exhausted → direct_response",
            "payload": {},
        })
        return {
            "response_text": resp,
            "agent_used": "negotiator",
            "offer_details": None,
            "agent_logs": logs,
        }

    # Build seller data reference
    seller_min_margin = (state.get("product_data", {}).get("_seller") or {}).get("min_margin_target", 0.12)
    budget_remaining = (state.get("product_data", {}).get("_seller") or {}).get("budget_remaining", 9999.0)
    max_discount = calculate_max_cart_discount(cart_products, seller_min_margin, budget_remaining)

    # Format negotiation history
    history = state.get("negotiation_history", [])
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in history[-4:]
    ) if history else "Henüz pazarlık geçmişi yok."

    user_content = NEGOTIATOR_USER_TEMPLATE.format(
        customer_segment=customer_data.get("segment", "new"),
        quota_remaining=quota_remaining,
        customer_memory=customer_memory,
        product_data_json=json.dumps(list(cart_products.values()), ensure_ascii=False, indent=2),
        cart_total=state.get("cart_total", 0.0),
        max_discount=max_discount,
        negotiation_history=history_text,
        user_message=state["user_message"],
    )

    try:
        result = await call_gemini(NEGOTIATOR_SYSTEM, user_content)
    except Exception as e:
        result = {
            "response_text": "Şu an bir teknik sorun yaşıyorum, lütfen biraz sonra tekrar deneyin.",
            "offered_discount_amount": 0.0,
            "offered_gifts": [],
            "free_shipping": False,
            "is_final_offer": False,
            "internal_reasoning": str(e),
        }

    logs.append({
        "timestamp": _ts(),
        "agent": "negotiator",
        "action": f"karar: indirim {result.get('offered_discount_amount', 0)} TL"
                  + (f" + hediye {result.get('offered_gifts')}" if result.get("offered_gifts") else "")
                  + (" + ücretsiz kargo" if result.get("free_shipping") else ""),
        "payload": {"internal_reasoning": result.get("internal_reasoning", "")},
    })
    logs.append({
        "timestamp": _ts(),
        "agent": "negotiator",
        "action": "Eko → response_ready",
        "payload": {},
    })

    cart_total = state.get("cart_total", 0.0)
    discount = result.get("offered_discount_amount", 0.0)
    offer_details = {
        "original_price": cart_total,
        "offered_price": round(cart_total - discount, 2),
        "discount_amount": discount,
        "gifts": result.get("offered_gifts", []),
        "free_shipping": result.get("free_shipping", False),
        "is_final": result.get("is_final_offer", False),
    }

    # Append to negotiation history
    new_history = list(history) + [
        {"role": "customer", "content": state["user_message"]},
        {"role": "eko", "content": result.get("response_text", "")},
    ]

    return {
        "response_text": result.get("response_text", ""),
        "agent_used": "negotiator",
        "offer_details": offer_details,
        "negotiation_history": new_history,
        "final_discount": discount,
        "final_gifts": result.get("offered_gifts", []),
        "negotiation_quota_used": state.get("negotiation_quota_used", 0) + 1,
        "agent_logs": logs,
    }


def _ts() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%H:%M:%S")
