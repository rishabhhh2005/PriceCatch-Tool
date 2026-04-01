# PriceCatch

Product Price Monitoring System for luxury fashion marketplaces (Grailed, Fashionphile, 1stdibs).

---

## Overview

PriceCatch is a product price monitoring system designed to track listings across multiple luxury marketplaces such as Grailed, Fashionphile, and 1stdibs.

The system collects product data from different sources, normalizes it into a unified format, and stores both the current state and historical price changes. It allows users to monitor how product prices evolve over time and detect significant changes.

Key capabilities include:

* Aggregating product data from multiple sources
* Tracking price history over time
* Detecting price changes during refresh cycles
* Providing analytics such as average prices by category and source
* Supporting webhook notifications for price change events

This project focuses on building a reliable backend system with clean API design, along with a simple dashboard to visualize product data.

---

## Setup & Run

```
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn backend.main:app --reload --port 8000
```

Open:
http://localhost:8000
Dashboard will load automatically.

---

## Load Initial Data

```
curl -X POST http://localhost:8000/api/refresh \
  -H "X-API-Key: dev-key-12345"
```

Or click **Refresh Data** in dashboard.

---

## Run Tests

```
pytest tests/ -v
```

---

## API Documentation

All endpoints require header:

```
X-API-Key: dev-key-12345
```

---

### POST /api/refresh

Triggers ingestion of JSON data.

Response:

```
{
  "inserted": 90,
  "updated": 0,
  "price_changes": 0,
  "errors": 0
}
```

---

### GET /api/products

Browse products with filters.

Query params:

* source
* category
* brand
* min_price
* max_price
* available_only (default: true)
* page (default: 1)
* page_size (default: 20, max: 100)

Example:

```
curl "http://localhost:8000/api/products?source=grailed&min_price=200" \
  -H "X-API-Key: dev-key-12345"
```

Response:

```
{
  "items": [
    {
      "id": 1,
      "brand": "amiri",
      "current_price": 425.0,
      "source": "grailed"
    }
  ],
  "total": 30,
  "page": 1,
  "pages": 2
}
```

---

### GET /api/products/{id}

Get full product details + price history.

```
curl http://localhost:8000/api/products/1 \
  -H "X-API-Key: dev-key-12345"
```

---

### GET /api/products/{id}/price-history

Query param:

* limit (default: 50)

---

### GET /api/analytics/summary

Response:

```
{
  "total_products": 90,
  "by_source": {
    "grailed": 30,
    "fashionphile": 30,
    "1stdibs": 30
  },
  "by_category": {
    "apparel": 30,
    "jewelry": 30,
    "belts": 30
  },
  "avg_price_by_source": {
    "grailed": 425.0,
    "fashionphile": 1200.0,
    "1stdibs": 2500.0
  },
  "avg_price_by_category": {
    "apparel": 425.0
  },
  "price_changes_last_24h": 0,
  "total_price_history_records": 90
}
```

---

### POST /api/webhooks

```
curl -X POST http://localhost:8000/api/webhooks \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yoursite.com/hook", "secret": "optional-hmac-secret"}'
```

---

### GET /api/webhooks

List active webhooks

### DELETE /api/webhooks/{id}

Remove webhook

### GET /api/webhooks/log

Recent delivery logs

---

### POST /api/auth/keys

```
curl -X POST http://localhost:8000/api/auth/keys \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-app-key"}'
```

---

## Design Decisions

### Price History Scaling

* Append-only table used
* Indexed by (product_id, recorded_at)
* Scales well for large datasets

Future improvements:

* Time-based partitioning
* Archive old data
* Materialized views for faster queries

---

### Notification System

* Uses in-memory async queue
* Background worker sends webhook requests
* Retries with exponential backoff
* Logs every attempt

Trade-off:

* Events lost if server crashes
* Production should use Redis or DB-based queue

---

### Extending to 100+ Sources

* Each source = separate parser
* Easy to add new sources
* No major code changes required
* Async processing allows parallel ingestion

---

## Known Limitations

* Uses static JSON (no real scraping)
* In-memory queue (not persistent)
* SQLite has limited concurrency
* No API rate limiting
* API keys cannot be recovered
* Filters are case-sensitive

## Final Notes
Project completed and ready for Entrupy evaluation.
Made by Rishabh Puri