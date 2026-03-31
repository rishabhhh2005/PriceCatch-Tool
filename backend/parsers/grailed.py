from backend.parsers.base import BaseParser, NormalizedProduct

class GrailedParser(BaseParser):
    source = "grailed"

    def parse(self, raw: dict, filename: str) -> NormalizedProduct:
        metadata = raw.get("metadata", {})
        
        # Category derivation
        func_id = raw.get("function_id", "")
        category = func_id.replace("_authentication", "") if func_id else "unknown"

        return NormalizedProduct(
            source_id=str(raw.get("product_id", "")),
            source=self.source,
            brand=raw.get("brand", ""),
            model=raw.get("model", ""),
            category=category,
            current_price=float(raw.get("price", 0.0)),
            currency="USD",
            condition=None, # Grailed might not have a single condition field in sample fields provided
            image_url=raw.get("image_url"),
            product_url=raw.get("product_url"),
            description=None,
            is_available=not metadata.get("is_sold", False)
        )
