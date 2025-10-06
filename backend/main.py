 # FastAPI backend API
 
from fastapi import FastAPI
from backend.routes import rag as rag_routes

app = FastAPI()
app.include_router(rag_routes.router)

@app.get("/")
def home():
    return {"message": "Agentic AI Sentiment Assistant Backend Running"}
