from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.agents.agent_bot import get_agent, to_empathetic_reply
from backend.agents.orchestrator import handle_user_message


# Define FastAPI router
router = APIRouter(prefix="/api", tags=["agent"])

# Define a request model for chat input
class ChatRequest(BaseModel):
    message: str

# Instantiate the agent globally (alternatively, use dependency injection for session/state)
agent = get_agent()

# The chat endpoint
@router.post("/chat")
async def chat_endpoint(chat_request: ChatRequest, request: Request):
    user_message = chat_request.message
    # Optionally, expose per-user memory by using request.session, user_id, etc.
    response = handle_user_message(user_message, agent)
    empathetic_reply = to_empathetic_reply(response, user_message)
    return {"reply": empathetic_reply}


