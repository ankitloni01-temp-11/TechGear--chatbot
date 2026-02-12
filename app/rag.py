import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from app.prompt_loader import load_prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()

# Configuration
CHROMA_PATH = "data/chroma_db"

def get_rag_chain():
    # 1. Initialize Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    if not os.path.exists(CHROMA_PATH):
        raise FileNotFoundError(f"ChromaDB not found at {CHROMA_PATH}. Run ingest first.")
        
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    
    # 2. Define LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.3,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # 3. Create Retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    
    # 4. Define Prompts
    
    # Prompt for rephrasing the question
    rephrase_prompt = load_prompt("rephrase")
    rephrase_chain = rephrase_prompt | llm | StrOutputParser()

    # Prompt for answering the rephrased question
    prompt = load_prompt("rag")
    
    # 5. Build Chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def route_query(input_data):
        question = input_data["question"]
        history = input_data.get("history", [])
        
        if not history:
            return question
        
        # Convert history list to string for the prompt
        history_str = "\n".join([f"User: {h['question']}\nBot: {h['response']}" for h in history])
        return rephrase_chain.invoke({"history": history_str, "question": question})

    # The final chain:
    # 1. Rephrase (if history exists)
    # 2. Retrieve
    # 3. Answer
    rag_chain = (
        {"context": route_query | retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

if __name__ == "__main__":
    # Test the chain
    try:
        chain = get_rag_chain()
        # Mocking a conversation
        history = [
            {"question": "Which of the powerbanks are USB-C?", "response": "We have the Pro Power Bank and Max Power Bank with USB-C."}
        ]
        response = chain.invoke({"question": "which is the cheapest among these?", "history": history})
        print(f"Test Response:\n{response}")
    except Exception as e:
        print(f"Error testing RAG chain: {e}")
