# backend/routes/rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from ml import rag_engine  

router = APIRouter(prefix="/api/products", tags=["rag"])

# ---------- Request / Response Models ----------

class ProductRequest(BaseModel):
    query: str = Field(..., description="User query for products (e.g. 'wireless headphones')")
    k: int = Field(3, ge=1, le=50, description="Number of products to return")


class ReviewRequest(BaseModel):
    product_id: Optional[str] = Field(None, description="Optional product id (use this to filter)")
    product_name: Optional[str] = Field(None, description="Fallback product name for similarity search")
    k: int = Field(3, ge=1, le=100, description="Number of reviews to return")
    include_sources: bool = Field(False, description="Include original review text and metadata in results")


class Hit(BaseModel):
    product_id: Optional[str]
    product_name: Optional[str]
    score: Optional[float]
    text: Optional[str]
    metadata: Optional[Dict[str, Any]]


# ---------- Routes ----------

@router.post("/retrieve", response_model=Dict[str, Any])
async def products(req: ProductRequest):
    """
    Return top-k matching products for a user query by calling rag_engine.get_top_products.
    """
    try:
        results = rag_engine.get_top_products(req.query, k=req.k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in rag engine: {e}")

    # Normalize results if needed (ensure list of dicts)
    return {"query": req.query, "count": len(results), "results": results}