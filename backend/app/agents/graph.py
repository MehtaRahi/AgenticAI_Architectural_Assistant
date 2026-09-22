from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.designer import designer_node
from app.agents.nodes.researcher import researcher_node
from app.agents.nodes.reviewer import reviewer_node

def route_planner(state: AgentState):
    """Route from planner node."""
    if state.get("next_node") == "designer":
        return "designer"
    return END

def route_designer(state: AgentState):
    """Route from designer node."""
    if state.get("next_node") == "researcher":
        return "researcher"
    return END

def route_researcher(state: AgentState):
    """Route from researcher node."""
    if state.get("next_node") == "reviewer":
        return "reviewer"
    return END

def build_graph():
    """Build and compile the multi-agent graph."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("designer", designer_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("reviewer", reviewer_node)
    
    # Add edges
    workflow.set_entry_point("planner")
    
    workflow.add_conditional_edges(
        "planner",
        route_planner,
        {
            "designer": "designer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "designer",
        route_designer,
        {
            "researcher": "researcher",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "researcher",
        route_researcher,
        {
            "reviewer": "reviewer",
            END: END
        }
    )
    
    workflow.add_edge("reviewer", END)
    
    return workflow.compile()
