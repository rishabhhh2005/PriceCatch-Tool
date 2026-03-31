from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import json, pathlib

@dataclass
class NormalizedProduct:
    source_id: str
    source: str
    brand: str
    model: str
    category: str
    current_price: float
    currency: str
    condition: Optional[str]
    image_url: Optional[str]
    product_url: Optional[str]
    description: Optional[str]
    is_available: bool

class BaseParser(ABC):
    source: str

    @abstractmethod
    def parse(self, raw: dict, filename: str) -> NormalizedProduct:
        pass

    def load_file(self, path: pathlib.Path) -> NormalizedProduct:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return self.parse(raw, path.name)
