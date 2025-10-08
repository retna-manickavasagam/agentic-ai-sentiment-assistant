# scripts/prepare_docs.py
import pandas as pd
import hashlib
from pathlib import Path

INPUT = "data/processed/sentiment_data.csv"
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# read raw csv
df = pd.read_csv(INPUT, dtype={1: str, 10: str})
#print(df.columns.tolist())
df = df.rename(columns=lambda x: x.strip())
#print('after')
#print(df.columns.tolist())
product_id_col="id"
product_col = "name"  
review_col = "reviews.text"  
rating_col = "reviews.rating"  
category_col = "categories"  
print("Unique product names and counts:")
print(df[product_col].value_counts())
print("Unique product ids and counts (if present):")
if product_id_col in df.columns:
    print(df[product_id_col].value_counts())
else:
    print("product_id_col missing")
# Fill NAs
df[review_col] = df[review_col].fillna("").astype(str)
df[product_col] = df[product_col].fillna("Unknown Product").astype(str)
df.columns = df.columns.str.strip()

score_thresholds = {
    "positive": 0.05,   # score >= 0.05 -> positive
    "negative": -0.05   # score <= -0.05 -> negative
}

# Helper to infer label from score
def infer_label_from_score(score):
    try:
        s = float(score)
    except Exception:
        return None
    if s >= score_thresholds["positive"]:
        return "positive"
    if s <= score_thresholds["negative"]:
        return "negative"
    return "neutral"

docs = []
for prod, group in df.groupby(product_col):
    # sample up to 10 reviews for the product to build product context
    sample_reviews = group[review_col].dropna().astype(str).tolist()[:10]
    combined = " ".join(sample_reviews)
    category_val = group[category_col].iloc[0] if category_col in group.columns else ""
    if "sentiment_label" in group.columns:
        labels = group["sentiment_label"].astype(str).fillna("").tolist()
    else:
        labels = [""] * len(group)

    # Try fill missing labels by using sentiment_score if available
    if ("sentiment_score" in group.columns):
        scores = group["sentiment_score"].tolist()
    else:
        scores = [None] * len(group)

    normalized_labels = []
    for lab, sc in zip(labels, scores):
        lab = lab.strip().lower() if isinstance(lab, str) else ""
        if lab not in ("positive", "negative", "neutral"):
            inferred = infer_label_from_score(sc)
            normalized_labels.append(inferred if inferred is not None else "neutral")  # default neutral
        else:
            normalized_labels.append(lab)

    # compute counts and percentages
    label_series = pd.Series(normalized_labels)
    counts = label_series.value_counts().to_dict()           # e.g. {'positive': 5, 'neutral': 2, 'negative': 1}
    total = max(len(label_series), 1)
    pct = {k: (v / total) * 100 for k, v in counts.items()} # percentages

    # ensure keys exist
    pos_count = counts.get("positive", 0)
    neu_count = counts.get("neutral", 0)
    neg_count = counts.get("negative", 0)
    pos_pct = pct.get("positive", 0.0)
    neu_pct = pct.get("neutral", 0.0)
    neg_pct = pct.get("negative", 0.0)

    # average sentiment score (if available)
    try:
        valid_scores = [float(s) for s in scores if pd.notna(s)]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else None
    except Exception:
        avg_score = None
    summary_text = f"Product: {prod}\nCategories: {category_val}\n\nTop reviews:\n{combined}"
    #prod_id = hashlib.md5(prod.encode("utf-8")).hexdigest()[:12]
    prod_id = group[product_id_col].iloc[0]
    print(prod_id)
    docs.append({"product_id": prod_id, "product_name": prod, "text": summary_text, "metadata": {
            "category": category_val,
            "sentiment_counts": {"positive": pos_count, "neutral": neu_count, "negative": neg_count},
            "sentiment_percent": {"positive_pct": round(pos_pct, 2), "neutral_pct": round(neu_pct, 2), "negative_pct": round(neg_pct, 2)},
            "avg_sentiment_score": round(avg_score, 4) if avg_score is not None else None,
            "num_reviews_used": total
        }})

