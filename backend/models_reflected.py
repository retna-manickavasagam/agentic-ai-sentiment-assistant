# backend/models_reflected.py
from sqlalchemy import Table, MetaData
from db import engine

metadata = MetaData()

# This will automatically read the table structure from the database
SentimentResults = Table('sentiment_results', metadata, autoload_with=engine)

# Use this in your main.py instead of the model class