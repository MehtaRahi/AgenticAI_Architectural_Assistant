import os
import argparse
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

def ingest_document(file_path: str, collection_name: str = "building_codes"):
    print(f"Starting ingestion for: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Load document
    print("Loading document...")
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    print(f"Loaded {len(docs)} pages.")

    # Split document
    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Created {len(chunks)} text chunks.")

    # Initialize embeddings and ChromaDB
    print("Initializing embeddings and vector store...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    persist_directory = str(Path(__file__).parent.parent / ".chroma")
    
    # Upsert to ChromaDB
    print(f"Upserting chunks to ChromaDB collection '{collection_name}' at {persist_directory}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    
    print("Ingestion complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest architectural documents into ChromaDB.")
    parser.add_argument("--file", type=str, default="data/raw/2010-design-standards.pdf", help="Path to the PDF file")
    args = parser.parse_args()
    
    ingest_document(args.file)
