# HuggingFace model for sentiment analysis

# Placeholder sentiment model
from transformers import pipeline

sentiment = pipeline("sentiment-analysis")

def analyze_review(text):
    return sentiment(text)
