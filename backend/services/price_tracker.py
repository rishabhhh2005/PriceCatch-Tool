from sqlalchemy.orm import Session
from backend.models import Product, PriceHistory
from backend.services.notifier import enqueue_price_change
import asyncio

async def check_and_record_price_change(session: Session, db_product: Product, new_price: float) -> bool:
    """
    Compare new_price vs db_product.current_price.
    If different: update products.current_price, insert price_history row,
    queue notification. Return True if changed.
    """
    if db_product.current_price != new_price:
        old_price = db_product.current_price
        db_product.current_price = new_price
        
        # Insert price_history row
        history = PriceHistory(
            product_id=db_product.id,
            price=new_price,
            currency=db_product.currency
        )
        session.add(history)
        session.commit()
        
        # Queue notification
        asyncio.create_task(
            enqueue_price_change(
                product_id=db_product.id,
                old_price=old_price,
                new_price=new_price,
                product_url=db_product.product_url
            )
        )
        return True
    return False

async def get_price_history(session: Session, product_id: int, limit: int = 100):
    """Return last `limit` price_history rows for product ordered by recorded_at DESC."""
    return session.query(PriceHistory).filter(PriceHistory.product_id == product_id).order_by(PriceHistory.recorded_at.desc()).limit(limit).all()
