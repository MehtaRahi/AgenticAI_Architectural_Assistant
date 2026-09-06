"""Project Setup — create projects, define requirements, and upload documents."""
import streamlit as st
from pathlib import Path
from components.sidebar import render_sidebar
import time

st.set_page_config(page_title="Project Setup — ArchAgent AI", page_icon="A", layout="wide")

css = Path(__file__).parent.parent / "styles.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

render_sidebar()

st.markdown(
    """<div style="margin-bottom:20px">
        <h1 style="font-size:1.8rem;font-weight:800;margin:0 0 4px 0">Project Setup</h1>
        <p style="color:#94a3b8;font-size:0.92rem;margin:0">
            Define project scope, set architectural requirements, and build your contextual knowledge base.</p>
    </div>""",
    unsafe_allow_html=True,
)

if "project_files" not in st.session_state:
    st.session_state.project_files = []

# Layout
left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="section-head">1. Project Definition</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.text_input("Project Name", value="Sample Residential (eval_001)")
        st.selectbox("Typology", ["Residential", "Commercial", "Healthcare", "Educational", "Mixed-Use"])
        st.text_area(
            "Project Description", 
            value="A standard single-family residential unit focusing on accessibility and egress compliance.",
            height=100
        )
        
    st.markdown('<div class="section-head">2. Requirements & Constraints</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.multiselect(
            "Governing Building Codes", 
            ["ADA 2010", "IBC 2021", "IRC 2021", "Local Zoning"], 
            default=["ADA 2010", "IRC 2021"]
        )
        st.text_area(
            "Specific Constraints (Text)", 
            placeholder="e.g., Must prioritize wheelchair accessibility in all common areas. Budget capped at $1.2M.",
            height=100
        )
        if st.button("Save Project Configuration", type="primary"):
            st.success("Project settings saved to PostgreSQL.")

with right:
    st.markdown('<div class="section-head">3. Document Hub (MinIO)</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            """<p style="font-size:0.88rem;color:#cbd5e1;margin-bottom:12px;">
            Upload architectural drawings (IFC, PDF) and text documents (DOCX, PDF) to automatically build this project's RAG knowledge base.
            </p>""",
            unsafe_allow_html=True,
        )
        uploaded_files = st.file_uploader(
            "Upload Documents", 
            type=["pdf", "docx", "ifc", "json", "png", "jpg"], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("Process & Index Documents"):
                with st.spinner("Parsing documents and generating embeddings..."):
                    time.sleep(1.5) # Simulate processing
                    for f in uploaded_files:
                        if f.name not in [x["name"] for x in st.session_state.project_files]:
                            st.session_state.project_files.append({"name": f.name, "type": f.name.split('.')[-1].upper(), "status": "Indexed"})
                    st.success("Documents successfully indexed into ChromaDB.")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<strong style='color:#f1f5f9;font-size:0.9rem;'>Project Knowledge Base</strong>", unsafe_allow_html=True)
        
        if not st.session_state.project_files:
            st.info("No documents uploaded yet.")
        else:
            for doc in st.session_state.project_files:
                st.markdown(
                    f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;background:rgba(15,23,42,0.5);border:1px solid rgba(255,255,255,0.06);
                        border-radius:8px;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span class="badge badge-info">{doc['type']}</span>
                            <span style="font-size:0.9rem;color:#f1f5f9;font-family:'JetBrains Mono',monospace;">{doc['name']}</span>
                        </div>
                        <span style="font-size:0.75rem;color:#34d399;">● {doc['status']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
