import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import shutil

# Load environment variables
load_dotenv()

# Configuration
DATA_PATH = "data/knowledge_base.txt"
CHROMA_PATH = "data/chroma_db"

def ingest_data():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    # 1. Load Data
    print("Loading documents...")
    loader = TextLoader(DATA_PATH, encoding="utf-8")
    documents = loader.load()
    print(f"Loaded {len(documents)} document(s).")

    # 2. Split Data
    print("Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 3. Create Embeddings & Store in ChromaDB
    print("Creating embeddings and storing in ChromaDB...")
    
    # Check if DB exists and clear it for fresh ingestion (optional)
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    print(f"Successfully saved to {CHROMA_PATH}")

if __name__ == "__main__":
    ingest_data()
