import streamlit as st
from openai import OpenAI
import json
import base64
from io import BytesIO
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

st.set_page_config(
    page_title="Clinical NLP Pipeline | MedIntel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL = "gpt-4o-mini"
DATA_DIR = Path(__file__).parent

# ── Brand CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #ffffff !important;
    color: #1a1a2e !important;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* Hide sidebar toggle */
[data-testid="collapsedControl"] { display: none !important; }

/* ── Announcement bar ── */
.coti-announce {
    background: #1a0a3d;
    color: #d0c4f0;
    text-align: center;
    padding: 8px 20px;
    font-size: 0.78rem;
    letter-spacing: 0.02em;
    margin: -1rem -1rem 0 -1rem;
}
.coti-announce b { color: #ffffff; }
.coti-announce span { color: #d4007a; font-weight: 600; cursor: pointer; }

/* ── Navbar ── */
.coti-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 40px;
    background: #ffffff;
    border-bottom: 1px solid #ede8f8;
    margin: 0 -1rem;
    position: sticky;
    top: 0;
    z-index: 100;
}
.coti-logo {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #1a0a3d;
    text-transform: uppercase;
}
.coti-logo span { font-weight: 300; }
.coti-nav-links {
    display: flex;
    gap: 28px;
    font-size: 0.88rem;
    font-weight: 500;
    color: #1a0a3d;
}
.coti-nav-right { display: flex; gap: 12px; align-items: center; }
.btn-outline {
    border: 1.5px solid #1a0a3d;
    color: #1a0a3d;
    background: transparent;
    padding: 7px 16px;
    border-radius: 4px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
}
.btn-magenta {
    background: #d4007a;
    color: #ffffff;
    border: none;
    padding: 8px 18px;
    border-radius: 4px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
}

/* ── Hero banner ── */
.coti-hero {
    background: linear-gradient(135deg, #1a0a3d 0%, #2d1464 50%, #1a0a3d 100%);
    padding: 52px 56px;
    margin: 0 -1rem 0 -1rem;
    position: relative;
    overflow: hidden;
}
.coti-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,0.07) 1px, transparent 1px);
    background-size: 22px 22px;
}
.coti-hero-inner {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 40px;
}
.coti-hero-left { flex: 1; }
.coti-hero-eyebrow {
    color: #d4007a;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.coti-hero h1 {
    color: #ffffff;
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1.18;
    margin: 0 0 16px 0;
}
.coti-hero p {
    color: #c8b8e8;
    font-size: 1rem;
    line-height: 1.65;
    max-width: 520px;
    margin: 0;
}
.coti-hero-stats {
    display: flex;
    gap: 32px;
    flex-shrink: 0;
}
.coti-stat {
    text-align: center;
    border-left: 1px solid rgba(255,255,255,0.15);
    padding-left: 32px;
}
.coti-stat-num {
    font-size: 2.2rem;
    font-weight: 800;
    color: rgba(212,0,122,0.7);
    line-height: 1;
}
.coti-stat-label {
    color: #c8b8e8;
    font-size: 0.78rem;
    line-height: 1.4;
    margin-top: 6px;
    max-width: 110px;
}

