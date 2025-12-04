# seferal
SEFERAI – Product Requirements Document (PRD)
📌 1. Ürün Tanımı

SeferAI, kullanıcıların sohbet arayüzü üzerinden otobüs bileti, uçak bileti ve ilerleyen sürümlerde otel, araç kiralama ve tatil planlama işlemlerini yapmasını sağlayan bir yapay zeka asistanıdır.

Kullanıcı doğal dilde sorular sorar:

“18 Aralık Denizli → İstanbul otobüs bileti var mı?”

“3 kişiyiz, 2 yan yana 1 tekli koltuk için İzmir Ankara’ya bak.”

“En ucuz hangisi?”

“Pamukkale firmasında boş koltuk var mı?”

Arka planda sistem:

NLP ile soruyu analiz eder

Uygun scraping işlemlerini başlatır

Sonuçları kullanıcıya okunmuş & filtrelenmiş şekilde döndürür

📌 2. Kullanıcı Senaryoları (User Stories)
🧍‍♂ 2.1. Bilet Arama

Kullanıcı → “18 Aralık Ankara İstanbul arası bilet var mı?”

NLP → (tarih, nereden, nereye)

Cache kontrolü → yoksa Selenium scraping

Sonuçları döndür

🧍‍♂ 2.2. Fiyat Sorma

Kullanıcı → “En ucuz hangisi?”

Daha önceki sonuçlardan fiyat karşılaştırması yapılır (cache)

🧍‍♂ 2.3. Firma Bazlı Sorgu

Kullanıcı → “Pamukkale’de var mı?”

Cache'den filtrelenir

🧍‍♂ 2.4. Koltuk Tercihi

Kullanıcı → “3 kişiyiz, 2 yan yana 1 tekli olsun”

Seat map → filtre → öneri

🧍‍♂ 2.5. Tarih/rota değişikliği

Kullanıcı → “O zaman yarına bak”

Yeni scraping tetiklenir

🧍‍♂ 2.6. Tatil planlama (V2)

Kullanıcı → “3 günlük Antalya tatili planla. Otel + uçak + aktiviteler.”

📌 3. Gereksinimler (Requirements)
3.1. Fonksiyonel Gereksinimler

 Otobüs firmalarından scraping (Metro, Pamukkale, Kamilkoç, Sarıkız…)

 Her sorguda NLP parse

 Redis caching ile hızlı yanıt

 MCP backend ile ChatGPT tarzı front-end entegrasyonu

 Multi-session chat context yönetimi

 Selenium scraping

 Anti-bot önlemleri

 Fiyat filtreleme, firma filtreleme, koltuk analizi

3.2. Teknik Gereksinimler

Selenium → Headless Chrome

Rotating proxy (later optional)

Redis cache (10–20 dk)

FastAPI → MCP tools

NLP → Gemini API

Docker deployment

Async scraper çalıştırma

Her scraper kendi konteyner içinde çalışabilir (scalable mimari)

3.3. NLP Gereksinimleri

Tarih parse

Lokasyon/rota çıkarımı

Kişi sayısı parse

Seat preference parse

Firma tercihleri

Delivery: structured JSON

📌 4. Sistem Mimarisi
           ┌────────────────────────────────────┐
           │              FRONTEND               │
           │   React Chat Clone (MCP Client)     │
           └────────────────────────────────────┘
                             │
                             ▼
                 (MCP Tool: /bus.search)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                    │
│                                                             │
│  ┌────────────┐   ┌─────────────────┐   ┌────────────────┐ │
│  │   NLP       │→ │  Cache Layer    │→ │  Scraper Manager │ │
│  │ (Gemini)    │   │ (Redis)         │   │ (Async Selenium)│ │
│  └────────────┘   └─────────────────┘   └────────────────┘ │
│               │         ▲                   ▲               │
│               ▼         │                   │               │
│         Business Logic Layer (Filters, Ranking, Merging)    │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
           ┌────────────────────────────────────┐
           │      ChatGPT-like final answer     │
           └────────────────────────────────────┘

📌 5. Teknolojiler (Stack)
🐍 Backend

Python 3.12

FastAPI → API & MCP Tool

Selenium → Otobüs siteleri scrape

undetected-chromedriver (opsiyonel)

Redis → Cache

Gemini API → NLP

Pydantic → Models

Celery or multiprocessing (opsiyonel async scraping)

🖥 Frontend

React

Tailwind

MCP Client

ChatGPT UI Clone

🗄 Altyapı & DevOps

Docker

Docker Compose

Nginx (opsiyonel)

CI/CD (GitHub Actions)

📌 6. MVP – Minimum Viable Product
MVP’de olacaklar

 Chat ekranı

 NLP parsing

 2–3 otobüs firmasından scraping

 Cache mekanizması

 Fiyat karşılaştırması

 Firma bazlı filtre

 Seat map analiz (basic)


 backend/
│
├── main.py
├── requirements.txt
├── dockerfile
├── app/
│   ├── mcp/
│   │    ├── bus_tool.py
│   │    ├── hotels_tool.py (future)
│   │    └── flights_tool.py (future)
│   ├── nlp/
│   │    ├── parser.py
│   │    └── gemini_client.py
│   ├── scraper/
│   │    ├── base.py
│   │    ├── metro.py
│   │    ├── pamukkale.py
│   │    ├── kamilkoc.py
│   │    └── sarikiz.py
│   ├── cache/
│   │    └── redis_client.py
│   ├── models/
│   │    ├── trip.py
│   │    └── seat.py
│   ├── logic/
│   │    ├── merger.py
│   │    ├── filters.py
│   │    └── ranking.py
│   └── utils/
│        ├── date.py
│        └── location.py
