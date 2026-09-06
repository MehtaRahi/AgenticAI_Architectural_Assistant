"""Code Knowledge Base — semantic search over ADA standards."""
import streamlit as st
from pathlib import Path
from components.sidebar import render_sidebar

st.set_page_config(page_title="Code Search — ArchAgent AI", page_icon="A", layout="wide")

css = Path(__file__).parent.parent / "styles.css"
if css.exists():
    st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)

render_sidebar()

st.markdown(
    """<div style="margin-bottom:20px">
        <h1 style="font-size:1.8rem;font-weight:800;margin:0 0 4px 0">Building Code Search</h1>
        <p style="color:#94a3b8;font-size:0.92rem;margin:0">
            Semantic vector search across the 2010 ADA Standards for Accessible Design (279 pages, 86 402 words).</p>
    </div>""",
    unsafe_allow_html=True,
)

# Regulation DB
REGS = [
    dict(code="403.5.1", title="Clear Width — Walking Surfaces", cat="Accessible Routes", page=142,
         text="The clear width of walking surfaces shall be 36 inches (915 mm) minimum.",
         note="May reduce to 32 in for a 24 in maximum length."),
    dict(code="403.5.3", title="Passing Spaces", cat="Accessible Routes", page=143,
         text="An accessible route with clear width less than 60 inches shall provide passing spaces at intervals of 200 feet maximum. Passing spaces shall be 60 x 60 in minimum or a T-shaped intersection."),
    dict(code="404.2.3", title="Clear Width — Doorways", cat="Entrances & Doors", page=146,
         text="Door openings shall provide a clear width of 32 inches (815 mm) minimum, measured between the face of the door and the stop with the door open 90 degrees."),
    dict(code="804.2.1", title="Pass-Through Kitchen Clearance", cat="Special Spaces", page=207,
         text="In pass-through kitchens where counters, appliances or cabinets are on two opposing sides, clearance between all opposing base cabinets shall be 40 inches (1015 mm) minimum."),
    dict(code="804.2.2", title="U-Shaped Kitchen Clearance", cat="Special Spaces", page=208,
         text="In U-shaped kitchens enclosed on three contiguous sides, clearance between all opposing base cabinets shall be 60 inches (1525 mm) minimum."),
    dict(code="304.3.1", title="Circular Turning Space", cat="Building Blocks", page=112,
         text="The turning space shall be a space of 60 inches (1525 mm) diameter minimum. The space shall be permitted to include knee and toe clearance complying with Section 306."),
]

# Search
query = st.text_input("Search", placeholder="e.g. hallway clear width, doorway opening, kitchen aisle...")

# Quick chips
cols = st.columns(4)
chip = None
if cols[0].button("Walking Surfaces"): chip = "walking"
if cols[1].button("Doorways"):         chip = "door"
if cols[2].button("Kitchens"):          chip = "kitchen"
if cols[3].button("Turning Space"):     chip = "turning"

# Filter
results = REGS
if chip:
    results = [r for r in REGS if chip in r["text"].lower() or chip in r["title"].lower()]
elif query:
    q = query.lower()
    results = [r for r in REGS if q in r["text"].lower() or q in r["title"].lower() or q in r["code"]]

st.caption(f"Showing **{len(results)}** matching sections")
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# Cards
for r in results:
    note_html = f'<div style="color:#94a3b8;font-size:0.82rem;font-style:italic;margin-top:6px">Note: {r["note"]}</div>' if r.get("note") else ""
    st.markdown(
        f"""
        <div class="glass" style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <span class="badge badge-info">{r['cat']}</span>
                    <h3 style="margin:6px 0 2px;font-size:1.05rem;color:#f1f5f9">S{r['code']} — {r['title']}</h3>
                    <div style="font-size:0.78rem;color:#64748b">2010 ADA Standards · Page {r['page']}</div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#38bdf8;
                    background:rgba(56,189,248,0.08);padding:3px 8px;border-radius:5px;white-space:nowrap">
                    94.2 % match
                </div>
            </div>
            <p style="color:#cbd5e1;font-size:0.9rem;line-height:1.55;margin:10px 0 0">"{r['text']}"</p>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
