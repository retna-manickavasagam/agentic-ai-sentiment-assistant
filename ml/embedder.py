# OpenAI embeddings

from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
import pandas as pd
from pathlib import Path

persist_dir = "./chroma_db"
Path(persist_dir).mkdir(exist_ok=True)

# choose embeddings model
emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 1) index product chunks
#prod_chunks = pd.read_csv("data/processed/chunked_products.csv")
prod_chunks = pd.read_csv("data/processed/chunked_products_with_sentiment.csv")

def safe_none(val):
    # convert NaN/empty strings to None for metadata
    if pd.isna(val):
        return None
    if isinstance(val, str) and val.strip() == "":
        return None
    return val
# Build metadata with sentiment fields (use .get style for optional columns)
def build_product_meta(row):
    return {
        "product_id": safe_none(row.get("product_id")),
        "product_name": safe_none(row.get("product_name")),
        "chunk_id": safe_none(row.get("chunk_id")),
        # product-level sentiment (support both naming variants)
        "positive_count": safe_none(row.get("positive") or row.get("positive_count") or row.get("pos_count")),
        "neutral_count": safe_none(row.get("neutral") or row.get("neutral_count") or row.get("neu_count")),
        "negative_count": safe_none(row.get("negative") or row.get("negative_count") or row.get("neg_count")),
        "positive_pct": safe_none(row.get("positive_pct") or row.get("pos_pct")),
        "neutral_pct": safe_none(row.get("neutral_pct") or row.get("neu_pct")),
        "negative_pct": safe_none(row.get("negative_pct") or row.get("neg_pct")),
        "avg_sentiment_score": safe_none(row.get("avg_sentiment_score") or row.get("avg_score")),
        "num_reviews_used": safe_none(row.get("num_reviews_used") or row.get("num_reviews")),
        # keep original chunk text length for filters (optional)
        "chunk_length": len(row.get("chunk_review_text", "")),
    }
    
texts = prod_chunks["chunk_review_text"].astype(str).tolist()
#metas = prod_chunks[["product_id", "product_name", "chunk_id"]].to_dict(orient="records")
metas = [build_product_meta(row) for _, row in prod_chunks.iterrows()]

product_store = Chroma.from_texts(
    texts=texts,
    embedding=emb,
    metadatas=metas,
    collection_name="products_with_sentiment",
    persist_directory=persist_dir
)

print("Persisted products collection.")

# 2) index  chunk reviews
reviews = pd.read_csv("data/processed/chunked_reviews_with_sentiment.csv")
def build_review_meta(row):
    return {
        "product_id": safe_none(row.get("product_id")),
        "product_name": safe_none(row.get("product_name")),
        "rating": safe_none(row.get("rating")),
        "review_id": safe_none(row.get("review_id") or row.get("reviews.id") or row.get("id")),
        "chunk_id": safe_none(row.get("chunk_id")),
        # per-review sentiment (if present)
        "review_sentiment_label": safe_none(row.get("review_sentiment_label") or row.get("sentiment_label")),
        "review_sentiment_score": safe_none(row.get("review_sentiment_score") or row.get("sentiment_score")),
        # product-level sentiment summary (if you merged it in)
        "positive_count": safe_none(row.get("positive") or row.get("positive_count") or row.get("pos_count")),
        "neutral_count": safe_none(row.get("neutral") or row.get("neutral_count") or row.get("neu_count")),
        "negative_count": safe_none(row.get("negative") or row.get("negative_count") or row.get("neg_count")),
        "positive_pct": safe_none(row.get("positive_pct") or row.get("pos_pct")),
        "neutral_pct": safe_none(row.get("neutral_pct") or row.get("neu_pct")),
        "negative_pct": safe_none(row.get("negative_pct") or row.get("neg_pct")),
        "avg_sentiment_score": safe_none(row.get("avg_sentiment_score") or row.get("avg_score")),
        "num_reviews_used": safe_none(row.get("num_reviews_used") or row.get("num_reviews")),
        "chunk_length": len(row.get("chunk_review_text", "")),
    }
texts2 = reviews["chunk_review_text"].astype(str).tolist()
metas2 = [build_review_meta(row) for _, row in reviews.iterrows()]

review_store = Chroma.from_texts(
    texts=texts2,
    embedding=emb,
    metadatas=metas2,
    collection_name="reviews_with_sentiment",
    persist_directory=persist_dir
)

print("Persisted reviews collection.")
