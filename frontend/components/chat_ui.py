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
            st.markdown(msg["content"])

    # Input
    prompt = st.chat_input("Ask about building codes or request a design review...")
    if prompt:
        _send(prompt)


def _send(text: str):
    """Append user message, generate simulated agentic reply, rerun."""
    st.session_state.chat_history.append({"role": "user", "content": text, "tools": []})

    low = text.lower()

    if any(k in low for k in ("hallway", "cubicasa", "corridor", "width")):
        tools = ["AnalyzeFloorPlanTool", "SearchBuildingCodeTool", "CheckComplianceTool"]
        reply = (
            "### Compliance Review — `cubicasa_sample_1.json`\n\n"
            "| Element | Measured | Required | Status |\n"
            "|---------|----------|----------|--------|\n"
            "| Hallway (room_2) clear width | **3.0 ft** (36 in) | **3.5 ft** (42 in) | Non-compliant |\n"
            "| Master Bedroom area | 224.0 sq ft | 120.0 sq ft min | Compliant |\n"
            "| Master Bedroom width | 14.0 ft | 10.0 ft min | Compliant |\n\n"
            "> **Recommendation**: Shift the southern partition wall outward by 6 inches "
            "to achieve 3.5 ft corridor clearance per Residential Building Code S101.2."
        )
    elif any(k in low for k in ("door", "404", "entrance")):
        tools = ["SearchBuildingCodeTool"]
        reply = (
            "**ADA 2010 — Section 404.2.3 (Clear Width)**\n\n"
            "> Door openings shall provide a clear width of **32 inches (815 mm) minimum**, "
            "measured between the face of the door and the stop with the door open 90 degrees.\n\n"
            "Maneuvering clearance requires 60 in perpendicular to the doorway (forward approach)."
        )
    elif any(k in low for k in ("kitchen", "804", "aisle")):
        tools = ["SearchBuildingCodeTool"]
        reply = (
            "**ADA 2010 — Section 804 (Kitchens)**\n\n"
            "| Layout | Minimum Clearance |\n"
            "|--------|-------------------|\n"
            "| Pass-through (opposing counters) | **40 in** (1015 mm) |\n"
            "| U-shaped (enclosed 3 sides) | **60 in** (1525 mm) |\n\n"
            "The wider clearance in U-shaped kitchens is required for wheelchair turnaround."
        )
    else:
        tools = ["SearchBuildingCodeTool"]
        reply = (
            f"I searched the ADA 2010 corpus for *\"{text}\"*. "
            "Please specify a room type or code section for a targeted compliance audit."
        )

    st.session_state.chat_history.append({"role": "assistant", "content": reply, "tools": tools})
    st.rerun()
