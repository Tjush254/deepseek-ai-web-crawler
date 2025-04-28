from pydantic import BaseModel, Field
from typing import Optional, List

class Product(BaseModel):
    name: str
    price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    seller: Optional[str] = None
    category: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    availability: Optional[str] = None
    features: Optional[List[str]] = None
    
    @property
    def discount_amount(self) -> Optional[float]:
        if self.original_price and self.price:
            return round(self.original_price - self.price, 2)
        return None
    