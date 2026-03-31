from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.database import get_session
from backend.models import Product, PriceHistory
from backend.schemas import ProductSchema, ProductWithHistory, PriceHistorySchema, PaginatedProducts
from backend.auth import require_api_key

products_router = APIRouter(dependencies=[Depends(require_api_key)])

@products_router.get("/products", response_model=PaginatedProducts)
async def get_products(
    source: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available_only: bool = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = session.query(Product)
    
    if source:
        query = query.filter(Product.source == source)
    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)
    if min_price is not None:
        query = query.filter(Product.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.current_price <= max_price)
    if available_only:
        query = query.filter(Product.is_available == True)
        
    total = query.count()
    pages = (total + page_size - 1) // page_size
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages
    }

@products_router.get("/products/{id}", response_model=ProductWithHistory)
async def get_product(id: int, session: Session = Depends(get_session)):
    product = session.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product

@products_router.get("/products/{id}/price-history", response_model=List[PriceHistorySchema])
async def get_product_history(id: int, limit: int = 50, session: Session = Depends(get_session)):
    product = session.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    history = session.query(PriceHistory).filter(PriceHistory.product_id == id).order_by(PriceHistory.recorded_at.desc()).limit(limit).all()
    return history
