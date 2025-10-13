# backend/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from db import Base

class SentimentResults(Base):
    __tablename__ = "sentiment_results"  # table name
    __table_arg__ = {'schema': 'ai_schema'}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # table columns
    product_id = Column(String)
    name = Column(String)
    asins = Column(String)
    brand = Column(String)
    categories = Column(String)
    keys = Column(String)
    manufacturer = Column(String)
    reviews_date = Column(String)
    reviews_dateadded = Column(String)
    reviews_dateseen = Column(String)
    reviews_didpurchase = Column(String)
    reviews_dorecommend = Column(String)
    reviews_id = Column(String)
    reviews_numberful = Column(String)
    reviews_rating = Column(String)
    reviews_sourceurls = Column(String)
    reviews_text = Column(String)
    reviews_title = Column(String)
    reviews_usercity = Column(String)
    reviews_userprovince = Column(String)
    reviews_username = Column(String)
    sentiment_label = Column(String)
    sentiment_score = Column(String)