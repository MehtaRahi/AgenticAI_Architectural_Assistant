from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from langchain_groq import ChatGroq
import json
import re

def reviewer_node(state: AgentState) -> dict:
    """
    Reviewer Agent: Checks design logic against retrieved building codes.
    """
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
        max_tokens=800
    )
    
    retrieved = "\n".join(state.get('retrieved_codes', []))
    
    sys_msg = SystemMessage(
        content="You are an Architectural Design Review Agent. "
                "You have been provided with building codes. "
                "Evaluate the AI's proposed architectural design layout against these codes. "
                "Output your response strictly as a JSON object with a single key 'findings', "
                "which is a list of objects containing 'element' (str), 'status' (Pass/Fail), and 'reason' (str)."
    )
    
    prompt = (
        f"Building Codes:\n{retrieved}\n\n"
        f"Proposed Design Layout:\n{state.get('generated_design', '')}\n\n"
        f"Original User Request:\n{state.get('query', '')}"
    )
    messages = [sys_msg, HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    
    findings = []
    try:
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            findings = parsed.get("findings", [])
    except Exception:
        pass
        
    if not findings:
        findings = [{"element": "General", "status": "Unknown", "reason": "Failed to parse LLM evaluation."}]
        
    return {"compliance_findings": findings, "next_node": "end"}
