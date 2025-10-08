 # FastAPI backend API
 
from fastapi import FastAPI
from backend.routes import products as products
from backend.routes import reviews as reviews

app = FastAPI()
app.include_router(products.router)
app.include_router(reviews.router)
@app.get("/")
def home():
    return {"message": "Agentic AI Sentiment Assistant Backend Running"}
