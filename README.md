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
