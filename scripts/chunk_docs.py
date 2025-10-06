# scripts/chunk_docs.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
from pathlib import Path

in_products = "data/processed/products.csv"
out_chunks = Path("data/processed/chunked_products.csv")
in_reviews = "data/processed/reviews.csv"
out_review_chunks = Path("data/processed/chunked_reviews.csv")

df = pd.read_csv(in_products)
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

rows = []
for _, r in df.iterrows():
    chunks = splitter.split_text(r['text'])
    for i, ch in enumerate(chunks):
        rows.append({
            "product_id": r['product_id'],
            "product_name": r['product_name'],
            "chunk_id": f"{r['product_id']}_c{i}",
            "chunk_review_text": ch
        })
        
pd.DataFrame(rows).to_csv(out_chunks, index=False)
print(f"Wrote {len(rows)} product chunks to {out_chunks}")

# chunk reviews
df_reviews = pd.read_csv(in_reviews)
#product_id,product_name,review_text,rating
rows = []
for _, r in df_reviews.iterrows():
    chunks = splitter.split_text(r['review_text'])
    for i, ch in enumerate(chunks):
        rows.append({
            "product_id": r['product_id'],
            "product_name": r['product_name'],
            "rating": r['rating'],
            "chunk_id": f"{r['product_id']}_c{i}",
            "chunk_review_text": ch
        })
        
pd.DataFrame(rows).to_csv(out_review_chunks, index=False)
print(f"Wrote {len(rows)} product chunks to {out_review_chunks}")