print(f"Built docs for {len(docs)} products.")
# Try building rows safely and report problems
rows = []
errors = []
for i, d in enumerate(docs):
    try:
        md = d.get("metadata", {}) or {}
        counts = md.get("sentiment_counts", {}) or {}
        pcts = md.get("sentiment_percent", {}) or {}
        row = {
            "product_id": d.get("product_id"),
            "product_name": d.get("product_name"),
            "text": d.get("text", ""),
            "positive": counts.get("positive", 0),
            "neutral": counts.get("neutral", 0),
            "negative": counts.get("negative", 0),
            "positive_pct": pcts.get("positive_pct", 0.0),
            "neutral_pct": pcts.get("neutral_pct", 0.0),
            "negative_pct": pcts.get("negative_pct", 0.0),
            "avg_sentiment_score": md.get("avg_sentiment_score", None),
            "num_reviews_used": md.get("num_reviews_used", None)
        }
        rows.append(row)
    except Exception as e:
        errors.append((i, str(e)))

print("built rows:", len(rows))
if errors:
    print("errors while building rows:")
    for e in errors:
        print(e)
else:
    print("no errors building rows")
    
products_df = pd.DataFrame(rows)

products_df.to_csv(OUT_DIR/"products_with_sentiment.csv", index=False)
print(f"Saved product docs: {OUT_DIR/'products_with_sentiment.csv'}")


# --- build a quick lookup map from product_id -> sentiment stats (from docs list) ---
stats_map = {}
for d in docs:
    pid = d["product_id"]
    md = d.get("metadata", {})
    counts = md.get("sentiment_counts", {})
    pcts = md.get("sentiment_percent", {})
    stats_map[pid] = {
        "positive_count": counts.get("positive", 0),
        "neutral_count": counts.get("neutral", 0),
        "negative_count": counts.get("negative", 0),
        "positive_pct": pcts.get("positive_pct", 0.0),
        "neutral_pct": pcts.get("neutral_pct", 0.0),
        "negative_pct": pcts.get("negative_pct", 0.0),
        "avg_sentiment_score": md.get("avg_sentiment_score", None),
        "num_reviews_used": md.get("num_reviews_used", None),
    }

# Also write review-level table: keep product_id, review text, rating plus product sentiment stats
rows = []
for _, r in df.iterrows():
    prod = r[product_col]
    prod_id = r[product_id_col]
    text = str(r.get(review_col, "")).strip()
    rating = r.get(rating_col, None)

    # fetch stats for this product_id (fallback to zeros if not found)
    stats = stats_map.get(prod_id, {
        "positive_count": 0,
        "neutral_count": 0,
        "negative_count": 0,
        "positive_pct": 0.0,
        "neutral_pct": 0.0,
        "negative_pct": 0.0,
        "avg_sentiment_score": None,
        "num_reviews_used": None,
    })

    # include original sentiment_label/score for each review if present in df
    sentiment_label = r.get("sentiment_label", None) if "sentiment_label" in r.index else None
    sentiment_score = r.get("sentiment_score", None) if "sentiment_score" in r.index else None

    rows.append({
        "product_id": prod_id,
        "product_name": prod,
        "review_text": text,
        "rating": rating,
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
        # product-level sentiment summary fields
        "positive_count": stats["positive_count"],
        "neutral_count": stats["neutral_count"],
        "negative_count": stats["negative_count"],
        "positive_pct": stats["positive_pct"],
        "neutral_pct": stats["neutral_pct"],
        "negative_pct": stats["negative_pct"],
        "avg_sentiment_score": stats["avg_sentiment_score"],
        "num_reviews_used": stats["num_reviews_used"],
    })

reviews_with_sentiment_df = pd.DataFrame(rows)

# Optionally reorder columns for readability
cols_order = [
    "product_id", "product_name", "review_text", "rating",
    "sentiment_label", "sentiment_score",
    "positive_count", "neutral_count", "negative_count",
    "positive_pct", "neutral_pct", "negative_pct",
    "avg_sentiment_score", "num_reviews_used"
]
existing_cols = [c for c in cols_order if c in reviews_with_sentiment_df.columns]
other_cols = [c for c in reviews_with_sentiment_df.columns if c not in existing_cols]
final_cols = existing_cols + other_cols
reviews_with_sentiment_df = reviews_with_sentiment_df[final_cols]

reviews_with_sentiment_df.to_csv(OUT_DIR/"reviews_with_sentiment.csv", index=False)
print(f"Saved review snippets with product-level sentiment: {OUT_DIR/'reviews_with_sentiment.csv'}")
