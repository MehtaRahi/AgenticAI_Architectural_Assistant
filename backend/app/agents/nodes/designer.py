from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from langchain_groq import ChatGroq
import json

def designer_node(state: AgentState):
    """
    Designer Agent: Takes constraints and generates a spatial layout.
    """
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.2,
        max_tokens=800
    )
    
    sys_msg = SystemMessage(
        content="You are an expert Architectural Designer. "
        "Your task is to take user room dimensions, constraints, and requirements, and propose a highly logical, structured spatial layout. "
        "Describe the placement of items (e.g., bed, closet, doors). "
        "IMPORTANT: You MUST also output a strict JSON array representing the elements to be drawn on a 2D floor plan. "
        "Wrap the JSON array in a markdown code block starting with ```json. "
        "Each object in the array must have: 'label' (str), 'x' (float, left position in ft), 'y' (float, top position in ft), "
        "'width' (float in ft), 'height' (float in ft), and 'type' (str: 'room', 'furniture', 'door', 'fixture'). "
        "Assume the origin (0,0) is the top-left corner of the room."
    )
    
    constraints_str = json.dumps(state.get("constraints", {}), indent=2)
    prompt = (
        f"User Query: {state['query']}\n"
        f"Constraints & Dimensions:\n{constraints_str}\n\n"
        "Generate a structured room layout."
    )
    
    human_msg = HumanMessage(content=prompt)
    
    response = llm.invoke([sys_msg, human_msg])
    
    # Store the raw text output in generated_design
    state["generated_design"] = response.content
    state["next_node"] = "researcher"
    
    return state
