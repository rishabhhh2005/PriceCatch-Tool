import pytest
from backend.services.ingest import upsert_product
from backend.parsers.base import NormalizedProduct
from backend.models import Product, PriceHistory

@pytest.mark.asyncio
async def test_no_history_row_created_when_price_unchanged(db_session):
    from backend.parsers.base import NormalizedProduct
    product = NormalizedProduct(
        source_id="tracker-unchanged-001",
        source="fashionphile",
        brand="Brand",
        model="Model",
        category="jewelry",
        current_price=500.0,
        currency="USD",
        condition=None,
        image_url=None,
        product_url="https://example.com",
        description=None,
        is_available=True,
    )
    await upsert_product(product)
    db_product = db_session.query(Product).filter(
        Product.source_id == "tracker-unchanged-001"
    ).first()
    count_before = db_session.query(PriceHistory).filter(
        PriceHistory.product_id == db_product.id
    ).count()
    # Upsert again with same price
    result = await upsert_product(product)
    count_after = db_session.query(PriceHistory).filter(
        PriceHistory.product_id == db_product.id
    ).count()
    assert result == "unchanged"
    assert count_after == count_before
