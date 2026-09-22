from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.agents.graph import build_graph
import logging

import mlflow
from langchain_core.messages import HumanMessage, AIMessage

# Enable MLflow autologging for LangChain
mlflow.langchain.autolog()

app = FastAPI(title="Agentic AI Architectural Assistant API")
logger = logging.getLogger(__name__)

# Compile the LangGraph orchestrator
agent_graph = build_graph()

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

class ChatResponse(BaseModel):
    plan: List[str]
    generated_design: Optional[str] = None
    layout_elements: List[Dict[str, Any]] = []
    retrieved_codes: List[str]
    findings: List[ComplianceFinding]

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to trigger the LangGraph multi-agent execution.
    """
    try:
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
        
        # Parse layout elements from JSON block in generated_design
        layout_elements = []
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
            layout_elements, clean_design = extract_json_array(generated_design)
            generated_design = clean_design
            
        # Format response
        findings = [
            ComplianceFinding(**f) for f in final_state.get("compliance_findings", [])
        ]
        
        return ChatResponse(
            plan=final_state.get("current_plan", []),
            generated_design=generated_design,
            layout_elements=layout_elements,
            retrieved_codes=final_state.get("retrieved_codes", []),
            findings=findings
        )
    except Exception as e:
        logger.error(f"Error executing agent graph: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
