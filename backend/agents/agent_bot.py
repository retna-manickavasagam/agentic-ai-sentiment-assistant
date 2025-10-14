import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# Import custom tools from agents/api_tools.py
from .api_tools import retrieve_product, retrieve_review_by_id, retrieve_review_by_name, order_product, add_review_tool, send_email

# Initialize the LLM with API Key
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    openai_api_key=openai_api_key
)

# Register your tools as a list
tools = [retrieve_product, retrieve_review_by_id, retrieve_review_by_name, order_product, add_review_tool, send_email]

# Initialize the LangChain agent
def get_agent():
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent
