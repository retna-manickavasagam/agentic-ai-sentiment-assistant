# scripts/prepare_docs.py
import pandas as pd
import hashlib
from pathlib import Path

INPUT = "data/raw/raw.csv"
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# read raw csv
df = pd.read_csv(INPUT, dtype={1: str, 10: str})
#print(df.columns.tolist())
df = df.rename(columns=lambda x: x.strip())
#print('after')
#print(df.columns.tolist())
product_col = "name"  
review_col = "reviews.text"  
rating_col = "reviews.rating"  
category_col = "categories"  

# Fill NAs
df[review_col] = df[review_col].fillna("").astype(str)
df[product_col] = df[product_col].fillna("Unknown Product").astype(str)
df.columns = df.columns.str.strip()

docs = []
for prod, group in df.groupby(product_col):
    # sample up to 10 reviews for the product to build product context
    sample_reviews = group[review_col].dropna().astype(str).tolist()[:10]
    combined = " ".join(sample_reviews)
    category_val = group[category_col].iloc[0] if category_col in group.columns else ""
    summary_text = f"Product: {prod}\nCategories: {category_val}\n\nTop reviews:\n{combined}"
    prod_id = hashlib.md5(prod.encode("utf-8")).hexdigest()[:12]
    docs.append({"product_id": prod_id, "product_name": prod, "text": summary_text})

products_df = pd.DataFrame(docs)
#print(products_df.columns.tolist())
products_df.to_csv(OUT_DIR/"products.csv", index=False)
print(f"Saved product docs: {OUT_DIR/'products.csv'}")


# Also write review-level table: keep product_id, review text, rating
rows = []
for _, r in df.iterrows():
    prod = r[product_col]
    prod_id = hashlib.md5(str(prod).encode("utf-8")).hexdigest()[:12]
    text = str(r.get(review_col, "")).strip()
    rating = r.get(rating_col, None)
    if text:
        rows.append({"product_id": prod_id, "product_name": prod, "review_text": text, "rating": rating})
        
reviews_df = pd.DataFrame(rows)
reviews_df.to_csv(OUT_DIR/"reviews_snippets.csv", index=False)
print(f"Saved review snippets: {OUT_DIR/'reviews_snippets.csv'}")