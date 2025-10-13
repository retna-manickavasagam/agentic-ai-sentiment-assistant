 # FastAPI backend API
from fastapi import FastAPI, HTTPException, Depends, Query
 
from backend.routes import chat as chat 
# from models_reflected import SentimentResults
# import schemas
# from sqlalchemy import text

# Create database tables
# models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Chat API", version="1.0.0")
app.include_router(chat.router) 
#app.include_router(agent.router)

@app.get("/")
def home():
    return {"message": "Agentic AI Chat backend Running"}
    