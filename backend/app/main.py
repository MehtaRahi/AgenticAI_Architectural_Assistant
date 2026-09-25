from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os

app = FastAPI(title="Agentic AI Architectural Assistant API")

# Add CORS middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ── Lazy initialization ─────────────────────────────────────────────
# We defer heavy imports (mlflow, langgraph, langchain) so the server
# can start and serve /health even if something in the AI stack is broken.
agent_graph = None
_init_error = None

def _init_agent_graph():
    """Attempt to build the agent graph. Called once on first request."""
    global agent_graph, _init_error
    if agent_graph is not None:
        return  # Already initialized
    if _init_error is not None:
        return  # Already tried and failed

    try:
        logger.info("Initializing agent graph...")
        
        # Try MLflow autolog (non-critical)
        try:
            import mlflow
            os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
            mlflow.langchain.autolog()
            logger.info("MLflow autologging enabled.")
        except Exception as e:
            logger.warning(f"MLflow autologging failed (non-critical): {e}")

        from app.agents.graph import build_graph
        agent_graph = build_graph()
        logger.info("Agent graph compiled successfully.")
    except Exception as e:
        _init_error = str(e)
        logger.error(f"FATAL: Failed to initialize agent graph: {e}", exc_info=True)

# ── Models ───────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[ChatMessage]] = []
    constraints: Optional[Dict[str, Any]] = {}

class ComplianceFinding(BaseModel):
    element: str
    status: str
    reason: str

class LayoutVariation(BaseModel):
    variation_name: str
    elements: List[Dict[str, Any]]

class ChatResponse(BaseModel):
    plan: List[str]
    generated_design: Optional[str] = None
    layout_variations: List[LayoutVariation] = []
    retrieved_codes: List[str]
    findings: List[ComplianceFinding]

# ── Endpoints ────────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to trigger the LangGraph multi-agent execution.
    """
    # Lazy-init on first real request
    _init_agent_graph()

    if agent_graph is None:
        raise HTTPException(
            status_code=503,
            detail=f"Agent graph failed to initialize: {_init_error}"
        )

    try:
        from langchain_core.messages import HumanMessage, AIMessage

        # Parse history into LangChain BaseMessage objects
        lc_messages = []
        for msg in request.history:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
                
        # Initialize state
        initial_state = {
            "query": request.query,
            "constraints": request.constraints,
            "messages": lc_messages,
            "current_plan": [],
            "generated_design": "",
            "retrieved_codes": [],
            "compliance_findings": []
        }
        
        # Execute the graph
        final_state = agent_graph.invoke(initial_state)
        
        generated_design = final_state.get("generated_design", "")
        
        # Parse layout variations from JSON block in generated_design
        layout_variations = []
        import re, json
        
        def extract_json_array(text):
            start_idx = text.find('[')
            if start_idx == -1: return [], text
            
            # Remove any markdown codeblock ticks around the json
            clean_text = text[:start_idx].replace('```json', '').replace('```', '').strip()
            
            end_idx = text.rfind(']')
            if end_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx:end_idx+1]), clean_text
                except Exception:
                    pass
            
            # Try to fix cut-off JSON
            json_str = text[start_idx:]
            last_brace = json_str.rfind('}')
            if last_brace != -1:
                try:
                    return json.loads(json_str[:last_brace+1] + ']'), text[:start_idx].strip()
                except Exception:
                    pass
            return [], text
            
        if generated_design:
            parsed_json, clean_design = extract_json_array(generated_design)
            generated_design = clean_design
            
            # The LLM is instructed to return a list of variations
            # e.g. [{"variation_name": "Opt 1", "elements": [...]}]
            # Fallback: if it returned a flat array of elements instead, wrap it in a single variation
            if isinstance(parsed_json, list) and len(parsed_json) > 0:
                if "variation_name" in parsed_json[0]:
                    layout_variations = parsed_json
                else:
                    layout_variations = [{"variation_name": "Standard Layout", "elements": parsed_json}]
            
        # Format response
        findings = []
        for f in final_state.get("compliance_findings", []):
            try:
                findings.append(ComplianceFinding(**f))
            except Exception:
                pass
        
        return ChatResponse(
            plan=final_state.get("current_plan", []),
            generated_design=generated_design,
            layout_variations=layout_variations,
            retrieved_codes=final_state.get("retrieved_codes", []),
            findings=findings
        )
    except Exception as e:
        logger.error(f"Error executing agent graph: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    groq_key = os.environ.get("GROQ_API_KEY", "")
    return {
        "status": "healthy",
        "agent_graph_ready": agent_graph is not None,
        "agent_graph_error": _init_error,
        "groq_api_key_set": bool(groq_key and len(groq_key) > 5),
    }
