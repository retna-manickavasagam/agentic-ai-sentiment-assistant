 # FastAPI backend API
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from db import SessionLocal, get_db, engine
# from backend.routes import products as products
# from backend.routes import reviews as reviews
# from backend.agents import agent_bot as agent
from models_reflected import SentimentResults
import schemas
from sqlalchemy import text

# Create database tables
# models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Sentiment Analysis API", version="1.0.0")
# app.include_router(products.router)
# app.include_router(reviews.router)
# app.include_router(agent.router)

@app.get("/")
def home():
    return {"message": "Agentic AI Sentiment Assistant Backend Running"}
    

# Sentiments endpoints
#Get all sentiments
@app.get("/sentiments", response_model=schemas.SentimentListResponse)
def get_sentiments(
    limit: int = 100, 
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get sentiment data from PostgreSQL database
    - limit: Number of records to return (default: 100)
    - offset: Number of records to skip (for pagination)
    """
    try:
        # Debug: Check table existence and count
        table_exists = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'sentiment_results'
            );
        """)).scalar()
        
        total_count = db.execute(text("SELECT COUNT(*) FROM sentiment_results")).scalar()
        
        print(f"Table exists: {table_exists}")
        print(f"Total records in table: {total_count}")

        # Query sentiments from database
        sentiments = db.query(SentimentResults).offset(offset).limit(limit).all()
        
        return {
            "status": "success",
            "data": sentiments,
            "count": len(sentiments)
        }
        
    except Exception as e:
        print(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Get sentiment statistics for reviews by product_id or for all product
# example: /sentiment_stats?product_id=AVqkIhwDv8e3D1O-lebb  
@app.get("/sentiment_stats")
def sentiment_stats(
    product_id: str = Query(None, description="Filter by product ID"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment statistics for reviews
    """
    try:
        if product_id:
            # Get stats for specific product
            result = db.execute(text("""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(CAST(sentiment_score AS FLOAT)) as avg_sentiment,
                    COUNT(CASE WHEN sentiment_label = 'positive' THEN 1 END) as positive_count,
                    COUNT(CASE WHEN sentiment_label = 'negative' THEN 1 END) as negative_count,
                    COUNT(CASE WHEN sentiment_label = 'neutral' THEN 1 END) as neutral_count
                FROM sentiment_results 
                WHERE product_id = :product_id
            """), {"product_id": product_id})
        else:
            # Get overall stats
            result = db.execute(text("""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(CAST(sentiment_score AS FLOAT)) as avg_sentiment,
                    COUNT(CASE WHEN sentiment_label = 'positive' THEN 1 END) as positive_count,
                    COUNT(CASE WHEN sentiment_label = 'negative' THEN 1 END) as negative_count,
                    COUNT(CASE WHEN sentiment_label = 'neutral' THEN 1 END) as neutral_count
                FROM sentiment_results
            """))
        
        stats = result.fetchone()
        
        return {
            "product_id": product_id if product_id else "All Products",
            "total_reviews": stats[0],
            "average_sentiment": float(stats[1]) if stats[1] else 0,
            "positive_reviews": stats[2],
            "negative_reviews": stats[3],
            "neutral_reviews": stats[4]
        }
        
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Filter by sentiment label
@app.get("/sentiments/filter/by-label/")
def get_sentiments_by_label(
    label: str,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    try:
        # sentiments = db.query(SentimentResults).filter(
        #     SentimentResults.sentiment_label == label
        # ).offset(offset).limit(limit).all()

         # Use raw SQL to avoid model issues
        result = db.execute(text("""
            SELECT * FROM ai_schema.sentiment_results 
            WHERE sentiment_label = :label 
            ORDER BY id 
            LIMIT :limit OFFSET :offset
        """), {
            "label": label,
            "limit": limit,
            "offset": offset
        })
        
        columns = result.keys()
        rows = result.fetchall()
        
        # Convert to list of dictionaries
        sentiments = []
        for row in rows:
            sentiments.append(dict(zip(columns, row)))
        
        return {
            "status": "success",
            "data": sentiments,
            "count": len(sentiments)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Get single sentiment by ID
@app.get("/sentiments/{product_id}", response_model=schemas.SentimentListResponse)
def get_sentiment(
    product_id: str,  # Now using integer ID
    db: Session = Depends(get_db),
    limit: int = Query(100, le=1000),
    offset: int = 0
):
    try:
        # Use raw SQL to avoid model issues
        result = db.execute(text("""
            SELECT * FROM ai_schema.sentiment_results 
            WHERE product_id = :product_id 
            ORDER BY id
            LIMIT :limit OFFSET :offset
        """), {
            "product_id": product_id,
            "limit": limit,
            "offset": offset
        })
        
        columns = result.keys()
        rows = result.fetchall()
        
        # Convert to list of dictionaries
        sentiments = []
        for row in rows:
            sentiments.append(dict(zip(columns, row)))
        
        return {
            "status": "success",
            "data": sentiments,
            "count": len(sentiments)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/get_product_ids")
def get_product_ids(
    limit: int = Query(50, description="Number of product IDs to return"),
    db: Session = Depends(get_db)
):
    """Get a list of product IDs for the frontend"""
    try:
        result = db.execute(text("""
            SELECT DISTINCT product_id 
            FROM ai_schema.sentiment_results 
            WHERE product_id IS NOT NULL 
            AND product_id != ''
            ORDER BY product_id
            LIMIT :limit
        """), {"limit": limit})
        
        product_ids = [row[0] for row in result.fetchall()]
        
        return {
            "product_ids": product_ids,
            "count": len(product_ids)
        }
        
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/available-sentiment-labels")
def get_available_sentiment_labels(db: Session = Depends(get_db)):
    """Get all distinct sentiment labels available in the database"""
    try:
        result = db.execute(text("""
            SELECT DISTINCT sentiment_label, COUNT(*) as count
            FROM ai_schema.sentiment_results 
            WHERE sentiment_label IS NOT NULL
            AND sentiment_label != ''
            GROUP BY sentiment_label
            ORDER BY count DESC
        """))
        
        labels = []
        for row in result:
            labels.append({
                "label": row[0],
                "count": row[1]
            })
        
        return {
            "available_labels": labels,
            "total_unique_labels": len(labels)
        }
        
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Health check for database
@app.get("/health", response_model=schemas.HealthCheck)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))  # Use text() wrapper here too
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


