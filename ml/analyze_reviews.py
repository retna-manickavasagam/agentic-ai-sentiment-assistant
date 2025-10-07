# analyze_reviews.py
import pandas as pd
import argparse
from tqdm import tqdm
from sentiment_model import get_classifier, analyze_texts

COMMON_TEXT_COLS = ["text", "review", "review_text", "comment", "feedback", "body"]

def find_text_column(df, provided=None):
    if provided and provided in df.columns:
        return provided
    for c in COMMON_TEXT_COLS:
        if c in df.columns:
            return c
    # fallback: first string/object column
    for c in df.columns:
        if df[c].dtype == object:
            return c
    raise ValueError("No text column found. Provide --text_col with column name.")

def preprocess_text(s):
    # simple clean: trim and replace newlines — extend as needed
    return str(s).strip().replace("\n", " ").replace("\r", "")

def main(input_path, output_path, text_col, batch_size):
    df = pd.read_csv(input_path)
    text_col = find_text_column(df, text_col)
    print(f"Using text column: {text_col} (rows: {len(df)})")

    texts = df[text_col].fillna("").astype(str).apply(preprocess_text).tolist()

    classifier = get_classifier()  # will auto-select GPU if available
    print("Classifier loaded. Processing in batches...")

    results = analyze_texts(texts, classifier=classifier, batch_size=batch_size)

    df["sentiment_label"] = [r["label"] for r in results]
    df["sentiment_score"] = [r["score"] for r in results]

    df.to_csv(output_path, index=False)
    print(f"Saved results to {output_path}")
    print("Label counts:")
    print(df["sentiment_label"].value_counts())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch sentiment analysis (positive/neutral/negative)")
    parser.add_argument("--input", "-i", required=True, help="Input CSV path (must contain a text column)")
    parser.add_argument("--output", "-o", default="sentiment_output.csv", help="Output CSV path")
    parser.add_argument("--text_col", default=None, help="Name of text column (auto-detected if omitted)")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size (reduce if OOM)")
    args = parser.parse_args()
    main(args.input, args.output, args.text_col, args.batch_size)
