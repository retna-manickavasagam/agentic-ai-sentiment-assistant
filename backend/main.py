 # FastAPI backend API
from fastapi import FastAPI 
from backend.routes import products as products
from backend.routes import reviews as reviews
from backend.routes import order as order
from backend.routes import sentiment as sentiment
from backend.routes import email as email
 

# Create FastAPI app
app = FastAPI(title="Sentiment Analysis API", version="1.0.0")
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(order.router)
app.include_router(sentiment.router)
app.include_router(email.router)

@app.get("/")
def home():
    return {"message": "Agentic AI Sentiment Assistant Backend Running"}
    




