"""Customer segmentation and memory helpers."""
from app.models.customer import Customer


QUOTA_BY_SEGMENT = {
    "new": 3,
    "loyal": 3,
    "bargain_hunter": 2,  # stricter quota for deal-seekers
}


def get_quota(segment: str) -> int:
    return QUOTA_BY_SEGMENT.get(segment, 3)


def remaining_quota(customer: Customer, quota_used: int) -> int:
    return max(get_quota(customer.segment) - quota_used, 0)


def format_history_for_prompt(history: list[dict]) -> str:
    if not history:
        return "Bu müşteriyle daha önce etkileşim yok."
    lines = []
    for h in history[-3:]:  # last 3 interactions
        lines.append(f"- {h.get('date', '?')}: {h.get('summary', '')}")
    return "\n".join(lines)
