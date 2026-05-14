"""Verify the 3 fixes with real Gemini calls."""
import asyncio
import httpx
import sys

sys.path.insert(0, ".")
from app.main import app

BASE = "http://test"

PERSONAS = [
    ("customer-ayse-01",   "Ayse  (new)"),
    ("customer-mehmet-02", "Mehmet (loyal/eco)"),
    ("customer-can-03",    "Can    (bargain_hunter)"),
]
PRODUCTS = ["prod-kulaklık-01", "prod-klavye-02"]


def section(title):
    print("\n" + "=" * 70)
    print("  " + title)
    print("=" * 70)


async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE, timeout=60) as c:

        # setup sessions with cart
        sessions = {}
        for pid, _ in PERSONAS:
            r = (await c.post("/api/session/start", json={"customer_id": pid})).json()
            sid = r["session_id"]
            for prod in PRODUCTS:
                await c.post(f"/api/cart/{sid}/add",
                             json={"product_id": prod, "quantity": 1})
            sessions[pid] = sid

        # ── FIX 1: Greeting kişiselleştirme ──────────────────────────────────
        section("FIX 1 — GREETING KISISELLESME")
        for pid, label in PERSONAS:
            r = (await c.post(
                f"/api/chat/{sessions[pid]}",
                json={"message": "Merhaba, nasılsın?"},
            )).json()
            txt = r["response_text"]
            print(f"\n[{label}]")
            print(f"  {txt}")

        await asyncio.sleep(1)

        # ── FIX 2: Agresif pazarlığa temkinli ilk yanıt ───────────────────────
        section("FIX 2 — AGRESIF PAZARLIK (ilk tur)")
        for pid, label in PERSONAS:
            r = (await c.post(
                f"/api/chat/{sessions[pid]}",
                json={"message": "Yuzde 30 indirim istiyorum, yoksa almiyorum."},
            )).json()
            offer = r.get("offer_details") or {}
            disc = offer.get("discount_amount", "?")
            is_fin = offer.get("is_final", "?")
            txt = r["response_text"]
            print(f"\n[{label}]  indirim={disc} TL  is_final={is_fin}")
            print(f"  {txt[:220]}")

        await asyncio.sleep(1)

        # ── FIX 3: Ürün sorusu — ürün datası ile ─────────────────────────────
        section("FIX 3 — URUN SORUSU (urun datasi inject)")
        for pid, label in PERSONAS:
            r = (await c.post(
                f"/api/chat/{sessions[pid]}",
                json={"message": "Sony kulaklık gurultu engellemesi nasil, bana deger mi?"},
            )).json()
            txt = r["response_text"]
            print(f"\n[{label}]")
            print(f"  {txt}")


if __name__ == "__main__":
    asyncio.run(main())
