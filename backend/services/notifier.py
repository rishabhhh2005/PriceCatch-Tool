import asyncio, json, hmac, hashlib, httpx, logging
from datetime import datetime
from backend.database import SessionLocal
from backend.models import WebhookSubscription, NotificationLog

_queue = asyncio.Queue()

async def enqueue_price_change(product_id: int, old_price: float, new_price: float, product_url: str):
    """Put event onto queue. Non-blocking. Never raises."""
    await _queue.put({
        "product_id": product_id,
        "old_price": old_price,
        "new_price": new_price,
        "product_url": product_url,
        "event": "price_change",
        "timestamp": datetime.utcnow().isoformat(),
    })

def sign_payload(payload: str, secret: str) -> str:
    return hmac.new(secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()

async def delivery_worker():
    """
    Background task started on app startup.
    Drains the queue. For each event:
      1. Load active webhook_subscriptions from DB
      2. For each webhook: POST payload (HMAC signed if secret set)
      3. On failure: retry up to 3 times with exponential backoff (1s, 2s, 4s)
      4. Log result to notification_log table (status = delivered | failed)
    """
    async with httpx.AsyncClient() as client:
        while True:
            try:
                event = await _queue.get()
                
                db = SessionLocal()
                try:
                    webhooks = db.query(WebhookSubscription).filter(WebhookSubscription.is_active == True).all()
                    payload_str = json.dumps(event)

                    for webhook in webhooks:
                        asyncio.create_task(deliver_webhook(client, event, payload_str, webhook.id, webhook.url, webhook.secret))
                except Exception as e:
                    logging.error(f"Error processing webhook event: {e}")
                finally:
                    db.close()
                
                _queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Worker exception: {e}")

async def deliver_webhook(client, event, payload_str, webhook_id, url, secret):
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["X-Signature"] = sign_payload(payload_str, secret)
        
    status = "failed"
    attempts = 0
    delays = [1, 2, 4]
    
    for attempt in range(3):
        attempts += 1
        try:
            response = await client.post(url, content=payload_str, headers=headers, timeout=10)
            if 200 <= response.status_code < 300:
                status = "delivered"
                break
        except Exception:
            pass
            
        if attempt < 2:
            await asyncio.sleep(delays[attempt])

    # Log to DB
    db = SessionLocal()
    try:
        log_entry = NotificationLog(
            webhook_id=webhook_id,
            product_id=event["product_id"],
            old_price=event["old_price"],
            new_price=event["new_price"],
            payload=payload_str,
            status=status,
            attempts=attempts,
            last_attempt=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logging.error(f"Failed to save notification log: {e}")
    finally:
        db.close()
