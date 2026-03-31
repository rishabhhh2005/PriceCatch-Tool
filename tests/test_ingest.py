import pytest
from backend.services.ingest import upsert_product
from backend.parsers.base import NormalizedProduct
from backend.models import Product, PriceHistory

def make_product(**kwargs):
    defaults = dict(
        source_id="ingest-test-001",
        source="grailed",
        brand="TestBrand",
        model="Test Model",
        category="apparel",
        current_price=100.0,
        currency="USD",
        condition=None,
        image_url=None,
        product_url="https://example.com",
        description=None,
        is_available=True,
    )
    defaults.update(kwargs)
    return NormalizedProduct(**defaults)

@pytest.mark.asyncio
async def test_upsert_inserts_new_product_and_creates_history_row(db_session):
    product = make_product(source_id="ingest-new-001")
    result = await upsert_product(product)
    assert result == "inserted"
    db_product = db_session.query(Product).filter(
        Product.source_id == "ingest-new-001"
    ).first()
    assert db_product is not None
    history = db_session.query(PriceHistory).filter(
        PriceHistory.product_id == db_product.id
    ).all()
    assert len(history) >= 1
    assert history[0].price == 100.0

@pytest.mark.asyncio
async def test_upsert_updates_price_and_creates_history_row_on_price_change(db_session):
    product = make_product(source_id="ingest-price-change-001", current_price=200.0)
    await upsert_product(product)
    updated = make_product(source_id="ingest-price-change-001", current_price=250.0)
    result = await upsert_product(updated)
    assert result == "price_changed"
    db_product = db_session.query(Product).filter(
        Product.source_id == "ingest-price-change-001"
    ).first()
    assert db_product.current_price == 250.0
    history = db_session.query(PriceHistory).filter(
        PriceHistory.product_id == db_product.id
    ).all()
    assert len(history) >= 2
