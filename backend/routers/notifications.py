from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_session
from backend.models import WebhookSubscription, NotificationLog
from backend.schemas import WebhookCreate, WebhookResponse, NotificationLogResponse
from backend.auth import require_api_key

notifications_router = APIRouter(dependencies=[Depends(require_api_key)])

@notifications_router.post("/webhooks", response_model=WebhookResponse)
async def create_webhook(webhook: WebhookCreate, session: Session = Depends(get_session)):
    existing = session.query(WebhookSubscription).filter(WebhookSubscription.url == str(webhook.url)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Webhook URL already registered")
        
    db_webhook = WebhookSubscription(url=str(webhook.url), secret=webhook.secret)
    session.add(db_webhook)
    session.commit()
    session.refresh(db_webhook)
    return db_webhook

@notifications_router.get("/webhooks", response_model=List[WebhookResponse])
async def get_webhooks(session: Session = Depends(get_session)):
    return session.query(WebhookSubscription).filter(WebhookSubscription.is_active == True).all()

@notifications_router.delete("/webhooks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(id: int, session: Session = Depends(get_session)):
    webhook = session.query(WebhookSubscription).filter(WebhookSubscription.id == id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    session.delete(webhook)
    session.commit()
    return None

@notifications_router.get("/webhooks/log", response_model=List[NotificationLogResponse])
async def get_webhook_logs(limit: int = Query(20, ge=1, le=100), session: Session = Depends(get_session)):
    return session.query(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(limit).all()
