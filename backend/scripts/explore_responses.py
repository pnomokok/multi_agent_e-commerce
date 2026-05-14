"""
Manual exploration script — sends the same messages to 3 personas and prints
the full Eko responses so we can compare behavior.

Run from the backend directory:
  python scripts/explore_responses.py
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx
from app.main import app

BASE = "http://test"

PERSONAS = [
    {"id": "customer-ayse-01",  "label": "Ayşe  (new)"},
    {"id": "customer-mehmet-02","label": "Mehmet (loyal / eco)"},
    {"id": "customer-can-03",   "label": "Can    (bargain_hunter)"},
]

PRODUCTS = ["prod-kulaklık-01", "prod-klavye-02"]  # 3499 + 1899 = 5398 TL

SCENARIOS = [
    ("GREETING",               "Merhaba! Ne yapabilirsin?"),
    ("PAZARLIK -- sert",       "Bu fiyatlar cok fazla, yuzde 30 indirim istiyorum yoksa almiyorum."),
    ("PAZARLIK -- nazik",      "Butcem biraz sinirli, kucuk bir indirim mumkun mu?"),
    ("SATIN ALMA KARARI",      "Tamam anlastik, satin aliyorum!"),
    ("YESIL TESLIMAT -- kabul","Konsolide teslimatı seciyorum, bekleyebilirim."),
    ("URUN SORUSU",            "Sony kulaklık gurultu engellemesi gercekten iyi mi?"),
]


async def run():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE, timeout=60) as client:

        # ── setup: create a session with cart for each persona ────────────────
        sessions = {}
        for p in PERSONAS:
            r = await client.post("/api/session/start", json={"customer_id": p["id"]})
            sid = r.json()["session_id"]
            for pid in PRODUCTS:
                await client.post(f"/api/cart/{sid}/add",
                                  json={"product_id": pid, "quantity": 1})
            sessions[p["id"]] = sid

        # ── run scenarios ─────────────────────────────────────────────────────
        for label, message in SCENARIOS:
            print(f"\n{'='*80}")
            print(f"  {label}")
            print(f"  Mesaj: \"{message}\"")
            print(f"{'='*80}")

            for p in PERSONAS:
                sid = sessions[p["id"]]
                r = await client.post(f"/api/chat/{sid}", json={"message": message})
                data = r.json()
                agent = data.get("agent_used", "?")
                text  = data.get("response_text", "")
                offer = data.get("offer_details")
                carbon = data.get("carbon_data")
                logs  = data.get("agent_logs", [])
                intents = [l["action"] for l in logs if "intent_detection" in l.get("action","")]

                print(f"\n  [{p['label']}]  → agent: {agent}")
                if intents:
                    print(f"  Intent: {intents[-1] if intents else '–'}")
                print(f"  Yanıt: {text}")
                if offer:
                    print(f"  Teklif: {json.dumps(offer, ensure_ascii=False, indent=2)}")
                if carbon:
                    print(f"  Karbon: {json.dumps(carbon, ensure_ascii=False)}")

            # small pause to avoid hammering Gemini
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run())