/* ── Section label (magenta eyebrow) ── */
.section-label {
    color: #d4007a;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

/* ── Content wrapper ── */
.content-block {
    padding: 32px 0 0 0;
}

/* ── Source badge ── */
.source-badge {
    display: inline-block;
    background: #1a0a3d;
    color: #ffffff;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 3px 10px;
    border-radius: 3px;
    margin-bottom: 10px;
}
.source-badge-magenta {
    background: #d4007a;
    color: #ffffff;
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 3px 10px;
    border-radius: 3px;
    margin-right: 6px;
}

/* ── Patient banner ── */
.patient-banner {
    background: linear-gradient(90deg, #1a0a3d 0%, #2d1464 100%);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
    color: #ffffff;
}
.patient-banner b { color: #ffffff; }
.patient-banner small { color: #c8b8e8; font-size: 0.8rem; }

/* ── Lab value cards ── */
.lab-card {
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 8px;
    text-align: center;
    font-size: 0.83rem;
}
.lab-high { background: #ffeef6; border: 1px solid #f4a0cc; }
.lab-low  { background: #eef2ff; border: 1px solid #a0b4f4; }
.lab-norm { background: #eefaf3; border: 1px solid #7ecfa0; }

/* ── ICD code cards ── */
.icd-card {
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
    background: #fafafa;
}
.icd-card-principal { border-left: 4px solid #d4007a; }
.icd-card-secondary { border-left: 2px solid #e0d4f4; }
.badge-principal {
    background: #d4007a; color: #fff;
    border-radius: 3px; padding: 2px 8px;
    font-size: 0.7rem; font-weight: 700;
    margin-right: 5px;
}
.badge-hcc {
    background: #1a0a3d; color: #fff;
    border-radius: 3px; padding: 2px 8px;
    font-size: 0.7rem; font-weight: 700;
}

/* ── MIMIC panel ── */
.mimic-card {
    border: 1px solid #e0d4f4;
    border-top: 3px solid #2d1464;
    border-radius: 0 0 8px 8px;
    padding: 14px;
    font-size: 0.82rem;
    height: 100%;
}
.mimic-card b { color: #1a0a3d; }
.mimic-hadm { font-size: 1rem; font-weight: 700; color: #2d1464; }

/* ── Streamlit overrides ── */
[data-testid="stTextInput"] input {
    border: 1.5px solid #d0c4f0 !important;
    border-radius: 6px !important;
    font-size: 0.88rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #d4007a !important;
    box-shadow: 0 0 0 2px rgba(212,0,122,0.15) !important;
}
[data-testid="stSelectbox"] > div > div {
    border: 1.5px solid #d0c4f0 !important;
    border-radius: 6px !important;
}
[data-testid="stButton"] > button {
    background: #d4007a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
    letter-spacing: 0.02em !important;
    transition: background 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    background: #b3006a !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 2px solid #e0d4f4 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #666688 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border-bottom: 3px solid transparent !important;
    padding: 8px 16px !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #d4007a !important;
    border-bottom: 3px solid #d4007a !important;
    background: transparent !important;
}
[data-testid="stExpander"] {
    border: 1px solid #e0d4f4 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #1a0a3d !important;
}

/* ── Footer ── */
.coti-footer {
    background: #1a0a3d;
    color: #8878b8;
    text-align: center;
    padding: 20px;
    margin: 40px -1rem -1rem -1rem;
    font-size: 0.78rem;
}
.coti-footer b { color: #d4007a; }

/* Remove default padding from main block */
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; }

/* ── Sidebar dark theme ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0620 0%, #1a0a3d 100%) !important;
    min-width: 270px !important;
    max-width: 300px !important;
}
[data-testid="stSidebarContent"] { padding: 0 16px 24px 16px !important; }
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #ffffff !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.35) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #e8ddf8 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: linear-gradient(135deg,#d4007a,#ff4da6) !important;
    font-size: 0.95rem !important;
    padding: 14px 20px !important;
    box-shadow: 0 4px 15px rgba(212,0,122,0.4) !important;
    border-radius: 8px !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    box-shadow: 0 6px 20px rgba(212,0,122,0.55) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    background: rgba(255,255,255,0.03) !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color: #c8b8e8 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

/* Sidebar brand */
.sb-logo {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #ffffff;
    text-transform: uppercase;
    padding: 20px 0 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 18px;
}
.sb-logo span { font-weight: 300; }
.sb-tagline {
    font-size: 0.62rem;
    color: rgba(200,184,232,0.55);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 3px;
}
.sb-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #d4007a;
    margin: 16px 0 6px 0;
}
.sb-divider { border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 14px 0; }
.sb-note-meta {
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 0.76rem;
    color: #c8b8e8;
    margin-top: 8px;
    border-left: 3px solid #d4007a;
    line-height: 1.5;
}
.sb-note-title { font-weight: 700; color: #ffffff; font-size: 0.83rem; margin-bottom: 3px; }

/* ── KPI strip ── */
.kpi-strip { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; margin-bottom: 14px; }
.kpi-card {
    background: white;
    border: 1px solid #e0d4f4;
    border-top: 3px solid #d4007a;
    border-radius: 0 0 10px 10px;
    padding: 13px 8px;
    text-align: center;
}
.kpi-card-green  { border-top-color: #198754; }
.kpi-card-orange { border-top-color: #e6a817; }
.kpi-card-purple { border-top-color: #1a0a3d; }
.kpi-num  { font-size: 1.65rem; font-weight: 900; color: #1a0a3d; line-height: 1; }
.kpi-label { font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #999; margin-top: 3px; }
.kpi-sub  { font-size: 0.65rem; color: #d4007a; font-weight: 600; margin-top: 2px; }

/* ── Clinical doc header bar ── */
.doc-bar {
    background: linear-gradient(90deg,#1a0a3d,#2d1464);
    border-radius: 8px 8px 0 0;
    padding: 10px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0;
}
.doc-bar-title { font-size: 0.72rem; font-weight: 700; color: #fff; letter-spacing: 0.08em; text-transform: uppercase; }
.doc-bar-badge {
    background: #d4007a; color: #fff;
    font-size: 0.62rem; font-weight: 700;
    padding: 2px 9px; border-radius: 99px; letter-spacing: 0.04em;
}
</style>
""", unsafe_allow_html=True)


# ── Load datasets ─────────────────────────────────────────────────────────────
@st.cache_data
def load_mtsamples():
    with open(DATA_DIR / "mtsamples_notes.json") as f:
        return json.load(f)

@st.cache_data
def load_mimic():
    with open(DATA_DIR / "mimic_context.json") as f:
        return json.load(f)

NOTES = load_mtsamples()
MIMIC = load_mimic()

SPECIALTY_ICONS = {
    "Cardiovascular / Pulmonary": "🫀",
    "Neurology": "🧠",
    "Orthopedic": "🦴",
    "Radiology": "🩻",
    "Discharge Summary": "📋",
    "General Medicine": "🩺",
}

# ── Announcement bar ──────────────────────────────────────────────────────────
st.markdown("""
<div class="coti-announce">
  <b>DEMO</b> &nbsp;·&nbsp; Clinical NLP Pipeline for Healthcare Payment Integrity &nbsp;·&nbsp;
  <span>Intern Assessment Submission →</span>
</div>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="coti-nav">
  <div class="coti-logo"><span>MED</span>INTEL</div>
  <div class="coti-nav-links">
    <span>Clinical NLP</span>
    <span>Data Sources</span>
    <span>Pipeline</span>
    <span>Results</span>
  </div>
  <div class="coti-nav-right">
    <button class="btn-outline">GPT-4o-mini Model</button>
    <button class="btn-magenta">Run Pipeline →</button>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="coti-hero">
  <div class="coti-hero-inner">
    <div class="coti-hero-left">
      <div class="coti-hero-eyebrow">Clinical Natural Language Technology</div>
      <h1>AI-Powered Clinical<br>Document Intelligence</h1>
      <p>Extract structured insights from unstructured clinical notes in real-time.
         Named entity recognition, clinical summarization, and ICD-10 code suggestion
         — powered by GPT-4o-mini on real MTSamples and MIMIC-III data.</p>
    </div>
    <div class="coti-hero-stats">
      <div class="coti-stat">
        <div class="coti-stat-num">$935B</div>
        <div class="coti-stat-label">in wasteful healthcare spending identified annually (JAMA, 2019)</div>
      </div>
      <div class="coti-stat">
        <div class="coti-stat-num">80%</div>
        <div class="coti-stat-label">of health data is unstructured clinical text</div>
      </div>
      <div class="coti-stat">
        <div class="coti-stat-num">3</div>
        <div class="coti-stat-label">NLP tasks run simultaneously per note</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ── API key check ─────────────────────────────────────────────────────────────
try:
    _secret_key = st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    _secret_key = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sb-logo'><span>MED</span>INTEL
    <div class='sb-tagline'>Clinical Intelligence Platform</div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">API Configuration</div>', unsafe_allow_html=True)
    if _secret_key:
        api_key = _secret_key
        st.markdown(
            "<div style='background:rgba(25,135,84,0.15);border:1px solid rgba(25,135,84,0.3);"
            "border-radius:6px;padding:8px 12px;font-size:0.78rem;color:#7ecfa0'>"
            "✅ <b style='color:#aaeec8'>API key loaded</b></div>",
            unsafe_allow_html=True,
        )
    else:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            label_visibility="collapsed",
        )
        st.markdown(
            "<div style='font-size:0.7rem;color:rgba(200,184,232,0.5);margin-top:4px'>"
            "~$0.01 per run · GPT-4o-mini</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Clinical Note Source</div>', unsafe_allow_html=True)
    specialty_choice = st.selectbox(
        "Specialty",
        options=list(NOTES.keys()),
        format_func=lambda k: k,
        label_visibility="collapsed",
    )
    meta = NOTES[specialty_choice]
    st.markdown(
        f"""<div class='sb-note-meta'>
        <div class='sb-note-title'>{meta['name']}</div>
        {meta['description'][:110]}…<br>
        <div style='margin-top:5px;font-size:0.68rem;color:rgba(212,0,122,0.8)'>
        📂 MTSamples · De-identified</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    run_btn = st.button("▶  Run Full NLP Pipeline", use_container_width=True)

    if st.session_state.get("last_risk"):
        r = st.session_state["last_risk"]
        st.markdown(
            f"""<div style='margin-top:14px;background:rgba(212,0,122,0.08);
            border:1px solid rgba(212,0,122,0.2);border-radius:8px;padding:12px 14px'>
            <div style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;
            color:#d4007a;text-transform:uppercase;margin-bottom:8px'>Last Analysis</div>
            <div style='font-size:0.76rem;color:#c8b8e8;display:flex;
            justify-content:space-between;margin-bottom:4px'>
            <span>Risk Score</span>
            <span style='color:#fff;font-weight:700'>{r.get("score","—")}/10 · {r.get("level","—")}</span>
            </div>
            <div style='font-size:0.76rem;color:#c8b8e8;display:flex;justify-content:space-between'>
            <span>30-Day Readmit</span>
            <span style='color:#fff;font-weight:700'>{r.get("readmission_risk","—")}</span>
            </div>
            <div style='font-size:0.76rem;color:#c8b8e8;display:flex;justify-content:space-between;margin-top:4px'>
            <span>Payment Flag</span>
            <span style='color:#fff;font-weight:700'>{r.get("payment_flag","—")}</span>
            </div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    with st.expander("📊  MIMIC-III ICU Records"):
        st.markdown(
            "<div style='font-size:0.7rem;color:rgba(200,184,232,0.5);margin-bottom:8px'>"
            "Beth Israel Deaconess · 100 de-identified patients · PhysioNet ODC</div>",
            unsafe_allow_html=True,
        )
        for pt in MIMIC[:3]:
            st.markdown(
                f"""<div style='border:1px solid rgba(255,255,255,0.1);border-radius:6px;
                padding:8px 10px;margin-bottom:8px'>
                <div style='font-size:0.77rem;font-weight:700;color:#e8ddf8'>
                Adm. {pt['hadm_id']}</div>
                <div style='font-size:0.67rem;color:#d4007a;font-weight:600;
                text-transform:uppercase;letter-spacing:0.06em'>{pt['primary_diagnosis']}</div>
                <div style='font-size:0.68rem;color:rgba(200,184,232,0.55);margin-top:3px'>
                {pt['insurance']} · {pt['admit_date']}</div>
                </div>""",
                unsafe_allow_html=True,
            )

# ── Main area ─────────────────────────────────────────────────────────────────
left, right = st.columns([4, 5], gap="large")

with left:
    st.markdown(
        f"""<div class='doc-bar'>
        <div class='doc-bar-title'>Clinical Document</div>
        <div class='doc-bar-badge'>{specialty_choice}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    input_tab_dataset, input_tab_ocr = st.tabs(["📄  Dataset Note", "📷  OCR Upload"])

    with input_tab_dataset:
        note = st.text_area(
            "note",
            value=meta["note"],
            height=500,
            label_visibility="collapsed",
            key="dataset_note",
        )
        st.markdown(
            f"<div style='font-size:0.71rem;color:#aaa;margin-top:4px'>"
            f"📏 {len(meta['note'].split())} words · MTSamples.com · De-identified</div>",
            unsafe_allow_html=True,
        )

    with input_tab_ocr:
        st.markdown(
            """<div style='background:#f8f5ff;border-left:4px solid #d4007a;
            padding:10px 14px;border-radius:0 6px 6px 0;font-size:0.82rem;
            color:#1a0a3d;margin-bottom:12px'>
            📷 <b>OCR Mode</b> — Upload a photo or scan of any clinical document.
            GPT-4o Vision reads it; the full pipeline runs on the extracted text.
            </div>""",
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload clinical document image",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )
        ocr_note = ""
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded document", use_container_width=True)
            extract_btn = st.button("🔍  Extract Text from Image", use_container_width=True)
            if extract_btn:
                if not api_key:
                    st.error("Enter your OpenAI API key in the sidebar first.")
                else:
                    with st.spinner("Reading image with GPT-4o Vision..."):
                        try:
                            img_bytes = uploaded_file.read()
                            b64 = base64.b64encode(img_bytes).decode("utf-8")
                            ext = uploaded_file.type
                            ocr_client = OpenAI(api_key=api_key)
                            ocr_resp = ocr_client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": [
                                    {"type": "text", "text": (
                                        "This is a clinical medical document. "
                                        "Extract ALL text exactly as written, "
                                        "preserving structure, headings, and medical "
                                        "terminology. Return only the extracted text."
                                    )},
                                    {"type": "image_url", "image_url": {"url": f"data:{ext};base64,{b64}"}},
                                ]}],
                                max_tokens=2000,
                            )
                            ocr_note = ocr_resp.choices[0].message.content or ""
                            st.session_state["ocr_note"] = ocr_note
                        except Exception as e:
                            st.error(f"OCR failed: {e}")

            if "ocr_note" in st.session_state and st.session_state["ocr_note"]:
                st.markdown(
                    "<div class='section-label' style='margin:10px 0 6px'>Extracted Text</div>",
                    unsafe_allow_html=True,
                )
                ocr_note = st.text_area(
                    "ocr_text",
                    value=st.session_state["ocr_note"],
                    height=320,
                    label_visibility="collapsed",
                    key="ocr_text_area",
                )
                st.success("Text extracted — ready to run pipeline.")
        else:
            st.markdown(
                "<div style='text-align:center;padding:50px 20px;color:#9988bb'>"
                "<div style='font-size:2.5rem'>📷</div>"
                "<div style='font-weight:600;margin-top:8px'>Drop an image here</div>"
                "<div style='font-size:0.8rem;margin-top:4px;color:#bbaad4'>"
                "PNG or JPG · handwritten notes · scanned discharge papers</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    ocr_active = (
        "ocr_note" in st.session_state
        and st.session_state.get("ocr_note", "")
        and uploaded_file is not None
    )
    active_note = st.session_state.get("ocr_note", "") if ocr_active else note

with right:
    # KPI strip — visible after any pipeline run
    if st.session_state.get("last_risk") and st.session_state.get("last_entities"):
        rsk = st.session_state["last_risk"]
        ent = st.session_state.get("last_entities") or {}
        cds = st.session_state.get("last_codes") or []
        n_dx   = len(ent.get("diagnoses") or [])
        n_med  = len(ent.get("medications") or [])
        n_hcc  = sum(1 for c in cds if isinstance(c, dict) and c.get("hcc_relevant"))
        score  = rsk.get("score", "—")
        level  = rsk.get("level", "—")
        readmit = rsk.get("readmission_risk", "—")
        sc_color = (
            "#198754" if isinstance(score, int) and score <= 3
            else "#e6a817" if isinstance(score, int) and score <= 6
            else "#d4007a"
        )
        st.markdown(
            f"""<div class='kpi-strip'>
            <div class='kpi-card' style='border-top-color:{sc_color}'>
              <div class='kpi-num' style='color:{sc_color}'>{score}<span style='font-size:0.9rem;color:#ccc;font-weight:400'>/10</span></div>
              <div class='kpi-label'>Risk Score</div>
              <div class='kpi-sub'>{level}</div>
            </div>
            <div class='kpi-card kpi-card-purple'>
              <div class='kpi-num'>{n_dx}</div>
              <div class='kpi-label'>Diagnoses</div>
              <div class='kpi-sub'>{n_med} meds</div>
            </div>
            <div class='kpi-card'>
              <div class='kpi-num'>{len(cds)}</div>
              <div class='kpi-label'>ICD-10</div>
              <div class='kpi-sub'>{n_hcc} HCC</div>
            </div>
            <div class='kpi-card kpi-card-green'>
              <div class='kpi-num' style='font-size:1.1rem'>{readmit}</div>
              <div class='kpi-label'>30-Day Readmit</div>
              <div class='kpi-sub'>{rsk.get("payment_flag","—")}</div>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

    tab_ner, tab_sum, tab_icd, tab_risk, tab_auth, tab_fraud, tab_chat = st.tabs([
        "🔍 Entities",
        "📋 Summary",
        "🏷️ ICD-10",
        "⚠️ Risk Score",
        "🔐 Prior Auth",
        "🚨 Fraud & Waste",
        "💬 Ask the Note",
    ])
    with tab_ner:
        ner_ph = st.empty()
    with tab_sum:
        sum_ph = st.empty()
    with tab_icd:
        icd_ph = st.empty()
    with tab_risk:
        risk_ph = st.empty()
    with tab_auth:
        auth_ph = st.empty()
    with tab_fraud:
        fraud_ph = st.empty()
    with tab_chat:
        chat_ph = st.empty()


# ── NLP helpers ───────────────────────────────────────────────────────────────
def get_text(resp) -> str:
    return resp.choices[0].message.content or ""


def clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.lower().startswith("json"):
            raw = raw[4:]
    return raw.strip()


def run_ner(client, note: str) -> dict:
    prompt = f"""You are a clinical NLP system. Extract structured information from the clinical note.
Return ONLY valid JSON with these keys (use null for missing fields):
- patient: {{name, dob, mrn, age, sex}}
- admission: {{admit_date, discharge_date, attending_physician, los_days}}
- chief_complaint: string
- diagnoses: list of {{name, detail}}
- medications: list of {{name, dose, route, frequency}}
- lab_values: list of {{test, value, unit, flag}} where flag is "high","low","normal"
- vital_signs: {{bp, hr, rr, spo2, temp}}
- procedures: list of strings
- follow_up: list of strings

Clinical Note:
{note[:5000]}

Return only valid JSON."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(get_text(resp))


def stream_summary(client, note: str):
    prompt = f"""You are a clinical documentation specialist. Summarize this clinical note into a
concise handoff summary using this format:

**Patient Overview:** [1-2 sentences]
**Key Clinical Findings:** [3-4 bullet points]
**Treatment / Procedure:** [What was done and outcome]
**Discharge Regimen:** [Medications or post-op instructions]
**Critical Follow-Up:** [Specific actions with timeframes]
**Return-to-Care Criteria:** [Warning signs]

Use physician-level clinical language. Be concise.

Note:
{note[:5000]}"""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def run_icd(client, note: str) -> list:
    prompt = f"""You are a certified medical coder with ICD-10-CM expertise.
Return ONLY a valid JSON object with key "codes" containing a list. Each item:
- code: ICD-10-CM code
- description: official short description
- condition: condition from the note
- justification: brief evidence from note (1 sentence)
- hcc_relevant: true or false
- principal_dx: true or false (only one true)

Clinical Note:
{note[:5000]}

Return only valid JSON."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    parsed = json.loads(get_text(resp))
    return parsed.get("codes", parsed) if isinstance(parsed, dict) else parsed


def run_risk_score(client, note: str) -> dict:
    prompt = f"""You are a clinical risk stratification expert. Analyze this clinical note and
return ONLY a valid JSON object with:
- score: integer 1-10 (1=minimal risk, 10=critical/life-threatening)
- level: one of "LOW", "MODERATE", "HIGH", "CRITICAL"
- summary: one sentence explaining the overall risk level
- drivers: list of exactly 3 strings — the top 3 clinical factors driving the risk score
- readmission_risk: one of "Low", "Moderate", "High" — 30-day hospital readmission risk
- readmission_reason: one sentence explaining the readmission risk
- recommendation: one sentence — most urgent clinical action needed
- payment_flag: one of "Routine", "Complex", "High-Cost" — expected payment complexity for payers

Clinical Note:
{note[:5000]}

Return only valid JSON."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(get_text(resp))


def run_prior_auth(client, note: str) -> list:
    prompt = f"""You are a health plan medical director reviewing a clinical note for prior authorization requirements.
Identify every procedure, service, and high-cost medication in the note.
Return ONLY valid JSON with key "items", each containing:
- service: procedure or service name
- status: "Required" | "May Be Required" | "Not Required"
- reason: one sentence why
- documentation: what the provider must submit (or "N/A")

Clinical Note:
{note[:5000]}

Return only valid JSON."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    parsed = json.loads(get_text(resp))
    return parsed.get("items", [])


def run_fraud_detection(client, note: str) -> list:
    prompt = f"""You are a healthcare payment integrity analyst. Review this clinical note for potential billing compliance concerns from a payer perspective.
Look for: upcoding signals, medical necessity gaps, unbundling indicators, duplicate service risk, documentation deficiencies.
Return ONLY valid JSON with key "flags", each containing:
- flag_type: short category label
- severity: "High" | "Medium" | "Low"
- description: what was found (1-2 sentences)
- evidence: direct quote or reference from the note
- recommendation: action for the payer or provider

If no flags found, return an empty list.

Clinical Note:
{note[:5000]}

Return only valid JSON."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    parsed = json.loads(get_text(resp))
    return parsed.get("flags", [])


def build_export_pdf(note, entities, summary, codes, risk) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER,
                            leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    s = getSampleStyleSheet()
    title_s  = ParagraphStyle("t", fontSize=14, fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#1a0a3d"), spaceAfter=4)
    label_s  = ParagraphStyle("l", fontSize=8, fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#d4007a"),
                               letterSpacing=1, spaceBefore=10, spaceAfter=3)
    body_s   = ParagraphStyle("b", fontSize=9, fontName="Helvetica",
                               textColor=colors.HexColor("#1a1a2e"), leading=14)
    small_s  = ParagraphStyle("sm", fontSize=8, fontName="Helvetica",
                               textColor=colors.HexColor("#555555"), leading=12)
    story = []

    story.append(Paragraph("MedIntel — Clinical NLP Analysis Report", title_s))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#d4007a")))
    story.append(Spacer(1, 6))

    p = (entities or {}).get("patient") or {}
    a = (entities or {}).get("admission") or {}
    story.append(Paragraph("PATIENT", label_s))
    story.append(Paragraph(
        f"{p.get('name','—')} · Age {p.get('age','—')} · {p.get('sex','—')} · MRN: {p.get('mrn','—')}<br/>"
        f"Admitted: {a.get('admit_date','—')} → Discharged: {a.get('discharge_date','—')}",
        body_s))

    story.append(Paragraph("CLINICAL SUMMARY", label_s))
    for line in (summary or "").split("\n"):
        if line.strip():
            story.append(Paragraph(line.replace("**",""), body_s))

    story.append(Paragraph("DIAGNOSES", label_s))
    for dx in (entities or {}).get("diagnoses") or []:
        name = dx.get("name","") if isinstance(dx, dict) else str(dx)
        story.append(Paragraph(f"• {name}", body_s))

    story.append(Paragraph("ICD-10-CM CODES", label_s))
    for c in (codes or []):
        if isinstance(c, dict):
            hcc = "  [HCC]" if c.get("hcc_relevant") else ""
            story.append(Paragraph(f"• {c.get('code','')} — {c.get('description','')}{hcc}", body_s))

    story.append(Paragraph("RISK SCORE", label_s))
    if risk:
        story.append(Paragraph(
            f"Score: {risk.get('score','—')}/10 · Level: {risk.get('level','—')} · "
            f"30-Day Readmission: {risk.get('readmission_risk','—')}",
            body_s))
        story.append(Paragraph(f"Recommendation: {risk.get('recommendation','')}", body_s))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#ddccee")))
    story.append(Paragraph("Generated by MedIntel Clinical NLP Pipeline · Data: MTSamples + MIMIC-III Demo", small_s))

    doc.build(story)
    return buf.getvalue()


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not api_key:
        st.error("Enter your OpenAI API key above.")
        st.stop()
    if not active_note.strip():
        st.error("No clinical note to analyze. Select a dataset note or extract text from an image first.")
        st.stop()

    client = OpenAI(api_key=api_key)

    # Tab 1 — NER
    with tab_ner:
        with ner_ph.container():
            with st.spinner("Extracting clinical entities..."):
                try:
                    entities = run_ner(client, active_note)
                    err = None
                except Exception as e:
                    entities = None; err = str(e)

            if err:
                st.error(f"NER error: {err}")
            elif entities:
                p = entities.get("patient") or {}
                a = entities.get("admission") or {}
                st.markdown(
                    f"""<div class='patient-banner'>
                    <b>👤 {p.get('name') or '—'}</b> &nbsp;·&nbsp;
                    Age {p.get('age') or '—'} &nbsp;·&nbsp; {p.get('sex') or '—'}<br>
                    <small>MRN: {p.get('mrn') or '—'} &nbsp;·&nbsp;
                    Admitted: {a.get('admit_date') or '—'} → {a.get('discharge_date') or '—'} &nbsp;·&nbsp;
                    Attending: {a.get('attending_physician') or '—'}</small>
                    </div>""",
                    unsafe_allow_html=True,
                )
                cc = entities.get("chief_complaint")
                if cc:
                    st.markdown(
                        f"<div style='font-size:0.85rem;color:#1a0a3d;margin-bottom:12px'>"
                        f"<b>Chief Complaint:</b> {cc}</div>",
                        unsafe_allow_html=True,
                    )

                c1, c2 = st.columns(2)
                with c1:
                    dx_list = entities.get("diagnoses") or []
                    if dx_list:
                        st.markdown(
                            "<div class='section-label' style='margin-bottom:6px'>Diagnoses</div>",
                            unsafe_allow_html=True,
                        )
                        for dx in dx_list[:6]:
                            name = dx.get("name","") if isinstance(dx, dict) else str(dx)
                            detail = dx.get("detail","") if isinstance(dx, dict) else ""
                            st.markdown(
                                f"<div style='font-size:0.82rem;padding:4px 0;border-bottom:1px solid #f0eaf8'>"
                                f"<b style='color:#1a0a3d'>{name}</b>"
                                f"{'<br><span style=color:#666688>' + detail + '</span>' if detail else ''}"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                    procs = entities.get("procedures") or []
                    if procs:
                        st.markdown(
                            "<div class='section-label' style='margin:12px 0 6px'>Procedures</div>",
                            unsafe_allow_html=True,
                        )
                        for pr in procs[:4]:
                            st.markdown(f"<div style='font-size:0.82rem;padding:3px 0'>· {pr}</div>",
                                        unsafe_allow_html=True)

                with c2:
                    meds = entities.get("medications") or []
                    if meds:
                        st.markdown(
                            "<div class='section-label' style='margin-bottom:6px'>Medications</div>",
                            unsafe_allow_html=True,
                        )
                        for m in meds[:7]:
                            if isinstance(m, dict):
                                parts = " · ".join(filter(None, [m.get("name"), m.get("dose"), m.get("route"), m.get("frequency")]))
                            else:
                                parts = str(m)
                            st.markdown(
                                f"<div style='font-size:0.82rem;padding:4px 0;border-bottom:1px solid #f0eaf8'>{parts}</div>",
                                unsafe_allow_html=True,
                            )

                labs = entities.get("lab_values") or []
                if labs:
                    st.markdown(
                        "<div class='section-label' style='margin:16px 0 8px'>Lab Values</div>",
                        unsafe_allow_html=True,
                    )
                    lab_cols = st.columns(min(len(labs[:8]), 4))
                    for i, lab in enumerate(labs[:8]):
                        if not isinstance(lab, dict):
                            continue
                        flag = (lab.get("flag") or "normal").lower()
                        css_class = "lab-high" if flag == "high" else ("lab-low" if flag == "low" else "lab-norm")
                        icon = "▲" if flag == "high" else ("▼" if flag == "low" else "✓")
                        with lab_cols[i % 4]:
                            st.markdown(
                                f"<div class='lab-card {css_class}'>"
                                f"<div style='font-weight:700;font-size:0.8rem;color:#1a0a3d'>{lab.get('test','')}</div>"
                                f"<div style='font-size:1rem;font-weight:800;margin:3px 0'>{lab.get('value','')} <span style='font-size:0.7rem;font-weight:400'>{lab.get('unit','')}</span></div>"
                                f"<div style='font-size:0.7rem;font-weight:700'>{icon} {flag.upper()}</div>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )

                n_dx = len(entities.get("diagnoses") or [])
                n_med = len(entities.get("medications") or [])
                st.markdown(
                    f"<div style='margin-top:12px;padding:8px 12px;background:#f8f5ff;"
                    f"border-radius:6px;font-size:0.8rem;color:#1a0a3d'>"
                    f"✅ Extracted <b>{n_dx}</b> diagnoses · <b>{n_med}</b> medications · "
                    f"<b>{len(labs)}</b> lab values</div>",
                    unsafe_allow_html=True,
                )

    # Tab 2 — Streaming summary
    with tab_sum:
        with sum_ph.container():
            st.markdown(
                "<div class='section-label' style='margin-bottom:10px'>Live Clinical Handoff Summary</div>",
                unsafe_allow_html=True,
            )
            box = st.empty()
            full = ""
            try:
                for chunk in stream_summary(client, active_note):
                    full += chunk
                    box.markdown(full + "▌")
                box.markdown(full)
                st.session_state["last_summary"] = full
                st.markdown(
                    "<div style='margin-top:10px;font-size:0.78rem;color:#d4007a;font-weight:600'>"
                    "⚡ Streamed live via GPT-4o-mini</div>",
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"Summary error: {e}")

    # Tab 3 — ICD-10 codes
    with tab_icd:
        with icd_ph.container():
            with st.spinner("Generating ICD-10-CM codes..."):
                try:
                    codes = run_icd(client, active_note)
                    err = None
                except Exception as e:
                    codes = []; err = str(e)

            if err:
                st.error(f"ICD error: {err}")
            elif codes:
                hcc_n = sum(1 for c in codes if isinstance(c, dict) and c.get("hcc_relevant"))
                st.markdown(
                    f"<div style='background:#f8f5ff;border-left:4px solid #d4007a;"
                    f"padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:14px;"
                    f"font-size:0.85rem;color:#1a0a3d'>"
                    f"<b>{len(codes)} ICD-10-CM codes suggested</b> — "
                    f"<b style='color:#d4007a'>{hcc_n} HCC-relevant</b> for risk adjustment</div>",
                    unsafe_allow_html=True,
                )
                for code in codes:
                    if not isinstance(code, dict):
                        continue
                    is_pdx = code.get("principal_dx", False)
                    is_hcc = code.get("hcc_relevant", False)
                    card_class = "icd-card icd-card-principal" if is_pdx else "icd-card icd-card-secondary"
                    badges = ""
                    if is_pdx:
                        badges += "<span class='badge-principal'>⭐ Principal</span>"
                    if is_hcc:
                        badges += "<span class='badge-hcc'>✅ HCC</span>"
                    st.markdown(
                        f"""<div class='{card_class}'>
                        <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                        <div>
                          <span style='font-size:1rem;font-weight:800;color:#1a0a3d'>{code.get('code','')}</span>
                          &nbsp;<span style='font-size:0.85rem;color:#444'>{code.get('description','')}</span>
                        </div>
                        <div>{badges}</div>
                        </div>
                        <div style='font-size:0.78rem;color:#666688;margin-top:5px'>
                        <b style='color:#2d1464'>Condition:</b> {code.get('condition','')} &nbsp;·&nbsp;
                        <b style='color:#2d1464'>Evidence:</b> {code.get('justification','')}
                        </div></div>""",
                        unsafe_allow_html=True,
                    )
                st.success(f"ICD-10 coding complete. {hcc_n} HCC codes flagged for risk adjustment.")

    # Tab 4 — Risk Score
    with tab_risk:
        with risk_ph.container():
            with st.spinner("Calculating patient risk score..."):
                try:
                    risk = run_risk_score(client, active_note)
                    err_risk = None
                except Exception as e:
                    risk = None; err_risk = str(e)

            if err_risk:
                st.error(f"Risk score error: {err_risk}")
            elif risk:
                score = int(risk.get("score", 5))
                level = risk.get("level", "MODERATE")
                summary = risk.get("summary", "")
                drivers = risk.get("drivers", [])
                readmission = risk.get("readmission_risk", "Moderate")
                readmission_reason = risk.get("readmission_reason", "")
                recommendation = risk.get("recommendation", "")
                pay_flag = risk.get("payment_flag", "Routine")

                # Score colors
                if score <= 3:
                    score_color = "#198754"
                    bar_color = "#198754"
                    bg_color = "#eefaf3"
                elif score <= 6:
                    score_color = "#e6a817"
                    bar_color = "#e6a817"
                    bg_color = "#fff8e6"
                elif score <= 8:
                    score_color = "#d4007a"
                    bar_color = "#d4007a"
                    bg_color = "#fff0f8"
                else:
                    score_color = "#8b0000"
                    bar_color = "#8b0000"
                    bg_color = "#fff0f0"

                bar_pct = score * 10

                # ── Main score card ──
                st.markdown(
                    f"""<div style='background:{bg_color};border-radius:12px;
                    padding:24px;text-align:center;margin-bottom:16px;
                    border:2px solid {score_color}33'>
                    <div style='font-size:0.7rem;font-weight:800;color:{score_color};
                    letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px'>
                    Patient Risk Score</div>
                    <div style='font-size:5rem;font-weight:900;color:{score_color};
                    line-height:1'>{score}<span style='font-size:1.5rem;
                    font-weight:400;color:#999'>/10</span></div>
                    <div style='background:#e0e0e0;border-radius:99px;height:10px;
                    margin:14px auto;max-width:280px;overflow:hidden'>
                    <div style='background:{bar_color};width:{bar_pct}%;height:100%;
                    border-radius:99px;transition:width 1s'></div></div>
                    <div style='display:inline-block;background:{score_color};color:white;
                    font-weight:800;font-size:0.85rem;letter-spacing:0.1em;
                    padding:4px 18px;border-radius:99px;margin-top:4px'>{level} RISK</div>
                    <div style='font-size:0.82rem;color:#444;margin-top:12px;
                    font-style:italic'>{summary}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

                # ── Risk drivers ──
                st.markdown(
                    "<div class='section-label' style='margin-bottom:8px'>Top Risk Drivers</div>",
                    unsafe_allow_html=True,
                )
                for i, driver in enumerate(drivers, 1):
                    st.markdown(
                        f"""<div style='display:flex;align-items:flex-start;gap:10px;
                        padding:10px 14px;background:#fafafa;border-radius:8px;
                        margin-bottom:6px;border-left:3px solid {score_color}'>
                        <span style='background:{score_color};color:white;font-weight:800;
                        font-size:0.75rem;border-radius:50%;width:20px;height:20px;
                        display:flex;align-items:center;justify-content:center;
                        flex-shrink:0'>{i}</span>
                        <span style='font-size:0.85rem;color:#1a1a2e'>{driver}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                # ── Bottom metrics row ──
                m1, m2, m3 = st.columns(3)

                readmit_color = (
                    "#198754" if readmission == "Low"
                    else "#e6a817" if readmission == "Moderate"
                    else "#d4007a"
                )
                pay_color = (
                    "#198754" if pay_flag == "Routine"
                    else "#e6a817" if pay_flag == "Complex"
                    else "#d4007a"
                )

                with m1:
                    st.markdown(
                        f"""<div style='border:1px solid #e0d4f4;border-top:3px solid {readmit_color};
                        border-radius:0 0 8px 8px;padding:12px;text-align:center'>
                        <div style='font-size:0.65rem;font-weight:700;color:{readmit_color};
                        letter-spacing:0.1em;text-transform:uppercase'>30-Day Readmission</div>
                        <div style='font-size:1.3rem;font-weight:800;color:{readmit_color};
                        margin:4px 0'>{readmission}</div>
                        <div style='font-size:0.72rem;color:#666'>{readmission_reason}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f"""<div style='border:1px solid #e0d4f4;border-top:3px solid {pay_color};
                        border-radius:0 0 8px 8px;padding:12px;text-align:center'>
                        <div style='font-size:0.65rem;font-weight:700;color:{pay_color};
                        letter-spacing:0.1em;text-transform:uppercase'>Payment Complexity</div>
                        <div style='font-size:1.3rem;font-weight:800;color:{pay_color};
                        margin:4px 0'>{pay_flag}</div>
                        <div style='font-size:0.72rem;color:#666'>Expected payer review level</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with m3:
                    st.markdown(
                        f"""<div style='border:1px solid #e0d4f4;border-top:3px solid #1a0a3d;
                        border-radius:0 0 8px 8px;padding:12px;text-align:center'>
                        <div style='font-size:0.65rem;font-weight:700;color:#1a0a3d;
                        letter-spacing:0.1em;text-transform:uppercase'>Clinical Score</div>
                        <div style='font-size:1.3rem;font-weight:800;color:#1a0a3d;
                        margin:4px 0'>{score}/10</div>
                        <div style='font-size:0.72rem;color:#666'>Acuity-based risk index</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                # ── Recommendation ──
                st.markdown(
                    f"""<div style='margin-top:14px;background:#1a0a3d;border-radius:8px;
                    padding:14px 18px;color:white'>
                    <div style='font-size:0.65rem;font-weight:700;color:#d4007a;
                    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px'>
                    Urgent Clinical Recommendation</div>
                    <div style='font-size:0.88rem;line-height:1.6'>{recommendation}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

    # Persist results for chat + PDF export
    st.session_state["last_note"] = active_note
    st.session_state["last_entities"] = entities if "entities" in dir() else None
    st.session_state["last_codes"] = codes if "codes" in dir() else []
    st.session_state["last_risk"] = risk if "risk" in dir() else None

    # Tab 5 — Prior Auth
    with tab_auth:
        with auth_ph.container():
            with st.spinner("Checking prior authorization requirements..."):
                try:
                    auth_items = run_prior_auth(client, active_note)
                    err_auth = None
                except Exception as e:
                    auth_items = []; err_auth = str(e)

            if err_auth:
                st.error(f"Prior auth error: {err_auth}")
            elif auth_items:
                req_n = sum(1 for i in auth_items if i.get("status") == "Required")
                st.markdown(
                    f"<div style='background:#f8f5ff;border-left:4px solid #d4007a;"
                    f"padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:14px;"
                    f"font-size:0.85rem;color:#1a0a3d'>"
                    f"<b>{len(auth_items)} services reviewed</b> — "
                    f"<b style='color:#d4007a'>{req_n} require prior authorization</b></div>",
                    unsafe_allow_html=True,
                )
                for item in auth_items:
                    status = item.get("status", "")
                    if status == "Required":
                        sc, bg = "#d4007a", "#fff0f8"
                        icon = "🔴"
                    elif status == "May Be Required":
                        sc, bg = "#e6a817", "#fff8e6"
                        icon = "🟡"
                    else:
                        sc, bg = "#198754", "#eefaf3"
                        icon = "🟢"
                    st.markdown(
                        f"""<div style='background:{bg};border:1px solid {sc}33;
                        border-left:4px solid {sc};border-radius:0 8px 8px 0;
                        padding:12px 16px;margin-bottom:10px'>
                        <div style='display:flex;justify-content:space-between;align-items:center'>
                          <div style='font-weight:700;color:#1a0a3d;font-size:0.88rem'>
                            {icon} {item.get("service","")}
                          </div>
                          <div style='background:{sc};color:white;font-size:0.68rem;
                          font-weight:700;padding:3px 10px;border-radius:99px;
                          letter-spacing:0.06em'>{status.upper()}</div>
                        </div>
                        <div style='font-size:0.79rem;color:#444;margin-top:6px'>
                          {item.get("reason","")}
                        </div>
                        <div style='font-size:0.75rem;color:#666688;margin-top:6px;
                        border-top:1px dashed #e0d4f4;padding-top:6px'>
                          <b style='color:#1a0a3d'>Documentation needed:</b>
                          {item.get("documentation","N/A")}
                        </div></div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No prior authorization items identified in this note.")

    # Tab 6 — Fraud & Waste Detection
    with tab_fraud:
        with fraud_ph.container():
            with st.spinner("Scanning for payment integrity flags..."):
                try:
                    flags = run_fraud_detection(client, active_note)
                    err_fraud = None
                except Exception as e:
                    flags = []; err_fraud = str(e)

            if err_fraud:
                st.error(f"Fraud detection error: {err_fraud}")
            elif not flags:
                st.markdown(
                    "<div style='background:#eefaf3;border-left:4px solid #198754;"
                    "padding:14px 16px;border-radius:0 8px 8px 0;margin-bottom:10px'>"
                    "<b style='color:#1a5c35'>✅ No payment integrity flags detected</b><br>"
                    "<span style='font-size:0.82rem;color:#444'>Documentation appears consistent "
                    "with the clinical presentation and services billed.</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                high_n = sum(1 for f in flags if f.get("severity") == "High")
                st.markdown(
                    f"<div style='background:#fff0f8;border-left:4px solid #d4007a;"
                    f"padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:14px;"
                    f"font-size:0.85rem;color:#1a0a3d'>"
                    f"<b>{len(flags)} compliance flags detected</b> — "
                    f"<b style='color:#d4007a'>{high_n} High severity</b></div>",
                    unsafe_allow_html=True,
                )
                for flag in flags:
                    sev = flag.get("severity", "Low")
                    if sev == "High":
                        sc, bg, icon = "#d4007a", "#fff0f8", "🚨"
                    elif sev == "Medium":
                        sc, bg, icon = "#e6a817", "#fff8e6", "⚠️"
                    else:
                        sc, bg, icon = "#888", "#f8f8f8", "ℹ️"
                    st.markdown(
                        f"""<div style='background:{bg};border:1px solid {sc}33;
                        border-left:4px solid {sc};border-radius:0 8px 8px 0;
                        padding:14px 16px;margin-bottom:12px'>
                        <div style='display:flex;justify-content:space-between;align-items:center'>
                          <div style='font-weight:700;color:#1a0a3d;font-size:0.88rem'>
                            {icon} {flag.get("flag_type","")}
                          </div>
                          <div style='background:{sc};color:white;font-size:0.68rem;
                          font-weight:700;padding:3px 10px;border-radius:99px;
                          letter-spacing:0.06em'>{sev.upper()}</div>
                        </div>
                        <div style='font-size:0.82rem;color:#1a1a2e;margin-top:8px;line-height:1.5'>
                          {flag.get("description","")}
                        </div>
                        <div style='font-size:0.75rem;color:#555;margin-top:8px;
                        background:rgba(0,0,0,0.04);padding:6px 10px;border-radius:4px;
                        font-style:italic'>
                          "{flag.get("evidence","")}"
                        </div>
                        <div style='font-size:0.78rem;color:#1a0a3d;margin-top:8px;
                        border-top:1px dashed #e0d4f4;padding-top:8px'>
                          <b>Recommendation:</b> {flag.get("recommendation","")}
                        </div></div>""",
                        unsafe_allow_html=True,
                    )

else:
    with tab_ner:
        ner_ph.markdown(
            "<div style='padding:40px;text-align:center;color:#9988bb'>"
            "<div style='font-size:2rem'>🔍</div>"
            "<div style='font-weight:600;margin-top:8px'>Entity extraction results will appear here</div>"
            "<div style='font-size:0.82rem;margin-top:4px'>Select a specialty and click Run Pipeline</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with tab_sum:
        sum_ph.markdown(
            "<div style='padding:40px;text-align:center;color:#9988bb'>"
            "<div style='font-size:2rem'>📋</div>"
            "<div style='font-weight:600;margin-top:8px'>Summary will stream live here</div>"
            "<div style='font-size:0.82rem;margin-top:4px'>Watch the model generate word-by-word in real-time</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with tab_icd:
        icd_ph.markdown(
            "<div style='padding:40px;text-align:center;color:#9988bb'>"
            "<div style='font-size:2rem'>🏷️</div>"
            "<div style='font-weight:600;margin-top:8px'>ICD-10 codes will appear here</div>"
            "<div style='font-size:0.82rem;margin-top:4px'>HCC-relevant codes flagged for risk adjustment</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with tab_risk:
        risk_ph.markdown(
            "<div style='padding:40px;text-align:center;color:#9988bb'>"
            "<div style='font-size:2rem'>⚠️</div>"
            "<div style='font-weight:600;margin-top:8px'>Patient risk score will appear here</div>"
            "<div style='font-size:0.82rem;margin-top:4px'>Clinical acuity · 30-day readmission · payment complexity</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with tab_auth:
        auth_ph.markdown(
            "<div style='padding:40px;text-align:center;color:#9988bb'>"
            "<div style='font-size:2rem'>🔐</div>"
            "<div style='font-weight:600;margin-top:8px'>Prior authorization check will appear here</div>"
            "<div style='font-size:0.82rem;margin-top:4px'>Run the pipeline to identify services requiring auth</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with tab_fraud:
        fraud_ph.markdown(
            "<div style='padding:40px;text-align:center;color:#9988bb'>"
            "<div style='font-size:2rem'>🚨</div>"
            "<div style='font-weight:600;margin-top:8px'>Fraud &amp; waste flags will appear here</div>"
            "<div style='font-size:0.82rem;margin-top:4px'>Payment integrity analysis runs with the pipeline</div>"
            "</div>",
            unsafe_allow_html=True,
        )

# ── Always-rendered: Ask the Note chat ────────────────────────────────────────
with tab_chat:
    note_for_chat = st.session_state.get("last_note", "")
    if not note_for_chat:
        chat_ph.markdown(
            "<div style='padding:40px;text-align:center;color:#9988bb'>"
            "<div style='font-size:2rem'>💬</div>"
            "<div style='font-weight:600;margin-top:8px'>Run the pipeline first</div>"
            "<div style='font-size:0.82rem;margin-top:4px'>Then come back here to chat with the clinical note</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        chat_ph.empty()
        if not api_key:
            st.warning("Enter your OpenAI API key above to chat.")
        else:
            chat_client = OpenAI(api_key=api_key)
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []

            st.markdown(
                "<div style='background:#f8f5ff;border-left:4px solid #d4007a;"
                "padding:10px 14px;border-radius:0 6px 6px 0;font-size:0.82rem;"
                "color:#1a0a3d;margin-bottom:12px'>"
                "💬 <b>Ask the Note</b> — Ask anything about this clinical document. "
                "The AI answers based only on the note content.</div>",
                unsafe_allow_html=True,
            )

            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_q := st.chat_input("Ask about diagnoses, medications, follow-up, risk factors..."):
                st.session_state.chat_messages.append({"role": "user", "content": user_q})
                with st.chat_message("user"):
                    st.markdown(user_q)

                with st.chat_message("assistant"):
                    resp_box = st.empty()
                    full_resp = ""
                    sys_ctx = (
                        "You are a clinical documentation expert. "
                        "Answer questions based only on this clinical note. "
                        "Be concise and use medical terminology appropriately.\n\n"
                        f"CLINICAL NOTE:\n{note_for_chat[:5000]}"
                    )
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_messages[:-1]
                    ]
                    chat_stream = chat_client.chat.completions.create(
                        model=MODEL,
                        messages=[{"role": "system", "content": sys_ctx}]
                            + history
                            + [{"role": "user", "content": user_q}],
                        stream=True,
                    )
                    for chunk in chat_stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            full_resp += delta
                            resp_box.markdown(full_resp + "▌")
                    resp_box.markdown(full_resp)
                    st.session_state.chat_messages.append({"role": "assistant", "content": full_resp})

# ── PDF Export ────────────────────────────────────────────────────────────────
if st.session_state.get("last_note") and st.session_state.get("last_risk"):
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center'>"
        "<div class='section-label' style='display:inline-block;margin-bottom:12px'>"
        "Export Full Report</div></div>",
        unsafe_allow_html=True,
    )
    exp_col1, exp_col2, exp_col3 = st.columns([1, 2, 1])
    with exp_col2:
        try:
            pdf_bytes = build_export_pdf(
                st.session_state.get("last_note"),
                st.session_state.get("last_entities"),
                st.session_state.get("last_summary"),
                st.session_state.get("last_codes"),
                st.session_state.get("last_risk"),
            )
            st.download_button(
                "📥  Download Full Analysis Report (PDF)",
                data=pdf_bytes,
                file_name="medintel_analysis.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF generation failed: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="coti-footer">
  <b>Clinical NLP Pipeline</b> · Healthcare Payment Integrity · Intern Assessment ·
  Data: MTSamples (mtsamples.com) + MIMIC-III Demo (PhysioNet, ODC License) ·
  Model: GPT-4o-mini
</div>
""", unsafe_allow_html=True)
