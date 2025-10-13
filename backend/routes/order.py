# backend/routes/rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

router = APIRouter(prefix="/api/order", tags=["rag"])


class OrderRequest(BaseModel):
    product_id: Optional[str] = Field(None, description="Optional product id (use this to filter)")  


class Hit(BaseModel):
    product_id: Optional[str]
    product_name: Optional[str]
    score: Optional[float]
    text: Optional[str]
    metadata: Optional[Dict[str, Any]]


@router.post("/insert", response_model=Dict[str, Any])
async def products(req: OrderRequest):
    return {"message":"success"}