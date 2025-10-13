# backend/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SentimentBase(BaseModel):  
    id: Optional[int] = None
    product_id: Optional[str] = None
    name: Optional[str] = None
    asins: Optional[str] = None
    brand: Optional[str] = None
    categories: Optional[str] = None
    keys: Optional[str] = None
    manufacturer: Optional[str] = None
    reviews_date: Optional[str] = None
    reviews_dateadded: Optional[str] = None
    reviews_dateseen: Optional[str] = None
    reviews_didpurchase: Optional[str] = None
    reviews_dorecommend: Optional[str] = None
    reviews_id: Optional[str] = None
    reviews_numberful: Optional[str] = None
    reviews_rating: Optional[str] = None
    reviews_sourceurls: Optional[str] = None
    reviews_text: Optional[str] = None
    reviews_title: Optional[str] = None
    reviews_usercity: Optional[str] = None
    reviews_userprovince: Optional[str] = None
    reviews_username: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[str] = None

class SentimentResponse(SentimentBase):
    id: int  # Primary key is required in response
    
    class Config:
        from_attributes = True

class SentimentListResponse(BaseModel):
    status: str
    data: List[SentimentResponse]
    count: int

class HealthCheck(BaseModel):
    status: str
    database: str