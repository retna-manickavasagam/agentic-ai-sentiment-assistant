# main.py
from fastapi import  APIRouter, HTTPException,Query
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import os

load_dotenv()
# Load your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/api/agent", tags=["agent"])

 
@router.post("/ask")
async def ask_llm(user_query: str = Query(..., description="The query to ask the agent")):
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_query}
            ],
            temperature=0.7,
            max_tokens=200
        )
        answer = response.choices[0].message.content.strip()
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
