from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.rag import get_rag_chain
from app.prompt_loader import load_prompt
import os
from dotenv import load_dotenv

load_dotenv()

# --- State ---
class GraphState(TypedDict):
    question: str
    history: list
    category: str
    response: str

# --- Nodes ---

# 1. Classifier Node
def classifier_node(state: GraphState):
    print("---CLASSIFIER---")
    question = state["question"]
    # We can also pass history to the classifier if needed for context-dependent routing
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    prompt = load_prompt("classifier")
    chain = prompt | llm
    
    category = chain.invoke({"question": question}).content.strip().lower()
    
    # Fallback for safety
    if category not in ["technical", "returns", "general"]:
        category = "general"
        
    return {"category": category}

# 2. RAG Responder Node
def rag_node(state: GraphState):
    print("---RAG---")
    question = state["question"]
    history = state.get("history", [])
    rag_chain = get_rag_chain()
    # Pass both question and history to the RAG chain
    response = rag_chain.invoke({"question": question, "history": history})
    return {"response": response}

# 3. Escalation Node (Supervisor Agent)
def escalation_node(state: GraphState):
    print("---ESCALATION (SUPERVISOR)---")
    question = state["question"]
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.5,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Context (Policy)
    policy_context = """
    Return Policy: 7-day no-questions-asked. Refund in 5-7 business days.
    Support Email: support@techgear.com
    Returns Portal: techgear.com/returns
    """
    
    prompt = load_prompt("escalation")
    chain = prompt | llm
    
    response = chain.invoke({"policy": policy_context, "question": question}).content
    
    return {"response": response}

# --- Conditional Edge ---
def decide_route(state: GraphState):
    return state["category"]

# --- Graph Construction ---
def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("escalation", escalation_node)
    
    workflow.add_edge(START, "classifier")
    
    workflow.add_conditional_edges(
        "classifier",
        decide_route,
        {
            "technical": "rag",
            "general": "rag",
            "returns": "escalation"
        }
    )
    
    workflow.add_edge("rag", END)
    workflow.add_edge("escalation", END)
    
    return workflow.compile()

if __name__ == "__main__":
    app = build_graph()
    
    # Test Technical
    print("\nTest 1 (Technical):")
    res1 = app.invoke({"question": "Does the SmartWatch have GPS?"})
    print(res1["response"])
    
    # Test Returns
    print("\nTest 2 (Returns):")
    res2 = app.invoke({"question": "I want to return my ear buds."})
    print(res2["response"])
