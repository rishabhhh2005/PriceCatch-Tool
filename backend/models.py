from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, autoincrement=True)
    key_hash = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ApiUsage(Base):
    __tablename__ = "api_usage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    key_hash = Column(String, ForeignKey("api_keys.key_hash"), nullable=False)
    endpoint = Column(String, nullable=False)
    called_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String, nullable=False)
    source = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    category = Column(String)
    current_price = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    condition = Column(String)
    image_url = Column(String)
    product_url = Column(String)
    description = Column(Text)
    is_available = Column(Boolean, default=True)
    last_seen = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('source_id', 'source', name='uix_source_id_source'),
        Index('idx_products_source', 'source'),
        Index('idx_products_brand', 'brand'),
        Index('idx_products_category', 'category'),
        Index('idx_products_current_price', 'current_price'),
    )

    history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    recorded_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_price_history_product', 'product_id'),
        Index('idx_price_history_recorded', 'recorded_at'),
    )

    product = relationship("Product", back_populates="history")

class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    secret = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class NotificationLog(Base):
    __tablename__ = "notification_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer, ForeignKey("webhook_subscriptions.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    old_price = Column(Float)
    new_price = Column(Float)
    payload = Column(Text)
    status = Column(String) # 'pending', 'delivered', 'failed'
    attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
