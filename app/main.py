from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse
from app.graph import build_graph
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure GOOGLE_API_KEY is set for LangChain components
if "GEMINI_API_KEY" in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

app = FastAPI(
    title="TechGear RAG Chatbot",
    description="Customer Support Chatbot using RAG and LangGraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Graph and History
conversation_graph = build_graph()
chat_history = []  # Persistent for UI (last 5)
session_context = []  # Memory for the AI assistant

# API Routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a user query through the LangGraph workflow.
    returns: The chatbot response and the classification category.
    """
    try:
        # Invoke Graph with session context
        result = conversation_graph.invoke({
            "question": request.message,
            "history": session_context
        })
        
        response_text = result.get("response", "I'm sorry, I couldn't process that.")
        # Try to get category if available in state, else default
        category = result.get("category", "general")
        timestamp = time.strftime("%H:%M")

        # Store in UI history (last 5 items)
        interaction = {
            "question": request.message,
            "response": response_text,
            "category": category,
            "timestamp": timestamp
        }
        
        chat_history.append(interaction)
        if len(chat_history) > 5:
            chat_history.pop(0)

        # Also store in AI session context
        session_context.append(interaction)

        return ChatResponse(
            response=response_text,
            sender="TechGear Assistant",
            timestamp=timestamp,
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    """Retrieve the last 5 chat interactions."""
    return chat_history

@app.post("/api/restart")
async def restart_chat():
    """Clear the AI session context for a fresh conversation window."""
    global session_context
    session_context = []
    return {"status": "success", "message": "AI session context cleared"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Mount Static Files
app.mount("/", StaticFiles(directory="static", html=True), name="static")
