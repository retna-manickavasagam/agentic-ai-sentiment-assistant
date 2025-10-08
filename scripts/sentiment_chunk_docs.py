# scripts/chunk_docs.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
from pathlib import Path

in_products = "data/processed/products_with_sentiment.csv"
out_chunks = Path("data/processed/chunked_products_with_sentiment.csv")
in_reviews = "data/processed/reviews_with_sentiment.csv"
out_review_chunks = Path("data/processed/chunked_reviews_with_sentiment.csv")

df = pd.read_csv(in_products)
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

rows = []
for _, r in df.iterrows():
    chunks = splitter.split_text(r['text'])
    # read sentiment fields with safe fallbacks (works whether columns exist or not)
    pos_count = r.get("positive", None) if "positive" in r.index else r.get("positive_count", None)
    neu_count = r.get("neutral", None) if "neutral" in r.index else r.get("neutral_count", None)
    neg_count = r.get("negative", None) if "negative" in r.index else r.get("negative_count", None)
    
    pos_pct = r.get("positive_pct", None)
    neu_pct = r.get("neutral_pct", None)
    neg_pct = r.get("negative_pct", None)
    
    avg_score = r.get("avg_sentiment_score", None)
    num_reviews_used = r.get("num_reviews_used", None)
    # optionally include per-review sentiment if present
    review_sentiment_label = r.get("sentiment_label", None) if "sentiment_label" in r.index else None
    review_sentiment_score = r.get("sentiment_score", None) if "sentiment_score" in r.index else None

    for i, ch in enumerate(chunks):
        rows.append({
            "product_id": r['product_id'],
            "product_name": r['product_name'],
            "chunk_id": f"{r['product_id']}_c{i}",
            "chunk_review_text": ch,
            # product-level sentiment metadata
            "positive_count": pos_count,
            "neutral_count": neu_count,
            "negative_count": neg_count,
            "positive_pct": pos_pct,
            "neutral_pct": neu_pct,
            "negative_pct": neg_pct,
            "avg_sentiment_score": avg_score,
            "num_reviews_used": num_reviews_used,
            # optional per-review sentiment (if your source rows were per-review)
            "review_sentiment_label": review_sentiment_label,
            "review_sentiment_score": review_sentiment_score,
        })
        
pd.DataFrame(rows).to_csv(out_chunks, index=False)
print(f"Wrote {len(rows)} product chunks to {out_chunks}")

# chunk reviews
df_reviews = pd.read_csv(in_reviews)
#product_id,product_name,review_text,rating
rows = []
for _, r in df_reviews.iterrows():
    chunks = splitter.split_text(r['review_text'])
    # per-review sentiment (if available)
    review_sentiment_label = r.get("sentiment_label", None)
    review_sentiment_score = r.get("sentiment_score", None)

    # product-level sentiment (support multiple possible column names)
    pos_count = r.get("positive", r.get("positive_count", r.get("pos_count", None)))
    neu_count = r.get("neutral", r.get("neutral_count", r.get("neu_count", None)))
    neg_count = r.get("negative", r.get("negative_count", r.get("neg_count", None)))

    pos_pct = r.get("positive_pct", r.get("pos_pct", None))
    neu_pct = r.get("neutral_pct", r.get("neu_pct", None))
    neg_pct = r.get("negative_pct", r.get("neg_pct", None))

    avg_score = r.get("avg_sentiment_score", r.get("avg_score", None))
    num_reviews_used = r.get("num_reviews_used", r.get("num_reviews", None))

    # review id (if present) for more unique chunk ids
    review_id = r.get("review_id", r.get("reviews.id", r.get("id", None)))

    for i, ch in enumerate(chunks):
        # create chunk id: product_productid + review id if available + chunk index
        if review_id is not None and str(review_id).strip() != "":
            chunk_id = f"{r.get('product_id')}_r{review_id}_c{i}"
        else:
            chunk_id = f"{r.get('product_id')}_c{i}"

        rows.append({
            "product_id": r.get("product_id"),
            "product_name": r.get("product_name"),
            "rating": r.get("rating"),
            "review_id": review_id,
            "chunk_id": chunk_id,
            "chunk_review_text": ch,
            # per-review sentiment
            "review_sentiment_label": review_sentiment_label,
            "review_sentiment_score": review_sentiment_score,
            # product-level sentiment summary
            "positive_count": pos_count,
            "neutral_count": neu_count,
            "negative_count": neg_count,
            "positive_pct": pos_pct,
            "neutral_pct": neu_pct,
            "negative_pct": neg_pct,
            "avg_sentiment_score": avg_score,
            "num_reviews_used": num_reviews_used,
        })
        
pd.DataFrame(rows).to_csv(out_review_chunks, index=False)
print(f"Wrote {len(rows)} product chunks to {out_review_chunks}")
