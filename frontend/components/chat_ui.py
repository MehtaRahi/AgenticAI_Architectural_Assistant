"""Interactive copilot chat — suggestion chips + tool execution badges."""
import streamlit as st


def render_chat_interface():
    """Chat stream with persistent history, quick-fire chips, and tool pills."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Welcome! I'm your **Architectural Design Assistant**.\n\n"
                    "I can review floor plans for code compliance, search ADA 2010 standards, "
                    "or answer questions about dimensional requirements. What would you like to check?"
                ),
                "tools": [],
            }
        ]

    # Suggestion Chips
    cols = st.columns(3)
    if cols[0].button("Hallway Compliance", key="chip_hw", use_container_width=True):
        _send("Does the hallway in cubicasa_sample_1.json comply with minimum width requirements?")
    if cols[1].button("Door Clear Width", key="chip_dr", use_container_width=True):
        _send("What is the minimum clear width required for doorways under ADA Section 404?")
    if cols[2].button("Kitchen Clearance", key="chip_kt", use_container_width=True):
        _send("What clearance is required for pass-through and U-shaped kitchens?")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Message Stream
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("tools"):
                pills = "".join(f'<span class="tool-pill">{t}</span>' for t in msg["tools"])
                st.markdown(f"<div style='margin-bottom:6px'>{pills}</div>", unsafe_allow_html=True)
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Input
    prompt = st.chat_input("Ask about building codes or request a design review...")
    if prompt:
        _send(prompt)


import requests

def render_svg_floorplan(elements: list) -> str:
    if not elements:
        return ""
    
    # Simple scaling: 1 ft = 30px
    SCALE = 30
    
    # Calculate bounds
    max_x = max([(el.get("x", 0) + el.get("width", 0)) for el in elements] + [12])
    max_y = max([(el.get("y", 0) + el.get("height", 0)) for el in elements] + [12])
    
    w = max_x * SCALE + 40
    h = max_y * SCALE + 40
    
    svg = f'<svg width="{w}" height="{h}" style="background-color: #ffffff; border: 1px solid #ccc; margin: 10px 0; font-family: monospace;">'
    
    # Draw elements (rooms first, then others)
    for el in sorted(elements, key=lambda e: 0 if e.get("type") == "room" else 1):
        ex = el.get("x", 0) * SCALE + 20
        ey = el.get("y", 0) * SCALE + 20
        ew = el.get("width", 0) * SCALE
        eh = el.get("height", 0) * SCALE
        etype = el.get("type", "furniture")
        
        if etype == "room":
            # Thick black outline for walls
            svg += f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="none" stroke="#000000" stroke-width="3" />'
            # Add room label and dimensions at the top center
            w_ft = el.get("width", 0)
            h_ft = el.get("height", 0)
            label = el.get("label", "ROOM").upper()
            svg += f'<text x="{ex+ew/2}" y="{ey+20}" fill="#000000" font-size="12" font-weight="bold" text-anchor="middle">{label}</text>'
            svg += f'<text x="{ex+ew/2}" y="{ey+35}" fill="#000000" font-size="10" text-anchor="middle">{w_ft}\' x {h_ft}\'</text>'
        elif etype == "door":
            # Simple door representation
            svg += f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="#ffffff" stroke="#000000" stroke-width="1.5" stroke-dasharray="2,2" />'
            svg += f'<text x="{ex+ew/2}" y="{ey+eh/2+3}" fill="#000000" font-size="9" text-anchor="middle">DOOR</text>'
        else:
            # Thin black outline for furniture/fixtures
            svg += f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="#ffffff" fill-opacity="0.7" stroke="#000000" stroke-width="1" />'
            # Add label and dimensions
            text_x = ex + ew/2
            text_y = ey + eh/2
            w_ft = el.get("width", 0)
            h_ft = el.get("height", 0)
            label = el.get("label", "").upper()
            svg += f'<text x="{text_x}" y="{text_y - 2}" fill="#000000" font-size="10" text-anchor="middle">{label}</text>'
            svg += f'<text x="{text_x}" y="{text_y + 8}" fill="#000000" font-size="8" text-anchor="middle">{w_ft}\' x {h_ft}\'</text>'
        
    svg += '</svg>'
    return svg

def _send(text: str):
    """Append user message, send to FastAPI backend, generate reply, rerun."""
    st.session_state.chat_history.append({"role": "user", "content": text, "tools": []})

    # Format history (exclude the current text which is sent as query)
    history_payload = []
    # Skip the very first initial welcome message, and the one we just appended
    for msg in st.session_state.chat_history[1:-1]:
        history_payload.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Call the FastAPI backend
    import os
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    try:
        response = requests.post(
            f"{backend_url}/api/chat",
            json={
                "query": text, 
                "history": history_payload,
                "constraints": st.session_state.get("design_constraints", {})
            },
            timeout=180
        )
        response.raise_for_status()
        data = response.json()
        
        plan = data.get("plan", [])
        design = data.get("generated_design", "")
        layout_elements = data.get("layout_elements", [])
        codes = data.get("retrieved_codes", [])
        findings = data.get("findings", [])
        
        reply_parts = []
        if design:
            reply_parts.append("### 📐 Proposed Design Layout\n" + design)
            
        if layout_elements:
            svg = render_svg_floorplan(layout_elements)
            reply_parts.append("### 🎨 Native 2D Render\n" + svg)
            
        if plan:
            reply_parts.append("**Execution Plan:**\n" + "\n".join(f"- {p}" for p in plan))
        if codes:
            reply_parts.append("**Retrieved Codes:**\n" + "\n".join(f"> {c}" for c in codes))
        if findings:
            reply_parts.append("**Compliance Findings:**")
            table = "| Element | Status | Reason |\n|---------|--------|--------|\n"
            for f in findings:
                table += f"| {f.get('element')} | {f.get('status')} | {f.get('reason')} |\n"
            reply_parts.append(table)
            
        reply = "\n\n".join(reply_parts)
        if not reply:
            reply = "No insights were generated by the agents."
            
        tools = ["PlannerAgent", "DesignerAgent", "ResearcherAgent", "ReviewerAgent"]
        
    except Exception as e:
        reply = f"Error connecting to AI Backend: {str(e)}"
        tools = ["Error"]

    st.session_state.chat_history.append({"role": "assistant", "content": reply, "tools": tools})
    st.rerun()
