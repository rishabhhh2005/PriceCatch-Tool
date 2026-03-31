from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.database import get_session
from backend.models import Product, PriceHistory
from backend.schemas import AnalyticsSummary
from backend.auth import require_api_key

analytics_router = APIRouter(dependencies=[Depends(require_api_key)])

@analytics_router.get("/analytics/summary", response_model=AnalyticsSummary)
async def get_summary(session: Session = Depends(get_session)):
    total_products = session.query(Product).count()
    
    # By source
    sources = session.query(Product.source, func.count(Product.id)).group_by(Product.source).all()
    by_source = {s: c for s, c in sources}
    
    # By category
    categories = session.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
    by_category = {c or "unknown": count for c, count in categories}
    
    # Avg price by source
    avg_price_source = session.query(Product.source, func.avg(Product.current_price)).group_by(Product.source).all()
    avg_price_by_source = {s: round(a, 2) for s, a in avg_price_source if a is not None}
    
    # Avg price by category
    avg_price_category = session.query(Product.category, func.avg(Product.current_price)).group_by(Product.category).all()
    avg_price_by_category = {c or "unknown": round(a, 2) for c, a in avg_price_category if a is not None}
    
    # Price changes last 24h
    yesterday = datetime.utcnow() - timedelta(days=1)
    # We count history records that are not the first insert. Simple approximation:
    # Just count price history rows in last 24h.
    price_changes_last_24h = session.query(PriceHistory).filter(PriceHistory.recorded_at >= yesterday).count()
    
    total_price_history_records = session.query(PriceHistory).count()
    
    return AnalyticsSummary(
        total_products=total_products,
        by_source=by_source,
        by_category=by_category,
        avg_price_by_source=avg_price_by_source,
        avg_price_by_category=avg_price_by_category,
        price_changes_last_24h=price_changes_last_24h,
        total_price_history_records=total_price_history_records
    )
