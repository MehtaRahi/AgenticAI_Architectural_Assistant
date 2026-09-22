from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from pathlib import Path
import os

def researcher_node(state: AgentState) -> dict:
    """
    Researcher Agent: Queries the local ChromaDB Vector Database for building codes.
    """
    query = state.get('query', '')
    
    # Initialize embeddings
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://host.docker.internal:11434"
    )
    
    # Path to ChromaDB - navigate from backend/app/agents/nodes to project root/.chroma
    persist_directory = str(Path(__file__).parent.parent.parent.parent.parent / ".chroma")
    
    retrieved_codes = []
    
    # Try to search ChromaDB if it exists
    if os.path.exists(persist_directory):
        try:
            vectorstore = Chroma(
                collection_name="building_codes",
                embedding_function=embeddings,
                persist_directory=persist_directory
            )
            
            # Retrieve top 3 relevant chunks
            docs = vectorstore.similarity_search(query, k=3)
            retrieved_codes = [doc.page_content for doc in docs]
        except Exception as e:
            retrieved_codes.append(f"Error accessing Vector Store: {str(e)}")
            
    if not retrieved_codes:
        # Fallback if DB isn't populated or fails
        retrieved_codes.append("No specific regulatory code found for the given query. Assuming general architectural best practices apply.")
        
    return {"retrieved_codes": retrieved_codes, "next_node": "reviewer"}
