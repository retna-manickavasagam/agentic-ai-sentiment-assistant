 # FastAPI backend API
 
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Agentic AI Sentiment Assistant Backend Running"}
