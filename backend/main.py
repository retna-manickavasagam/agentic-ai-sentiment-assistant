 # FastAPI backend API
from fastapi import FastAPI, HTTPException, Depends, Query
#from sqlalchemy.orm import Session
#from db import SessionLocal, get_db, engine
from backend.routes import products as products
from backend.routes import reviews as reviews
#from backend.agents import agent_bot as agent
from backend.routes import order as order
from backend.routes import sentiment as sentiment
# from models_reflected import SentimentResults
# import schemas
# from sqlalchemy import text

# Create database tables
# models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Sentiment Analysis API", version="1.0.0")
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(order.router)
app.include_router(sentiment.router)
#app.include_router(agent.router)

@app.get("/")
def home():
    return {"message": "Agentic AI Sentiment Assistant Backend Running"}
    




