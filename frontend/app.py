"""ArchAgent AI — Main Dashboard."""
import streamlit as st
from pathlib import Path
from components.sidebar import render_sidebar
from components.chat_ui import render_chat_interface

st.set_page_config(
    page_title="ArchAgent AI",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
css = Path(__file__).parent / "styles.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

project = render_sidebar()

# Hero
st.markdown(
    """
    <div class="hero">
        <h1>ArchAgent AI</h1>
        <p>Autonomous architectural review — analyse floor plans, verify building code compliance,
        and generate remediation reports powered by LangGraph multi-agent orchestration.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPIs
c1, c2, c3, c4 = st.columns(4)

c1.markdown(
    f"""<div class="glass">
        <div class="kpi-label">Active Project</div>
        <div class="kpi-value" style="font-size:1.15rem">{project.split('(')[0].strip()}</div>
        <div class="kpi-hint">In Review</div>
    </div>""",
    unsafe_allow_html=True,
)
c2.markdown(
    """<div class="glass">
        <div class="kpi-label">Regulations Indexed</div>
        <div class="kpi-value">86 402 <span style="font-size:0.85rem;color:#94a3b8">words</span></div>
        <div class="kpi-hint">ADA 2010 · 279 pages</div>
    </div>""",
    unsafe_allow_html=True,
)
c3.markdown(
    """<div class="glass">
        <div class="kpi-label">Compliance Score</div>
        <div class="kpi-value" style="color:#fbbf24">75%</div>
        <div class="kpi-hint" style="color:#fbbf24">1 infraction detected</div>
    </div>""",
    unsafe_allow_html=True,
)
c4.markdown(
    """<div class="glass">
        <div class="kpi-label">Agent Pipeline</div>
        <div class="kpi-value" style="color:#34d399">Online</div>
        <div class="kpi-hint">LangGraph · 4 nodes</div>
    </div>""",
    unsafe_allow_html=True,
)

# Workspaces
st.markdown('<div class="section-head">Workspaces</div>', unsafe_allow_html=True)

h1, h2 = st.columns(2)
h3, h4 = st.columns(2)

with h1:
    st.markdown(
        """<div class="hub">
            <div class="hub-title">Project Setup</div>
            <div class="hub-desc">Define architectural project scope, set building code requirements,
            and upload contextual documents (IFC, PDF) to MinIO.</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Manage Project", key="go_setup", use_container_width=True):
        st.switch_page("pages/0_Project_Setup.py")

with h2:
    st.markdown(
        """<div class="hub">
            <div class="hub-title">Design Review</div>
            <div class="hub-desc">Upload or select a floor plan, run autonomous compliance audits,
            and export findings with citations.</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Open Review Studio", key="go_review", use_container_width=True):
        st.switch_page("pages/1_Design_Review.py")

with h3:
    st.markdown(
        """<div class="hub">
            <div class="hub-title">Code Search</div>
            <div class="hub-desc">Semantic search across ADA 2010 standards — retrieve exact sections,
            clearances, and dimensional requirements.</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Search Standards", key="go_kb", use_container_width=True):
        st.switch_page("pages/2_Code_Knowledge_Base.py")

with h4:
    st.markdown(
        """<div class="hub">
            <div class="hub-title">Evaluation</div>
            <div class="hub-desc">Run benchmark scenarios, validate agent tool chains,
            and track compliance accuracy with MLflow.</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("View Benchmarks", key="go_eval", use_container_width=True):
        st.switch_page("pages/3_Evaluation.py")


# Copilot
st.markdown('<div class="section-head">Architectural Copilot</div>', unsafe_allow_html=True)
render_chat_interface()
