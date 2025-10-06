 # RAG endpoint (QA + agent)
 
 # rag.py
import os
import pandas as pd
from typing import List, Dict, Any

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# -------------------------------
# CONFIGURATION
# -------------------------------
dbname = "chroma_db"  # <-- your Chroma DB folder
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..","..", dbname)

# Resolve to absolute path
PERSIST_DIR = os.path.abspath(PERSIST_DIR)
#print(PERSIST_DIR)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PRODUCT_COLLECTION = "product_docs"
REVIEW_COLLECTION = "review_snippets"

# -------------------------------
# INITIALIZE
# -------------------------------
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# Load the persisted Chroma collection for product
product_store = Chroma(
    collection_name=PRODUCT_COLLECTION,
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)
print(product_store._collection.count())
# Load the persisted Chroma collection for review
review_store = Chroma(
    collection_name=REVIEW_COLLECTION,
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)
print(review_store._collection.count())
# -------------------------------
# FUNCTION TO QUERY THE DB
# -------------------------------
def query_docs(query_text: str, top_k: int = 3):
    """
    Perform a similarity search on the Chroma DB.
    
    Args:
        query_text (str): The user's query.
        top_k (int): Number of top documents to retrieve.
    
    Returns:
        list of strings: Retrieved document texts.
    """
    #print('inside')
    results = product_store.similarity_search(query_text, k=top_k)
    return [doc.page_content for doc in results]

# Product discovery: vector search in products collection
# -------------------------
# rag.py
"""
RAG utility: similarity search for products and product reviews using Chroma + HuggingFace embeddings.

Requirements:
  pip install langchain chromadb sentence-transformers

Assumes you have already created/persisted two Chroma collections:
  - collection_name="product_docs"   (metadatas contain 'product_id', 'product_name', 'chunk_id')
  - collection_name="review_snippets" (metadatas contain 'product_id', 'product_name', 'rating')

Persist directory is ./chroma_db by default. Adjust PERSIST_DIR if yours differs.
"""

from typing import List, Dict, Any, Optional
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import os

# Config
PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")
PRODUCT_COLLECTION = "product_docs"
REVIEW_COLLECTION = "review_snippets"
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


# Initialize embedding and Chroma stores (lazy init pattern)
_embeddings = None
_product_store = None
_review_store = None


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def _get_product_store() -> Chroma:
    global _product_store
    if _product_store is None:
        emb = _get_embeddings()
        _product_store = Chroma(collection_name=PRODUCT_COLLECTION, embedding_function=emb, persist_directory=PERSIST_DIR)
    return _product_store


def _get_review_store() -> Chroma:
    global _review_store
    if _review_store is None:
        emb = _get_embeddings()
        _review_store = Chroma(collection_name=REVIEW_COLLECTION, embedding_function=emb, persist_directory=PERSIST_DIR)
    return _review_store


