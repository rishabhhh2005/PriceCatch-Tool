import asyncio
import pathlib
import logging
from typing import List, Dict, Any
from backend.parsers.grailed import GrailedParser
from backend.parsers.fashionphile import FashionphileParser
from backend.parsers.firstdibs import FirstDibsParser
from backend.services.price_tracker import check_and_record_price_change
from backend.database import SessionLocal
from backend.models import Product, PriceHistory
from datetime import datetime

SAMPLE_DIR = pathlib.Path("sample_products")

PARSER_MAP = {
    "grailed": GrailedParser(),
    "fashionphile": FashionphileParser(),
    "1stdibs": FirstDibsParser(),
}

async def ingest_all() -> Dict[str, int]:
    """Read all JSON files from sample_products/, parse, upsert into DB."""
    results = {"inserted": 0, "updated": 0, "price_changes": 0, "errors": 0}
    if not SAMPLE_DIR.exists():
        logging.warning("sample_products/ directory not found.")
        return results

    files = list(SAMPLE_DIR.glob("*.json"))

    async def process_file(path: pathlib.Path):
        source = path.name.split("_")[0]
        parser = PARSER_MAP.get(source)
        if not parser:
            logging.warning(f"No parser for source: {source}")
            return
        
        try:
            product_data = parser.load_file(path)
            change = await upsert_product(product_data)
            if change == "inserted":
                results["inserted"] += 1
            elif change == "updated":
                results["updated"] += 1
                
            if change in ("inserted", "price_changed"):
                if change == "price_changed":
                    results["updated"] += 1
                    results["price_changes"] += 1
        except Exception as e:
            logging.error(f"Error processing {path.name}: {e}")
            results["errors"] += 1

    tasks = [process_file(f) for f in files]
    if tasks:
        await asyncio.gather(*tasks)
    return results

async def upsert_product(product) -> str:
    """Insert or update product. Return 'inserted', 'updated', 'price_changed' or 'unchanged'."""
    db = SessionLocal()
    try:
        db_product = db.query(Product).filter(
            Product.source_id == product.source_id,
            Product.source == product.source
        ).first()

        if db_product:
            price_changed = await check_and_record_price_change(db, db_product, product.current_price)
            
            # Update other fields
            is_updated = False
            fields_to_update = [
                'brand', 'model', 'category', 'currency', 'condition',
                'image_url', 'product_url', 'description', 'is_available'
            ]
            for field in fields_to_update:
                new_val = getattr(product, field)
                if getattr(db_product, field) != new_val:
                    setattr(db_product, field, new_val)
                    is_updated = True
            
            db_product.last_seen = datetime.utcnow()
            
            if is_updated and not price_changed:
                db.commit()
                return "updated"
            elif price_changed:
                db.commit()
                return "price_changed"
            else:
                db.commit()
                return "unchanged"
        else:
            # Insert new product
            new_product = Product(
                source_id=product.source_id,
                source=product.source,
                brand=product.brand,
                model=product.model,
                category=product.category,
                current_price=product.current_price,
                currency=product.currency,
                condition=product.condition,
                image_url=product.image_url,
                product_url=product.product_url,
                description=product.description,
                is_available=product.is_available,
                last_seen=datetime.utcnow()
            )
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            
            # Initial history record
            history = PriceHistory(
                product_id=new_product.id,
                price=product.current_price,
                currency=product.currency
            )
            db.add(history)
            db.commit()
            return "inserted"
    finally:
        db.close()
