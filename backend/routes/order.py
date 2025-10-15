# backend/routes/rag.py
from fastapi import FastAPI, HTTPException, Depends, Query, APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from backend.db import SessionLocal, get_db, engine
# from backend.models_reflected import SentimentResults
import backend.schemas as schemas
from sqlalchemy import text
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/order", tags=["rag"])


class OrderRequest(BaseModel):
    product_id: str 
    name: str


@router.post("/insert", response_model=Dict[str, Any])
async def products(order: OrderRequest, db: Session = Depends(get_db)):
    """Insert a new order record into PostgreSQL."""
    try:
        # Use date from request or current date
        date = datetime.now().strftime("%Y-%m-%d")
        order_id = str(uuid.uuid4())

        print(f"Received order: {order}")
        print(f"Order type: {type(order)}")
        print(f"Order attributes: {order_id}")
        
        stmt = text("""
            INSERT INTO ai_schema.orders (product_id, name, _date, order_id)
            VALUES (:product_id, :name, :date, :order_id)
            RETURNING order_id;
        """)
        
        # Execute with parameters
        result = db.execute(stmt, {
            'product_id': order.product_id,
            'name': order.name,
            'date': date,
            'order_id': order_id
        })

        db.commit()
        inserted_order_id = result.scalar()

        return {
            "message": "✅ New order inserted successfully",
            "order_id": inserted_order_id,
            "product_id": order.product_id,
            "date": date
        }
    except Exception as e:
        db.rollback()  # Rollback on error
        print(f"Error details: {str(e)}")
        #raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        return {
            "message": "✅ New order inserted failed",
            "order_id": "",
            "product_id": "",
            "date": ""
        }