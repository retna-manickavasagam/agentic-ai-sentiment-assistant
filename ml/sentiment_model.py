# sentiment_model.py
# Zero-shot classifier for 3-label sentiment: positive / neutral / negative
from transformers import pipeline
import torch

def get_classifier(device=None, model_name="facebook/bart-large-mnli"):
    """
    Returns a Hugging Face zero-shot-classification pipeline.
    Automatically uses GPU if available (device=0), otherwise CPU (device=-1).
    """
    if device is None:
        device = 0 if torch.cuda.is_available() else -1
    classifier = pipeline("zero-shot-classification", model=model_name, device=device)
    return classifier

def analyze_texts(texts, classifier=None, candidate_labels=None, batch_size=8):
    """
    texts: list[str]
    classifier: pipeline object (from get_classifier)
    candidate_labels: list[str] e.g. ["positive","neutral","negative"]
    batch_size: process in batches to avoid OOM
    returns: list of dicts: {"label":..., "score":...}
    """
    if candidate_labels is None:
        candidate_labels = ["positive", "neutral", "negative"]
    if classifier is None:
        classifier = get_classifier()

    results = []
    # The pipeline accepts a list or single string; when given a list returns list of outputs
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        out = classifier(batch, candidate_labels, multi_label=False)
        # out is a list of dicts when input is list
        for o in out:
            label = o["labels"][0].lower()
            score = float(o["scores"][0])
            results.append({"label": label, "score": score})
    return results
