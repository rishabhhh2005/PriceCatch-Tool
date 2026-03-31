from backend.parsers.base import BaseParser, NormalizedProduct

class FirstDibsParser(BaseParser):
    source = "1stdibs"

    def parse(self, raw: dict, filename: str) -> NormalizedProduct:
        metadata = raw.get("metadata", {})
        
        # Derive category from filename (e.g., 1stdibs_chanel_belts_02.json)
        parts = filename.split("_")
        category = parts[2] if len(parts) > 2 else "unknown"

        images = raw.get("main_images", [])
        image_url = images[0].get("url") if images else None

        return NormalizedProduct(
            source_id=str(raw.get("product_id", "")),
            source=self.source,
            brand=raw.get("brand", ""),
            model=raw.get("model", ""),
            category=category,
            current_price=float(raw.get("price", 0.0)),
            currency="USD",
            condition=metadata.get("condition_display"),
            image_url=image_url,
            product_url=raw.get("product_url"),
            description=raw.get("full_description"),
            is_available=metadata.get("availability") == "In Stock"
        )
