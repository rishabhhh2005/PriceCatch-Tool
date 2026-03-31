from backend.parsers.base import BaseParser, NormalizedProduct

class FashionphileParser(BaseParser):
    source = "fashionphile"

    def parse(self, raw: dict, filename: str) -> NormalizedProduct:
        metadata = raw.get("metadata", {})
        
        category = metadata.get("garment_type", "unknown")
        
        return NormalizedProduct(
            source_id=str(raw.get("product_id", "")),
            source=self.source,
            brand=raw.get("brand", ""),
            model=raw.get("model", ""),
            category=category,
            current_price=float(raw.get("price", 0.0)),
            currency=raw.get("currency", "USD"),
            condition=raw.get("condition"),
            image_url=raw.get("image_url"),
            product_url=raw.get("product_url"),
            description=metadata.get("description"),
            is_available=True
        )
