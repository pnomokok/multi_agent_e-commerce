from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="EKO — Akıllı Sepet Asistanı API",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from app.api import products, cart, chat, checkout, seller, ws_logs  # noqa: E402

app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(cart.router, prefix="/api", tags=["cart"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(checkout.router, prefix="/api", tags=["checkout"])
app.include_router(seller.router, prefix="/api", tags=["seller"])
app.include_router(ws_logs.router, tags=["websocket"])


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "service": "eko-backend"}
