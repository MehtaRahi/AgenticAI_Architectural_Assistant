from typing import TypedDict, Annotated, List, Dict, Any, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    State for the architectural multi-agent workflow.
    """
    # The history of messages in the conversation (human and AI)
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # The user's original query or task
    query: str
    
    # The current execution plan formulated by the Planner
    current_plan: List[str]
    
    # The project constraints (e.g., ADA 2010, specific dimensions)
    constraints: Dict[str, Any]
    
    # The generated design layout
    generated_design: str
    
    # Results from the Code Search / RAG agent
    retrieved_codes: List[str]
    
    # Results from the Design Review agent
    compliance_findings: List[Dict[str, Any]]
    
    # The name of the next node to execute
    next_node: str
