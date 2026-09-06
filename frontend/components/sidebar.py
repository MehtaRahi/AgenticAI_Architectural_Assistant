"""Sidebar — Project context and workflow controls only."""
import streamlit as st


def render_sidebar():
    """Lean sidebar: brand, project picker, workflow mode, and session reset."""
    with st.sidebar:
        # Brand
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:24px;">
                <div style="background:linear-gradient(135deg,#38bdf8,#818cf8);width:36px;height:36px;
                    border-radius:9px;display:flex;align-items:center;justify-content:center;
                    font-weight:800;font-size:1.1rem;color:#fff;">A</div>
                <div>
                    <div style="font-weight:700;font-size:1.05rem;color:#f1f5f9;line-height:1.1;">ArchAgent AI</div>
                    <div style="font-size:0.7rem;color:#64748b;">Architectural Design Assistant</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Active Project
        st.markdown("##### Active Project")
        project = st.selectbox(
            "Project",
            [
                "Sample Residential (eval_001)",
                "Studio Apartment 101",
                "Modern Flat — Island Kitchen",
                "Commercial Retail Space",
                "Custom Upload",
            ],
            index=0,
            label_visibility="collapsed",
            key="sidebar_project",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("New / Edit Project", use_container_width=True):
            st.switch_page("pages/0_Project_Setup.py")

        st.markdown("---")

        st.markdown("##### Review Mode")
        mode = st.radio(
            "Mode",
            ["Autonomous Review", "Interactive Q&A", "Strict Code Audit"],
            index=0,
            label_visibility="collapsed",
            key="sidebar_mode",
        )

        st.markdown("---")

        # Status Indicator
        st.markdown(
            """
            <div style="font-size:0.78rem;color:#64748b;line-height:1.7;">
                <div>● <span style="color:#34d399;">Ollama llama3.1</span> — Running locally</div>
                <div>● <span style="color:#34d399;">ChromaDB</span> — Ready</div>
                <div>● <span style="color:#34d399;">FastAPI</span> — Listening :8000</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if st.button("Reset Session", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    return project
