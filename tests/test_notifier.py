import pytest
import asyncio
from backend.services.notifier import enqueue_price_change, _queue

@pytest.mark.asyncio
async def test_enqueue_does_not_raise():
    before = _queue.qsize()
    await enqueue_price_change(
        product_id=1,
        old_price=100.0,
        new_price=150.0,
        product_url="https://example.com/product/1"
    )
    assert _queue.qsize() == before + 1

@pytest.mark.asyncio
async def test_enqueue_event_has_correct_fields():
    # Empty queue from previous tests
    while not _queue.empty():
        await _queue.get()
        
    await enqueue_price_change(
        product_id=42,
        old_price=200.0,
        new_price=180.0,
        product_url="https://example.com/product/42"
    )
    event = await _queue.get()
    assert event["product_id"] == 42
    assert event["old_price"] == 200.0
    assert event["new_price"] == 180.0
    assert event["event"] == "price_change"
    assert "timestamp" in event
