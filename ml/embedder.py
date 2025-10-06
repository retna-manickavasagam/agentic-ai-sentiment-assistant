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
prod_chunks = pd.read_csv("data/processed/chunked_products.csv")
texts = prod_chunks["chunk_review_text"].astype(str).tolist()
metas = prod_chunks[["product_id", "product_name", "chunk_id"]].to_dict(orient="records")

product_store = Chroma.from_texts(
    texts=texts,
    embedding=emb,
    metadatas=metas,
    collection_name="products",
    persist_directory=persist_dir
)

print("Persisted products collection.")

# 2) index  chunk reviews
reviews = pd.read_csv("data/processed/chunked_reviews.csv")
texts2 = reviews["chunk_review_text"].astype(str).tolist()
metas2 = reviews[["product_id", "product_name", "rating"]].to_dict(orient="records")

review_store = Chroma.from_texts(
    texts=texts2,
    embedding=emb,
    metadatas=metas2,
    collection_name="reviews",
    persist_directory=persist_dir
)

print("Persisted reviews collection.")
