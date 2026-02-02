from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.rag import get_rag_chain
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
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    template = """You are a customer support query routing assistant.
    Analyze the user's question and classify it into one of the following categories:
    
    - technical: Questions about product features, specs, how-to, or compatibility.
    - returns: Questions about returning products, refunds, or warranty claims.
    - general: Greetings, general inquiries, or unclear utility.
    
    Return ONLY the category name (technical, returns, or general).
    
    Question: {question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
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
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)
    
    # Context (Policy)
    policy_context = """
    Return Policy: 7-day no-questions-asked. Refund in 5-7 business days.
    Support Email: support@techgear.com
    Returns Portal: techgear.com/returns
    """
    
    template = """You are a senior Support Supervisor at TechGear Electronics.
    A customer is asking about returns or has a complaint.
    
    Your goal is to:
    1. Be empathetic and professional. Acknowledge their situation.
    2. Clearly explain our 7-day no-questions-asked return policy.
    3. Guide them to use the Returns Portal or email support.
    
    Formatting Guidelines:
    - Use a natural, empathetic tone.
    - If listing steps or info, place each on a new line.
    - Do NOT use markdown bolding (e.g., **text**) or asterisks for bullets.
    
    Policy Info:
    {policy}
    
    Customer Query: {question}
    
    Response:"""
    
    prompt = ChatPromptTemplate.from_template(template)
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