def get_top_products(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Return top-k matching products for a user query using product_docs collection.

    Returns a list of dicts:
      { "product_id": str, "product_name": str, "score": float, "snippet": str, "metadata": {...} }
    """
    if not query or not query.strip():
        return []

    store = _get_product_store()
    retriever = store.as_retriever(search_kwargs={"k": 20})
    docs = retriever.get_relevant_documents(query)

    results = []
    for d in docs:
        md = getattr(d, "metadata", {}) or {}
        # Chroma doc content is in page_content
        snippet = d.page_content if hasattr(d, "page_content") else str(d)
        # Some vectorstores include a 'score' in doc; Chroma via LangChain doc doesn't expose score directly.
        # If you need scores, use chromadb client directly. For now, we return None for score.
        results.append({
            "product_id": md.get("product_id"),
            "product_name": md.get("product_name"),
            "snippet": snippet,
            "metadata": md,
            "score": None
        })
    df = pd.DataFrame(results)

        # Drop duplicate product_ids, keeping the best (lowest) score
    df = df.sort_values("score", ascending=True).drop_duplicates(subset=["product_id"], keep="first")

        # Return top unique 3 products
    top_results = df.head(k).to_dict(orient="records")

    return top_results

def get_reviews_for_product(product_id: Optional[str] = None, product_name: Optional[str] = None, k: int = 5) -> List[Dict[str, Any]]:
    """
    Return top-k review snippets for a product. Provide either product_id or product_name.

    Results: list of dicts:
      { "review_text": str, "rating": Optional[float], "metadata": {...}, "score": Optional[float] }

    If product_id provided, we use Chroma's metadata filtering (if supported).
    If metadata filtering is not supported by your Chroma version, this falls back to retrieving top-k nearest and filtering client-side.
    """
    if not product_id and not product_name:
        raise ValueError("Provide product_id or product_name")

    store = _get_review_store()
    # Attempt metadata filtering if available
    try:
        # langchain's Chroma supports metadata filters via retriever.as_retriever(...) with search_kwargs filter param in some versions.
        # We'll try a straightforward approach: use the client's query interface if available.
        retriever = store.as_retriever(search_kwargs={"k": k})
        # If product_id is provided, we try to filter manually by retrieving more and filtering.
        docs = retriever.get_relevant_documents(product_name if product_name else product_id)
        filtered = []
        for d in docs:
            md = getattr(d, "metadata", {}) or {}
            if product_id and md.get("product_id") == product_id:
                filtered.append(d)
            elif product_name and md.get("product_name") == product_name:
                filtered.append(d)
            # stop when reached k
            if len(filtered) >= k:
                break

        # If we didn't find enough via naive retriever search, do a broader search and filter
        if len(filtered) < k:
            # Do another retrieval with higher k
            docs_more = retriever.get_relevant_documents(product_name if product_name else product_id)
            for d in docs_more:
                md = getattr(d, "metadata", {}) or {}
                if product_id and md.get("product_id") == product_id:
                    if d not in filtered:
                        filtered.append(d)
                    if len(filtered) >= k:
                        break
                elif product_name and md.get("product_name") == product_name:
                    if d not in filtered:
                        filtered.append(d)
                    if len(filtered) >= k:
                        break

        results = []
        for d in filtered[:k]:
            md = getattr(d, "metadata", {}) or {}
            results.append({
                "review_text": d.page_content,
                "rating": md.get("rating"),
                "metadata": md,
                "score": None
            })
        return results

    except Exception as e:
        # Fall back: simple retrieval and filter client-side
        print("Warning: metadata-filter retrieval raised exception, falling back. Error:", e)
        docs = store.similarity_search(product_name if product_name else "", k=50)
        filtered = []
        for d in docs:
            md = getattr(d, "metadata", {}) or {}
            if product_id and md.get("product_id") == product_id:
                filtered.append(d)
            elif product_name and md.get("product_name") == product_name:
                filtered.append(d)
            if len(filtered) >= k:
                break
        return [{"review_text": d.page_content, "rating": d.metadata.get("rating"), "metadata": d.metadata, "score": None} for d in filtered[:k]]

# -------------------------------
# OPTIONAL: QUICK TEST
# -------------------------------
# if __name__ == "__main__":
#     test_query = "Fire HD 8 Tablet"
#     print("Querying Chroma DB for:", test_query)
#     docs = query_docs(test_query)
#     for i, doc in enumerate(docs, 1):
#         print(f"\nResult {i}:\n{doc}")
if __name__ == "__main__":
    q = "tell me about fire hd"
    print(f"Querying top products for: {q}")
    tops = get_top_products(q, k=3)
    for i, p in enumerate(tops, 1):
        print(f"\n[{i}] {p['product_name']} (id={p['product_id']})")
        print("Snippet:", p["snippet"][:400].replace("\n", " "))
    
    # If user wants reviews for the first product:
    if tops:
        pid = tops[0].get("product_id")
        print(f"\nFetching reviews for product_id={pid}")
        revs = get_reviews_for_product(product_id=pid, k=5)
        for j, r in enumerate(revs, 1):
            print(f"\n  Review {j} (rating={r['rating']}): {r['review_text'][:300]}")