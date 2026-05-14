# EKO Backend — Kurulum ve Çalıştırma

## Gereksinimler
- Python 3.11+
- Gemini API Key ([Google AI Studio](https://aistudio.google.com/))

## Kurulum

```bash
cd backend

# Virtual environment oluştur
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Bağımlılıkları yükle
pip install -e ".[dev]"

# .env dosyasını oluştur
copy .env.example .env
# .env dosyasını aç ve GEMINI_API_KEY değerini gir

# Veritabanını migrate et (opsiyonel — uygulama açılışta otomatik yapar)
alembic upgrade head

# Seed datayı yükle
python -m app.seed.seed_data

# Sunucuyu başlat
uvicorn app.main:app --reload --port 8000
```

## API Endpoint'leri

| Method | URL | Açıklama |
|--------|-----|----------|
| GET | /api/health | Sağlık kontrolü |
| GET | /api/products | Ürün listesi |
| GET | /api/personas | Müşteri persona listesi |
| POST | /api/session/start | Yeni oturum |
| GET | /api/session/{id} | Oturum durumu |
| POST | /api/cart/{id}/add | Sepete ekle |
| POST | /api/cart/{id}/remove | Sepetten çıkar |
| GET | /api/cart/{id} | Sepet detayı |
| POST | /api/chat/{id} | Eko ile konuş |
| POST | /api/checkout/{id} | Satın al |
| GET | /api/seller/{id}/dashboard | Satıcı dashboard |
| GET/PUT | /api/seller/{id}/policy | Pazarlık politikası |
| GET | /api/seller/{id}/stats | ROI istatistikleri |
| WS | /ws/logs/{session_id} | Canlı ajan logları |

Swagger UI: http://localhost:8000/docs

## Testler

```bash
pytest tests/ -v
```
