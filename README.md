# agentic-ai-sentiment-assistant
AI-powered shopping assistant with RAG, sentiment analysis, and Streamlit UI

Once cloned, run these commands in the root folder:
# Create virtual environment (for windows vscode)
python -m venv venv

venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up .env
cp .env.example .env
# (Add your OpenAI API key, PostgreSQL credentials, and email SMTP settings)

# Initialize database
python backend/db.py

# Start backend
uvicorn backend.main:app --reload

# Run frontend
streamlit run frontend/app.py


RAG
1)	Downloaded raw3000.csv
2)	Python scripts/inspect_csv.py
3)	Python scripts/sentiment_prepare_docs.py -> This groups reviews by product and creates product docs and review snippets. (products.csv, review_snippets.csv)
4)	Python scripts/sentiment_chunk_docs.py -> (use LangChain text splitter)
Large product docs or long reviews should be chunked before indexing. Use RecursiveCharacterTextSplitter.
5)	Python ml/embedder.py - Build embeddings & index to Chroma (product chunks + review chunks)
6)	Python ml/rag_engine.py – retrieval from rag for products and reviews
7)	uvicorn backend.main:app --reload --port 8000 – as fast api if we need for another purpose
8) uvicorn backend.main_chat:app --reload --port 8001 - as fast api for chat engine
