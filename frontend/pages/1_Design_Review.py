"""Design Review Studio — floor plan viewer + compliance audit."""
import streamlit as st
import json
from pathlib import Path
from PIL import Image
from components.sidebar import render_sidebar

st.set_page_config(page_title="Design Review — ArchAgent AI", page_icon="A", layout="wide")

css = Path(__file__).parent.parent / "styles.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

render_sidebar()

# Header
st.markdown(
    """<div style="margin-bottom:20px">
        <h1 style="font-size:1.8rem;font-weight:800;margin:0 0 4px 0">Design Review Studio</h1>
        <p style="color:#94a3b8;font-size:0.92rem;margin:0">
            Inspect plan geometries and run automated code compliance audits.</p>
    </div>""",
    unsafe_allow_html=True,
)

# Controls
base = Path(__file__).parent.parent.parent / "data"
scenarios = base / "scenarios"
raw = base / "raw"

sel_c, code_c = st.columns([2.5, 1])
with sel_c:
    plan = st.selectbox(
        "Floor Plan",
        [
            "cubicasa_sample_1.json — Sample Residential",
            "1.png — Studio Apartment",
            "2png.png — 2-Bedroom Flat",
            "3.png — Commercial / Retail",
            "4.png — Multi-Room Apartment",
            "Upload Custom...",
        ],
    )
with code_c:
    st.selectbox("Standard", ["ADA 2010 + Residential Code 2024", "ADA 2010 (Strict Federal)"], index=0)

st.markdown("---")

# Dual layout
viewer, audit = st.columns([1, 1.15])

# Left: Drawing Viewer
with viewer:
    st.markdown('<div class="section-head">Drawing</div>', unsafe_allow_html=True)

    file_map = {"1.png": "1.png", "2png.png": "2png.png", "3.png": "3.png", "4.png": "4.png", "cubicasa": "1.png"}
    img_key = next((k for k in file_map if k in plan), None)

    if img_key:
        img_path = scenarios / file_map[img_key]
        if img_path.exists():
            st.image(Image.open(img_path), caption=img_path.name, width=None)
    elif "Upload" in plan:
        f = st.file_uploader("Upload floor plan", type=["png", "jpg", "json", "pdf"])
        if f:
            st.success(f"Uploaded: {f.name}")

    # Quick metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Rooms", "2")
    m2.metric("Corridor", "12.0 ft")
    m3.metric("Total Area", "260 sqft")

    with st.expander("View raw JSON geometry"):
        jp = raw / "cubicasa_sample_1.json"
        if jp.exists():
            st.json(json.loads(jp.read_text()))

# Right: Audit
with audit:
    st.markdown('<div class="section-head">Compliance Audit</div>', unsafe_allow_html=True)

    st.button("Run Agentic Review", type="primary", use_container_width=True)

    # Verdict bar
    st.markdown(
        """
        <div style="display:flex;gap:10px;margin:14px 0">
            <div class="glass" style="flex:1;padding:14px 18px">
                <div class="kpi-label">Verdict</div>
                <div style="font-size:1.3rem;font-weight:800;color:#fb7185">FAILED</div>
                <div style="font-size:0.75rem;color:#fb7185">Action required</div>
            </div>
            <div class="glass" style="width:120px;padding:14px 18px">
                <div class="kpi-label">Score</div>
                <div style="font-size:1.3rem;font-weight:800;color:#fbbf24">75%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Findings
    st.markdown("##### Findings")

    # F1 — Non-compliant hallway
    st.markdown(
        """
        <div class="finding fail">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <strong style="color:#f1f5f9">Hallway (room_2) — Clear Width</strong>
                <span class="badge badge-fail">NON-COMPLIANT</span>
            </div>
            <div style="color:#cbd5e1;font-size:0.88rem;margin-bottom:6px">
                Measured <strong>3.0 ft</strong> (36 in). Code requires <strong>3.5 ft</strong> (42 in) for residential egress corridors.
            </div>
            <div class="cite">
                <em>Residential Building Code S101.2 &amp; ADA Advisory 403.5</em><br>
                Shift partition wall southward by 6 in to achieve 3.5 ft clearance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # F2 — Compliant bedroom
    st.markdown(
        """
        <div class="finding pass">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <strong style="color:#f1f5f9">Master Bedroom (room_1) — Dimensions</strong>
                <span class="badge badge-pass">COMPLIANT</span>
            </div>
            <div style="color:#cbd5e1;font-size:0.88rem">
                14.0 ft x 16.0 ft (224 sqft). Exceeds minimum 120 sqft / 10 ft width.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # F3 — Compliant doors
    st.markdown(
        """
        <div class="finding pass">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <strong style="color:#f1f5f9">Door Openings — Clear Width</strong>
                <span class="badge badge-pass">COMPLIANT</span>
            </div>
            <div style="color:#cbd5e1;font-size:0.88rem">
                All 4 doorways >= 32 in clear opening (ADA S404.2.3).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    dl, chat = st.columns(2)
    with dl:
        st.download_button(
            "Export Audit (.md)",
            data="# Compliance Audit\n\n**Status**: Failed\n- Hallway: 3.0 ft -> requires 3.5 ft",
            file_name="audit_sample_001.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with chat:
        if st.button("Discuss with Agent", use_container_width=True):
            st.switch_page("app.py")
