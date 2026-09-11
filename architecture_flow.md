# System Architecture Flow

Here is the architectural flow representing our current technical decisions and containerized setup:

```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f1f5f9
    classDef backend fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#f1f5f9
    classDef agent fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f1f5f9
    classDef storage fill:#334155,stroke:#fbbf24,stroke-width:2px,color:#f1f5f9
    classDef external fill:#475569,stroke:#94a3b8,stroke-width:2px,stroke-dasharray: 5 5,color:#f1f5f9

    %% Users
    User((Architect /<br/>User)):::external
    
    %% Frontend Layer
    subgraph Frontend Layer
        UI[Streamlit Frontend<br/>Port: 8501]:::frontend
    end

    %% Backend Layer
    subgraph Backend & Orchestration Layer
        API[FastAPI Backend<br/>Port: 8000]:::backend
        LG[LangGraph Orchestrator<br/>State Machine]:::agent
        
        subgraph Specialized Agents
            A1[Project & Setup Agent]:::agent
            A2[Design Review Agent]:::agent
            A3[RAG / Code Search Agent]:::agent
        end
    end

    %% Data & Storage Layer
    subgraph Storage & Tracking Layer (Docker Compose)
        PG[(PostgreSQL<br/>Metadata & MLflow Backend)]:::storage
        MINIO[(MinIO S3<br/>Artifacts & Docs)]:::storage
        CHROMA[(ChromaDB<br/>Vector Store)]:::storage
        MLFLOW[MLflow Tracking Server<br/>Port: 5000]:::storage
    end

    %% External LLM
    OLLAMA{{Ollama + Llama 3.1<br/>Local LLM Engine}}:::external

    %% Connections
    User -- Uploads Plans & Queries --> UI
    UI -- REST API / WebSockets --> API
    API -- Triggers Workflows --> LG
    
    LG --> A1
    LG --> A2
    LG --> A3
    
    A1 & A2 & A3 -- Prompts & Reasoning --> OLLAMA
    
    %% Storage Connections
    A1 -- Stores Docs --> MINIO
    A1 -- Stores Project Meta --> PG
    A3 -- Embeds & Retrieves --> CHROMA
    
    %% MLflow Connections
    LG -- Logs Metrics & Traces --> MLFLOW
    MLFLOW -- Backend Store --> PG
    MLFLOW -- Artifacts --> MINIO
```
