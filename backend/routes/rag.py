# backend/routes/rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from ml import rag_engine  

router = APIRouter(prefix="/api/rag", tags=["rag"])

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

@router.post("/products", response_model=Dict[str, Any])
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


@router.post("/reviews", response_model=Dict[str, Any])
async def reviews(req: ReviewRequest):
    """
    Return top reviews for a product. If product_id is provided, it will be used to filter results.
    Otherwise product_name (approximate / semantic match) will be used.
    """
    # validation: need at least one identifier
    if not req.product_id and not req.product_name:
        raise HTTPException(status_code=400, detail="Provide product_id or product_name")

    try:
        # call into your rag engine
        docs = rag_engine.get_reviews_for_product(
            product_id=req.product_id,
            product_name=req.product_name,
            k=req.k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in rag engine: {e}")

    print(docs)
    # Format output and optionally strip source text/metadata
    out_results: List[Dict[str, Any]] = []
    for d in docs:
        item = {
            "product_id": d.get("product_id"),
            "product_name": d.get("product_name"),
            "score": d.get("score")
        }
        if req.include_sources:
            item["text"] = d.get("review_text")
            item["metadata"] = d.get("metadata", {})
        out_results.append(item)
    #print(out_results)
    return {
        "product_id": req.product_id,
        "product_name": req.product_name,
        "count": len(out_results),
        "results": out_results
    }
