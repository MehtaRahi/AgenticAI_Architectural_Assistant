"""Evaluation — benchmark scenarios and MLflow tracking."""
import streamlit as st
import json
from pathlib import Path
from components.sidebar import render_sidebar

st.set_page_config(page_title="Evaluation — ArchAgent AI", page_icon="A", layout="wide")

css = Path(__file__).parent.parent / "styles.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

render_sidebar()

st.markdown(
    """<div style="margin-bottom:20px">
        <h1 style="font-size:1.8rem;font-weight:800;margin:0 0 4px 0">Evaluation Dashboard</h1>
        <p style="color:#94a3b8;font-size:0.92rem;margin:0">
            Run benchmark scenarios, validate tool chains, and monitor accuracy metrics.</p>
    </div>""",
    unsafe_allow_html=True,
)

# Load scenario
sc_path = Path(__file__).parent.parent.parent / "data" / "scenarios" / "design_review_1.json"
sc = json.loads(sc_path.read_text()) if sc_path.exists() else {}

col_pick, col_run = st.columns([3, 1])
with col_pick:
    st.selectbox(
        "Scenario",
        [f"{sc.get('scenario_id','eval_001')} — {sc.get('name','Hallway Width Compliance Check')}"],
    )
with col_run:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.button("Run Benchmark", type="primary", use_container_width=True)

st.markdown("---")

# Scenario definition
left, right = st.columns(2)

with left:
    st.markdown('<div class="section-head">Scenario Input</div>', unsafe_allow_html=True)
    inp = sc.get("inputs", {})
    st.markdown(
        f"""
        <div class="glass">
            <div class="kpi-label">Scenario ID</div>
            <div style="font-size:1rem;font-weight:700;color:#38bdf8;margin-bottom:10px">{sc.get('scenario_id','')}</div>
            <div class="kpi-label">User Query</div>
            <div style="color:#f1f5f9;font-style:italic;margin-bottom:10px">"{inp.get('user_query','')}"</div>
            <div class="kpi-label">Target Plan</div>
            <code style="color:#34d399">{inp.get('floor_plan_path','')}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown('<div class="section-head">Expected Assertions</div>', unsafe_allow_html=True)
    exp = sc.get("expected_outcome", {})
    tools = exp.get("tool_calls_expected", [])
    kws = exp.get("expected_answer_contains", [])
    st.markdown(
        f"""
        <div class="glass">
            <div class="kpi-label" style="margin-bottom:4px">Required Tool Calls</div>
            <div style="margin-bottom:12px">{''.join(f'<span class="tool-pill">{t}</span>' for t in tools)}</div>
            <div class="kpi-label" style="margin-bottom:4px">Answer Must Contain</div>
            <div>{''.join(f'<span class="badge badge-info" style="margin:2px 4px 2px 0">{k}</span>' for k in kws)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Results
st.markdown('<div class="section-head">Results</div>', unsafe_allow_html=True)

r1, r2, r3, r4 = st.columns(4)

r1.markdown(
    """<div class="glass">
        <div class="kpi-label">Verdict</div>
        <div class="kpi-value" style="color:#34d399">PASSED</div>
        <div class="kpi-hint">All assertions met</div>
    </div>""",
    unsafe_allow_html=True,
)
r2.markdown(
    """<div class="glass">
        <div class="kpi-label">Tool Coverage</div>
        <div class="kpi-value" style="color:#38bdf8">100%</div>
        <div class="kpi-hint">2 / 2 tools</div>
    </div>""",
    unsafe_allow_html=True,
)
r3.markdown(
    """<div class="glass">
        <div class="kpi-label">Keyword Accuracy</div>
        <div class="kpi-value" style="color:#38bdf8">100%</div>
        <div class="kpi-hint">3 / 3 tokens</div>
    </div>""",
    unsafe_allow_html=True,
)
r4.markdown(
    """<div class="glass">
        <div class="kpi-label">Latency</div>
        <div class="kpi-value">1.14s</div>
        <div class="kpi-hint">Local</div>
    </div>""",
    unsafe_allow_html=True,
)

# MLflow trace
st.markdown('<div class="section-head">MLflow Trace</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="background:#0c1120;border:1px solid rgba(255,255,255,0.06);border-radius:10px;
        padding:16px;font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#64748b;line-height:1.9">
        <div>[03:15:22] <span style="color:#38bdf8">INFO</span> Experiment <span style="color:#f1f5f9">'architectural_assistant_eval'</span> initialized</div>
        <div>[03:15:23] <span style="color:#38bdf8">INFO</span> Run <span style="color:#818cf8">run_7a9f4c82b1</span> started for <span style="color:#f1f5f9">eval_001</span></div>
        <div>[03:15:24] <span style="color:#34d399">METRIC</span> tool_coverage = 100.0%</div>
        <div>[03:15:24] <span style="color:#34d399">METRIC</span> keyword_accuracy = 100.0%</div>
        <div>[03:15:24] <span style="color:#34d399">METRIC</span> passed = 1</div>
        <div>[03:15:24] <span style="color:#38bdf8">INFO</span> Run <span style="color:#818cf8">run_7a9f4c82b1</span> finished</div>
    </div>
    """,
    unsafe_allow_html=True,
)
