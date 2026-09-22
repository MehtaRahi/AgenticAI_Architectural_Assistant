from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from langchain_groq import ChatGroq
import json
import re

def planner_node(state: AgentState) -> dict:
    """
    Planner Agent: Analyzes the query and generates an execution plan.
    """
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
        max_tokens=800
    )
    
    sys_msg = SystemMessage(
        content="You are an expert Architectural Planner Agent. "
                "Analyze the user's architectural query and formulate a step-by-step plan to solve it. "
                "If the user asks for a compliance check, include steps to search codes and review designs. "
                "Output your response strictly as a JSON object with a single key 'plan' containing a list of strings."
    )
    
    messages = [sys_msg, HumanMessage(content=state.get('query', ''))]
    response = llm.invoke(messages)
    
    plan = []
    try:
        # Attempt to parse JSON from the response
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            plan = parsed.get("plan", [])
    except Exception:
        pass
        
    if not plan:
        # Fallback if LLM doesn't output valid JSON
        plan = ["Analyze query", "Execute necessary agent tasks"]
        
    # Always route to the designer in the new design-first flow
    next_node = 'designer'
        
    return {"current_plan": plan, "next_node": next_node}
