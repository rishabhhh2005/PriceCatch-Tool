from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime

class ProductBase(BaseModel):
    source_id: str
    source: str
    brand: str
    model: str
    category: Optional[str] = None
    current_price: float
    currency: str = "USD"
    condition: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    description: Optional[str] = None
    is_available: bool = True

class ProductSchema(ProductBase):
    id: int
    last_seen: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PriceHistorySchema(BaseModel):
    id: int
    product_id: int
    price: float
    currency: str
    recorded_at: datetime

    class Config:
        from_attributes = True

class ProductWithHistory(ProductSchema):
    history: List[PriceHistorySchema] = []

class PaginatedProducts(BaseModel):
    items: List[ProductSchema]
    total: int
    page: int
    pages: int

class WebhookCreate(BaseModel):
    url: HttpUrl
    secret: Optional[str] = None

class WebhookResponse(BaseModel):
    id: int
    url: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class NotificationLogResponse(BaseModel):
    id: int
    webhook_id: Optional[int]
    product_id: Optional[int]
    old_price: Optional[float]
    new_price: Optional[float]
    payload: str
    status: str
    attempts: int
    last_attempt: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_products: int
    by_source: Dict[str, int]
    by_category: Dict[str, int]
    avg_price_by_source: Dict[str, float]
    avg_price_by_category: Dict[str, float]
    price_changes_last_24h: int
    total_price_history_records: int
