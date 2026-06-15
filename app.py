"""
EEE Career Pathways Platform - CONNECTED TO BACKEND
Uses backend_api.py (EEECareerPlatform) for all data and ML operations.
"""

import os
from dotenv import load_dotenv
load_dotenv()
# Suppress macOS/PyTorch threading mutex warnings from abseil C++ runtime
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GLOG_minloglevel", "3")

import streamlit as st
import re
import sys
import collections
import base64
from pathlib import Path
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ========== Page Configuration — MUST be first Streamlit command ==========
st.set_page_config(
    page_title="NTU EEE Career Pathways Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Premium CSS ==========
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* Global text colour fix — ensures dark text on light backgrounds */
.main .block-container, [data-testid="stMarkdownContainer"],
[data-testid="stText"], [data-testid="stCaptionContainer"],
.stRadio label, .stSelectbox label, .stFileUploader label,
.stCheckbox label, .stTextArea label { color: #1a1a2e !important; }
/* Button text must be white — dark text inherits onto dark Streamlit buttons */
.main button, .main button p, .main button span, .main button div { color: white !important; }

/* Header always above everything */
header[data-testid="stHeader"] {
    z-index: 2147483647 !important;
    position: fixed !important;
}

/* Hide the native Streamlit sidebar arrow — we use our own buttons */
[data-testid="collapsedControl"] { display: none !important; }

/* File uploader button text white */
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] button span,
[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploadDropzone"] button,
[data-testid="stFileUploadDropzone"] button span,
.stFileUploader button, .stFileUploader button span, .stFileUploader button p {
    color: white !important;
    background-color: #3a3a5c !important;
}

/* sidebar chat */
section[data-testid="stSidebar"] { background: #f8f9ff; }
/* Close Panel button — red tint */
section[data-testid="stSidebar"] button[key="close_sidebar_btn"],
section[data-testid="stSidebar"] div:has(button[key="close_sidebar_btn"]) button {
    background: rgba(220,53,69,0.08) !important;
    border: 1.5px solid rgba(220,53,69,0.4) !important;
    color: #c0392b !important;
}
section[data-testid="stSidebar"] .stChatInput { border-top: 1px solid #e0e0e0; padding-top: 6px; }
section[data-testid="stSidebar"] .stButton button { border-radius: 8px !important; font-size: 0.78rem !important; }
section[data-testid="stSidebar"] .stChatInput textarea { font-size: 0.88rem; }
section[data-testid="stSidebar"] button[kind="secondary"] {
    border-radius: 20px !important; font-size: 0.78rem !important;
    padding: 4px 10px !important; border: 1.5px solid #dde !important;
    background: white !important; color: #444 !important;
    transition: all 0.15s !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: #667eea !important; color: white !important; border-color: #667eea !important;
}

.main-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem 3rem; border-radius: 0 0 2rem 2rem;
    margin: -1rem -1rem 2rem -1rem; box-shadow: 0 10px 40px rgba(0,0,0,0.15);
}
.main-header h1 { color: white; font-size: 2.5rem; font-weight: 700; margin: 0; }
.main-header p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem; }

.stTabs [data-baseweb="tab-list"] { gap: 8px; background: white; padding: 0.5rem; border-radius: 1rem; }
.stTabs [data-baseweb="tab"] { padding: 0.8rem 1.5rem; border-radius: 0.8rem; font-weight: 600; color: #1a1a2e !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; }

.glass-card { background: rgba(255,255,255,0.95); border-radius: 1.2rem; padding: 1.8rem; box-shadow: 0 8px 32px rgba(0,0,0,0.08); margin: 1rem 0; color: #1a1a2e; }
.glass-card h4, .glass-card p, .glass-card span { color: #1a1a2e; }
.gradient-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1.2rem; padding: 1.8rem; margin: 1rem 0; }
.gradient-card-blue { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; border-radius: 1.2rem; padding: 1.8rem; margin: 1rem 0; }

.info-box { background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%); border-left: 5px solid #00bcd4; border-radius: 0 1rem 1rem 0; padding: 1.2rem 1.5rem; margin: 1rem 0; color: #1a1a2e; }
.success-box { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-left: 5px solid #4caf50; border-radius: 0 1rem 1rem 0; padding: 1.2rem 1.5rem; margin: 1rem 0; color: #1a1a2e; }
.warning-box { background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-left: 5px solid #ff9800; border-radius: 0 1rem 1rem 0; padding: 1.2rem 1.5rem; margin: 1rem 0; color: #1a1a2e; }

.metric-container { background: white; border-radius: 1rem; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08); color: #1a1a2e; }
.metric-value { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-label { color: #666; font-size: 0.95rem; font-weight: 500; margin-top: 0.5rem; }

.skill-progress { background: #e0e0e0; border-radius: 1rem; height: 12px; overflow: hidden; margin: 0.5rem 0; }
.skill-progress-fill { height: 100%; border-radius: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }

.job-card { background: white; border-radius: 1rem; padding: 1.5rem; margin: 1rem 0; border-left: 5px solid #667eea; box-shadow: 0 4px 15px rgba(0,0,0,0.08); color: #1a1a2e; }
.job-card h4 { color: #1a1a2e; }
.job-card.high-match { border-left-color: #4caf50; }
.job-card.good-match { border-left-color: #2196f3; }
.job-card.medium-match { border-left-color: #ff9800; }

.similarity-badge { display: inline-block; padding: 0.4rem 1rem; border-radius: 2rem; font-weight: 600; font-size: 0.9rem; }
.similarity-high { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
.similarity-good { background: linear-gradient(135deg, #1565c0 0%, #42a5f5 100%); color: white; }
.similarity-medium { background: linear-gradient(135deg, #e65100 0%, #ffa726 100%); color: white; }

.course-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1rem; padding: 1.5rem; margin: 0.8rem 0; }
.section-header { font-size: 1.8rem; font-weight: 700; color: #1e3c72; margin: 2rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 3px solid #667eea; display: inline-block; }
.footer { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 2rem; border-radius: 2rem 2rem 0 0; margin-top: 3rem; text-align: center; }

/* Pill toggle for Tab 1 mode switch */
div[data-testid="stRadio"] { display: flex !important; justify-content: center !important; width: 100% !important; margin: 0 !important; }
div[data-testid="stRadio"] > div {
    display: flex; gap: 0; background: #e4e8ec; border-radius: 2rem;
    padding: 4px; width: 100% !important;
}
div[data-testid="stRadio"] > div > label {
    flex: 1; text-align: center; padding: 0.6rem 1.4rem; border-radius: 2rem; cursor: pointer;
    font-weight: 600; font-size: 0.95rem; color: #1a1a2e !important;
    transition: background 0.3s ease, box-shadow 0.3s ease;
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    box-shadow: 0 2px 8px rgba(30,60,114,0.3);
}
div[data-testid="stRadio"] > div > label:has(input:checked) p,
div[data-testid="stRadio"] > div > label:has(input:checked) span,
div[data-testid="stRadio"] > div > label:has(input:checked) div {
    color: white !important;
}
div[data-testid="stRadio"] > div > label input { display: none; }
/* Expander content — white background, dark text */
[data-testid="stExpander"] { background: white !important; border-radius: 0.5rem; }
[data-testid="stExpander"] details { background: white !important; }
[data-testid="stExpander"] summary { color: #1a1a2e !important; font-weight: 600; }
[data-testid="stExpander"] div[data-testid="stExpanderDetails"] { background: white !important; color: #1a1a2e !important; }
</style>
""", unsafe_allow_html=True)

# ========== Sidebar visibility (CSS-only, no JS needed) ==========
if "sidebar_visible" not in st.session_state:
    st.session_state["sidebar_visible"] = False

if st.session_state["sidebar_visible"]:
    st.markdown("""<style>
    section[data-testid="stSidebar"] {
        display: flex !important; visibility: visible !important;
        transform: none !important; min-width: 244px !important;
    }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
    section[data-testid="stSidebar"] { display: none !important; }
    </style>""", unsafe_allow_html=True)

# ========== Header ==========
_logo_path = Path(__file__).parent / "ntu_eee_logo.png"
_logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode() if _logo_path.exists() else ""
_logo_html = f"<img src='data:image/png;base64,{_logo_b64}' style='height:64px;border-radius:10px;background:white;padding:6px 10px;flex-shrink:0;'>" if _logo_b64 else ""

_hive_path = Path(__file__).parent / "ntu_hive.jpeg"
_hive_b64 = base64.b64encode(_hive_path.read_bytes()).decode() if _hive_path.exists() else ""

_imp_logo_path = Path(__file__).parent / "imperial_logo.png"
_imp_logo_b64 = base64.b64encode(_imp_logo_path.read_bytes()).decode() if _imp_logo_path.exists() else ""

_hive_bg = (
    f"linear-gradient(to right, #1e3c72 0%, #1e3c72 28%, rgba(20,50,110,0.45) 46%, rgba(20,50,110,0.45) 54%, #2a5298 72%, #2a5298 100%),"
    f"url('data:image/jpeg;base64,{_hive_b64}') center/cover no-repeat"
) if _hive_b64 else "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)"

st.markdown(f"""
<div class='main-header' style='background:{_hive_bg};'>
    <div style='display:flex;align-items:center;justify-content:space-between;'>
        <div>
            <h1 style='margin:0;'>NTU EEE Career Pathways Platform</h1>
            <p style='margin:0.3rem 0 0 0;'>Career Exploration Platform for EEE Students | Built in collaboration with Imperial College London</p>
        </div>
        {_logo_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ========== Backend Loading ==========
@st.cache_resource(show_spinner=False)
def _get_platform(_v=2):
    from backend_api import EEECareerPlatform
    platform = EEECareerPlatform()
    platform.load()
    return platform


def load_platform_with_status():
    try:
        return _get_platform(), None
    except Exception as exc:
        return None, str(exc)

platform, err = load_platform_with_status()

if err or platform is None:
    st.error(
        f"**Backend initialisation failed.**\n\n{err}\n\n"
        "Check that all four Excel files exist in the `Data/` folder and that "
        "all Python dependencies are installed."
    )
    st.stop()




# ========== Skill Categorisation ==========
SOFT_SKILL_DIMS = [
    'problem solving', 'analytical thinking', 'critical thinking',
    'teamwork', 'communication skills', 'technical writing',
    'documentation', 'project management', 'time management',
    'attention to detail'
]

def categorize_skills(skills):
    categories = {
        'Programming':  ['python', 'java', 'c++', 'c', 'javascript', 'sql', 'matlab', 'html', 'css'],
        'ML/AI':        ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'computer vision', 'nlp', 'artificial intelligence'],
        'EEE Core':     ['signal processing', 'control systems', 'power systems', 'embedded systems', 'circuit', 'electronics'],
        'Hardware':     ['fpga', 'verilog', 'vhdl', 'pcb', 'microcontroller', 'arduino', 'iot'],
        'Data':         ['data analysis', 'statistics', 'pandas', 'numpy', 'visualization'],
        'Tools':        ['git', 'linux', 'docker', 'matlab'],
        'Soft Skills':  SOFT_SKILL_DIMS,
    }
    result = {}
    for skill in skills:
        skill_lower = skill.lower()
        assigned = False
        for cat, keywords in categories.items():
            if any(kw in skill_lower for kw in keywords):
                result.setdefault(cat, []).append(skill)
                assigned = True
                break
        if not assigned:
            result.setdefault('Other', []).append(skill)
    return result


# Broad keyword indicators per soft skill dimension (scanned against raw CV text)
SOFT_SKILL_KEYWORDS = {
    'problem solving':      ['problem solv', 'troubleshoot', 'debug', 'diagnos', 'resolv', 'root cause'],
    'analytical thinking':  ['analytic', 'analytical', 'data-driven', 'insight', 'interpret', 'evaluat'],
    'critical thinking':    ['critical think', 'assess', 'evaluat', 'judgement', 'judgment', 'decision'],
    'teamwork':             ['team', 'collaborat', 'cooperat', 'cross-functional', 'group project', 'co-worker'],
    'communication skills': ['communicat', 'present', 'report', 'written', 'verbal', 'stakeholder'],
    'technical writing':    ['technical writ', 'documentation', 'report writ', 'technical report', 'spec'],
    'documentation':        ['document', 'wiki', 'readme', 'manual', 'log', 'record'],
    'project management':   ['project manag', 'agile', 'scrum', 'kanban', 'sprint', 'deadline', 'deliverable'],
    'time management':      ['time manag', 'prioriti', 'deadline', 'schedul', 'organis', 'organiz'],
    'attention to detail':  ['attention to detail', 'meticulous', 'thorough', 'accurate', 'precision', 'quality'],
}

def detect_soft_skills_from_text(cv_text: str) -> dict:
    """Scan raw CV text for soft skill indicators. Returns {dim: score 0-100}
    based on the fraction of that dimension's keywords matched."""
    text_lower = cv_text.lower()
    scores = {}
    for dim, keywords in SOFT_SKILL_KEYWORDS.items():
        matched = sum(1 for kw in keywords if kw in text_lower)
        scores[dim] = round(matched / len(keywords) * 100)
    return scores


def build_radar_chart(soft_skills_found):
    """Radar chart across all 10 soft skill dimensions using keyword-match scores."""
    if isinstance(soft_skills_found, dict):
        scores = soft_skills_found
    else:
        # legacy: list of detected dim names → treat as fully matched
        scores = {dim: (100 if dim in soft_skills_found else 0) for dim in SOFT_SKILL_DIMS}

    labels = [s.title() for s in SOFT_SKILL_DIMS]
    values = [scores.get(dim, 0) for dim in SOFT_SKILL_DIMS]
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.25)',
        line=dict(color='#667eea', width=2),
        marker=dict(size=6, color='#764ba2'),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor='#e0e0e0'),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=30, r=30),
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# ========== Chatbot ==========
import html as _html

def _build_chat_html(history: list) -> str:
    """Render chat history as self-contained HTML with auto-scroll."""
    msgs = ""
    for msg in history:
        safe = _html.escape(msg["text"])
        safe = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe)
        safe = re.sub(r'\*(.+?)\*', r'<em>\1</em>', safe)
        safe = safe.replace('\n', '<br>')
        if msg["role"] == "bot":
            msgs += f"""
            <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:14px;">
              <div style="min-width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1e3c72,#2a5298);display:flex;align-items:center;justify-content:center;font-size:16px;">🤖</div>
              <div style="background:white;border-radius:4px 18px 18px 18px;padding:10px 14px;max-width:84%;font-size:12.5px;line-height:1.65;color:#1a1a2e;box-shadow:0 2px 10px rgba(0,0,0,0.09);">{safe}</div>
            </div>"""
        else:
            msgs += f"""
            <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:14px;flex-direction:row-reverse;">
              <div style="min-width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:16px;">🎓</div>
              <div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:18px 4px 18px 18px;padding:10px 14px;max-width:84%;font-size:12.5px;line-height:1.65;color:white;">{safe}</div>
            </div>"""
    if not msgs:
        msgs = '<p style="text-align:center;color:#aaa;font-size:12px;padding:24px 0;">Ask me anything below 👇</p>'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
          background:linear-gradient(160deg,#f0f4ff 0%,#f5f0ff 100%);padding:12px 10px;}}
    </style></head><body>{msgs}<div id="b"></div>
    <script>document.getElementById("b").scrollIntoView();</script>
    </body></html>"""


def _build_system_prompt() -> str:
    try:
        sectors = platform.get_sectors()
        sector_list = ", ".join(s.title() for s in sectors)
    except Exception:
        sector_list = "Semiconductor, ICT, Power & Energy, Telecommunications, Defence, Biomedical, Aerospace"
    return f"""You are an EEE (Electrical & Electronic Engineering) Career Advisor chatbot embedded in NTU Singapore's career platform.

The platform contains:
- Job postings across these sectors: {sector_list}
- NTU EEE course catalog matched to job roles via TF-IDF similarity
- SkillsFuture Singapore TSC (Technical Skills & Competencies) framework data
- CV analysis: skill extraction, job match scoring, soft-skills radar

Salary benchmarks (Singapore, 2024-2025):
- Fresh grad: S$3,500–S$4,800/month (semiconductor fabs often S$4,200–S$4,800)
- 3–5 years: S$5,500–S$9,000/month
- Senior (7+ yrs): S$8,000–S$15,000+/month

Answer concisely since you appear in a sidebar. Use bullet points and bold text for clarity.
Refer users to platform tabs (Explore Jobs, CV Analysis, Analytics) for detailed data.
When asked about specific roles or skills, give concrete, practical advice for EEE students in Singapore."""

def get_bot_response(user_input: str) -> str:
    import concurrent.futures
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return "Chatbot unavailable — GROQ_API_KEY not set in .env file."

    messages = [{"role": "system", "content": _build_system_prompt()}]
    for msg in st.session_state.chat_history[-20:]:
        role = "assistant" if msg["role"] == "bot" else "user"
        messages.append({"role": role, "content": msg["text"]})
    messages.append({"role": "user", "content": user_input})

    for delay in [None, 5, 10]:
        try:
            client = Groq(api_key=api_key)
            with concurrent.futures.ThreadPoolExecutor() as ex:
                future = ex.submit(client.chat.completions.create,
                                   model="llama-3.3-70b-versatile",
                                   messages=messages, max_tokens=1024)
                response = future.result(timeout=25)
            return response.choices[0].message.content
        except concurrent.futures.TimeoutError:
            return "⚠️ Request timed out. Please try again."
        except Exception as e:
            err = str(e)
            if ("rate" in err.lower() or "429" in err or "quota" in err.lower()) and delay:
                import time; time.sleep(delay)
                continue
            return f"⚠️ Error: {err}"
    return "⚠️ Rate limited. Please wait a moment."


# ========== CV AI Feedback ==========

def _get_cv_ai_feedback(cv_text: str, skills: list, jobs: list) -> str:
    import concurrent.futures
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", "")
    top_jobs = ", ".join(j.get("position", "") for j in jobs[:3]) or "EEE engineering roles"
    skill_list = ", ".join(skills[:20]) or "none detected"
    prompt = f"""You are an expert career coach reviewing an EEE (Electrical & Electronic Engineering) student's CV for roles in Singapore.

CV TEXT:
---
{cv_text[:4000]}
---

Detected skills: {skill_list}
Top matching jobs: {top_jobs}

Provide a structured CV feedback report with these sections:
1. **Overall Impression** (2-3 sentences)
2. **Strengths** (3 bullet points — specific things done well)
3. **Weaknesses** (3 bullet points — specific gaps or weak areas)
4. **Missing Skills** (skills expected for {top_jobs} that are absent)
5. **Actionable Improvements** (5 concrete, specific suggestions to strengthen this CV)
6. **ATS Score Estimate** (estimate 1-10 and explain why)

Be specific — reference actual content from the CV. Keep total response under 500 words."""

    for delay in [None, 5]:
        try:
            client = Groq(api_key=api_key)
            with concurrent.futures.ThreadPoolExecutor() as ex:
                future = ex.submit(client.chat.completions.create,
                                   model="llama-3.3-70b-versatile",
                                   messages=[{"role": "user", "content": prompt}],
                                   max_tokens=1200)
                response = future.result(timeout=30)
            return response.choices[0].message.content
        except Exception as e:
            err = str(e)
            if ("rate" in err.lower() or "429" in err) and delay:
                import time; time.sleep(delay)
                continue
            return f"Error generating feedback: {err}"
    return "Rate limited. Please try again in a moment."


# ========== Mock Interview Helpers ==========

def _get_iv_system_prompt() -> str:
    iv_type = st.session_state.get("iv_type", "Behavioural")
    topic   = st.session_state.get("iv_topic", "")
    cv_text = st.session_state.get("_cv_text", "")
    if "Behavioural" in iv_type:
        cv_context = f"\n\nStudent's CV (use to personalise questions):\n---\n{cv_text[:2000]}\n---" if cv_text else ""
        return f"""You are a professional job interviewer conducting a behavioural interview for an EEE student applying for engineering roles in Singapore.{cv_context}
Rules:
- Ask ONE behavioural question at a time (STAR method)
- If CV is provided, reference specific experiences from it to make questions personal
- After the student answers: give 2-3 sentence feedback, then ask the next question
- Cover: teamwork, leadership, problem-solving, communication, handling failure, time management
- After 5 complete Q&A rounds, append exactly [INTERVIEW_COMPLETE] at the end of your final feedback
- Be professional and encouraging
Start: briefly introduce yourself and ask Question 1."""
    elif "Technical" in iv_type:
        return f"""You are a technical interviewer for EEE roles in Singapore, specialising in {topic}.
Rules:
- Ask ONE technical question at a time, starting from fundamentals then increasing difficulty
- After each answer: give specific technical feedback, correct misconceptions, then ask next question
- Test: core concepts, problem-solving approach, practical applications, relevant tools
- After 5 complete Q&A rounds, append exactly [INTERVIEW_COMPLETE] at the end of your final feedback
Start: briefly introduce yourself and ask Question 1 on {topic}."""
    else:
        return f"""You are an interviewer doing a CV deep-dive for an EEE student. Their CV:
---
{cv_text[:3000]}
---
Rules:
- Ask ONE question at a time about specific CV items (projects, experiences, skills, education)
- After each answer: give brief feedback then ask the next question
- Challenge: technical decisions, lessons learned, impact, how skills apply to target roles
- After 5 complete Q&A rounds, append exactly [INTERVIEW_COMPLETE] at the end of your final feedback
- Reference specific CV items by name
Start: briefly introduce yourself and ask about a specific project or experience from the CV."""


def _iv_log_result(report: str):
    """Save a completed interview result to the session progress log."""
    import re as _re
    from datetime import datetime
    rating_match = _re.search(r'(\d+)\s*/\s*10', report)
    rating = int(rating_match.group(1)) if rating_match else None
    entry = {
        "type": st.session_state.get("iv_type", "Interview").replace("⚙️ ","").replace("🧠 ","").replace("📄 ",""),
        "topic": st.session_state.get("iv_topic") or "—",
        "rating": rating,
        "time": datetime.now().strftime("%d %b, %H:%M"),
        "q_count": len([m for m in st.session_state.get("iv_history",[]) if m["role"] == "student"]),
    }
    st.session_state.setdefault("iv_log", []).append(entry)


def _iv_call(message: str) -> str:
    import concurrent.futures
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", "")

    messages = [{"role": "system", "content": _get_iv_system_prompt()}]
    for msg in st.session_state.get("iv_history", []):
        role = "assistant" if msg["role"] == "interviewer" else "user"
        messages.append({"role": role, "content": msg["text"].replace("[INTERVIEW_COMPLETE]", "").strip()})
    messages.append({"role": "user", "content": message})

    for delay in [None, 5, 10]:
        try:
            client = Groq(api_key=api_key)
            with concurrent.futures.ThreadPoolExecutor() as ex:
                future = ex.submit(client.chat.completions.create,
                                   model="llama-3.3-70b-versatile",
                                   messages=messages, max_tokens=1024)
                response = future.result(timeout=25)
            return response.choices[0].message.content
        except concurrent.futures.TimeoutError:
            return "⚠️ Request timed out. Please click Submit again."
        except Exception as e:
            err = str(e)
            if ("rate" in err.lower() or "429" in err or "quota" in err.lower()) and delay:
                import time; time.sleep(delay)
                continue
            return f"⚠️ Error: {err}"
    return "⚠️ Rate limited. Please wait a moment."


def _iv_camera_tts_html(latest_msg: str, msg_idx: int, q_num: int, total_q: int = 5) -> str:
    import json
    safe_msg = json.dumps(latest_msg[:600])
    pct = int((q_num - 1) / total_q * 100)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:transparent;padding:4px;}}
#cam-wrap{{position:relative;border-radius:12px;overflow:hidden;background:#1a1a2e;aspect-ratio:4/3;}}
#cam{{width:100%;height:100%;object-fit:cover;display:none;}}
#cam-off{{display:flex;align-items:center;justify-content:center;height:100%;color:#666;font-size:13px;flex-direction:column;gap:6px;min-height:140px;}}
#progress-bar-bg{{background:#e0e0e0;border-radius:8px;height:8px;margin:8px 0 4px;}}
#progress-bar{{background:linear-gradient(90deg,#667eea,#764ba2);height:8px;border-radius:8px;width:{pct}%;transition:width 0.4s;}}
#q-label{{font-size:12px;color:#666;text-align:center;}}
#tts-btn{{margin-top:6px;width:100%;padding:6px;border:1px solid #ddd;border-radius:8px;background:white;font-size:12px;cursor:pointer;color:#555;}}
#tts-btn:hover{{background:#f5f5f5;}}
</style></head><body>
<div id="cam-wrap">
  <video id="cam" autoplay muted playsinline></video>
  <div id="cam-off"><span style="font-size:28px">📷</span><span>Allow camera access</span></div>
</div>
<div id="progress-bar-bg"><div id="progress-bar"></div></div>
<div id="q-label">Question {min(q_num, total_q)} of {total_q}</div>
<button id="tts-btn" onclick="speak()">🔊 Replay Question</button>
<script>
// Camera
navigator.mediaDevices.getUserMedia({{video:true,audio:false}})
  .then(s=>{{
    const v=document.getElementById('cam');
    v.srcObject=s; v.style.display='block';
    document.getElementById('cam-off').style.display='none';
  }}).catch(()=>{{}});

// TTS — auto-speak new messages only
const msg={safe_msg};
const key='iv_tts_{msg_idx}';
function speak(){{
  if(!msg||!window.speechSynthesis)return;
  window.speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(msg);
  u.lang='en-SG'; u.rate=0.88; u.pitch=1.05;
  window.speechSynthesis.speak(u);
}}
if(!sessionStorage.getItem(key)){{
  sessionStorage.setItem(key,'1');
  setTimeout(speak, 600);
}}
</script></body></html>"""


def _iv_mic_html() -> str:
    return """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:transparent;padding:4px 0;}
#btn{display:flex;align-items:center;justify-content:center;gap:8px;
  background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;
  border-radius:24px;padding:10px 24px;font-size:14px;font-weight:600;
  cursor:pointer;width:100%;transition:all 0.2s;}
#btn.on{background:linear-gradient(135deg,#e53935,#e91e63);}
#btn:disabled{opacity:0.45;cursor:not-allowed;}
#st{font-size:11px;color:#999;text-align:center;margin-top:5px;}
#prev{font-size:12px;color:#444;background:#f0f0f0;border-radius:8px;
  padding:8px 12px;margin-top:6px;display:none;line-height:1.5;}
</style></head><body>
<button id="btn" onclick="toggle()">🎤 Speak Answer</button>
<div id="st">Chrome only · click to speak</div>
<div id="prev"></div>
<script>
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let rec,active=false;
if(!SR){document.getElementById('st').textContent='⚠️ Not supported — use Chrome';document.getElementById('btn').disabled=true;}
else{
  rec=new SR();rec.lang='en-SG';rec.continuous=true;rec.interimResults=true;
  rec.onstart=()=>{active=true;document.getElementById('btn').className='on';
    document.getElementById('btn').textContent='🔴 Listening… click to stop';
    document.getElementById('st').textContent='Speak now…';
    document.getElementById('prev').style.display='block';};
  rec.onresult=(e)=>{
    const txt=Array.from(e.results).map(r=>r[0].transcript).join('');
    document.getElementById('prev').textContent=txt;
    if(e.results[e.results.length-1].isFinal){
      try{
        const tas=window.parent.document.querySelectorAll('textarea');
        for(const ta of tas){
          const lbl=(ta.getAttribute('aria-label')||ta.placeholder||'').toLowerCase();
          if(lbl.includes('answer')){
            const s=Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype,'value').set;
            s.call(ta,txt);ta.dispatchEvent(new window.parent.Event('input',{bubbles:true}));break;
          }
        }
      }catch(err){}
    }
  };
  rec.onerror=(e)=>{document.getElementById('st').textContent='Error: '+e.error;reset();};
  rec.onend=reset;
}
function toggle(){active?rec.stop():rec.start();}
function reset(){active=false;document.getElementById('btn').className='';
  document.getElementById('btn').textContent='🎤 Speak Answer';
  document.getElementById('st').textContent='Chrome only · click to speak';}
</script></body></html>"""


def _iv_chat_html(history: list) -> str:
    msgs = ""
    for msg in history:
        safe = _html.escape(msg["text"].replace("[INTERVIEW_COMPLETE]", "").strip())
        safe = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe)
        safe = safe.replace('\n', '<br>')
        if msg["role"] == "interviewer":
            msgs += f"""<div style="display:flex;gap:8px;margin-bottom:14px;">
              <div style="min-width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#1e3c72,#2a5298);display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;">👔</div>
              <div style="background:white;border-radius:4px 16px 16px 16px;padding:10px 14px;max-width:90%;font-size:13px;line-height:1.65;color:#1a1a2e;box-shadow:0 2px 8px rgba(0,0,0,0.09);">{safe}</div>
            </div>"""
        else:
            msgs += f"""<div style="display:flex;gap:8px;margin-bottom:14px;flex-direction:row-reverse;">
              <div style="min-width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;">🎓</div>
              <div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px 4px 16px 16px;padding:10px 14px;max-width:90%;font-size:13px;line-height:1.65;color:white;">{safe}</div>
            </div>"""
    if not msgs:
        msgs = '<p style="text-align:center;color:#bbb;font-size:13px;padding:30px;">Starting interview…</p>'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
          background:linear-gradient(160deg,#f0f4ff,#f5f0ff);padding:14px;}}
    </style></head><body>{msgs}<div id="b"></div>
    <script>document.getElementById("b").scrollIntoView();</script></body></html>"""


# ========== Sidebar Chatbot ==========
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "text": "Hi! 👋 I'm your EEE Career Advisor.\n\nI can answer questions about EEE careers, industries, skills, salaries, internships, NTU courses, and more.\n\nTry asking me anything — or tap a quick question below!"}
    ]

with st.sidebar:
    st.markdown("**🤖 EEE Career Advisor**")

    is_busy = st.session_state.get("_chat_busy", False)

    if is_busy:
        st.markdown("<div style='text-align:center;font-size:0.78rem;color:#999;padding:4px 0;'>⏳ Thinking…</div>", unsafe_allow_html=True)

    components.html(_build_chat_html(st.session_state.chat_history), height=420, scrolling=True)

    user_msg = st.chat_input("Ask about EEE careers…", key="chatbot_input")
    if user_msg and not is_busy:
        st.session_state["_chat_busy"] = True
        st.session_state.chat_history.append({"role": "user", "text": user_msg})
        with st.spinner("Thinking…"):
            st.session_state.chat_history.append({"role": "bot", "text": get_bot_response(user_msg)})
        st.session_state["_chat_busy"] = False
        st.rerun()

    # Follow-up suggestions based on last bot reply
    if st.session_state.chat_history and not is_busy:
        last_bot = next((m["text"] for m in reversed(st.session_state.chat_history) if m["role"] == "bot"), "")
        _follow_map = [
            (["salary","pay","compensation","earn"],    [("💰 Fresh grad salary?","What is the typical fresh graduate salary for EEE in Singapore?"), ("📈 Salary growth?","How does salary grow with experience in EEE roles?")]),
            (["skill","python","matlab","machine learn"],[ ("🛠️ Must-have skills?","What are the top 3 must-have technical skills for EEE graduates?"), ("📚 Where to learn?","What are the best resources to learn these skills?")]),
            (["internship","intern"],                   [("🔍 How to find?","How do I find EEE internships in Singapore?"), ("📄 Application tips?","What should I include in my internship application?")]),
            (["cv","resume","portfolio"],               [("✅ CV checklist?","What should every EEE student include in their CV?"), ("⚠️ Common CV mistakes?","What are common CV mistakes EEE students make?")]),
            (["career","path","role","job"],            [("🚀 Best entry roles?","What are the best entry-level roles for EEE graduates?"), ("🏢 Top companies?","Which companies hire the most EEE graduates in Singapore?")]),
        ]
        suggestions = []
        last_lower = last_bot.lower()
        for keywords, prompts in _follow_map:
            if any(k in last_lower for k in keywords):
                suggestions = prompts
                break
        if suggestions:
            st.markdown("<p style='font-size:0.72rem;color:#aaa;margin:4px 0 4px;text-align:center;'>Suggested follow-ups</p>", unsafe_allow_html=True)
            scols = st.columns(len(suggestions))
            for ci, (label, prompt) in enumerate(suggestions):
                with scols[ci]:
                    if st.button(label, key=f"sugg_{label}", width='stretch'):
                        st.session_state["_chat_busy"] = True
                        st.session_state.chat_history.append({"role": "user", "text": prompt})
                        with st.spinner("Thinking…"):
                            st.session_state.chat_history.append({"role": "bot", "text": get_bot_response(prompt)})
                        st.session_state["_chat_busy"] = False
                        st.rerun()

    if st.button("🗑️ Clear chat", width='stretch'):
        st.session_state.chat_history = [
            {"role": "bot", "text": "Chat cleared! Ask me anything about EEE careers."}
        ]
        st.session_state["_chat_sector"] = None
        st.session_state["_chat_job"] = None
        st.rerun()

    if st.button("✕ Close Panel", key="close_sidebar_btn", use_container_width=True):
        st.session_state["sidebar_visible"] = False
        st.rerun()


# ========== Tabs ==========
tab1, tab2, tab3, tab5, tab_chat, tab_imperial = st.tabs(["🔍 Explore Jobs", "📄 CV Analysis", "🎤 Mock Interview", "📊 Analytics", "💬 AI Chat", "Imperial Platform"])

# ==================== TAB 1: Explore Jobs ====================
with tab1:
    st.markdown("<h2 class='section-header'>🔍 Explore Career Opportunities</h2>", unsafe_allow_html=True)

    _SENIOR_KEYWORDS = {"senior", "lead", "principal", "chief", "head", "manager", "director"}

    def _job_label(title: str) -> str:
        if any(w in title.lower().split() for w in _SENIOR_KEYWORDS):
            return f"{title.title()}  〔 Advanced Role 〕"
        return title.title()

    def _level_badge(level):
        try:
            lvl = int(level)
        except (TypeError, ValueError):
            return f"<span style='background:#ccc;color:#333;padding:2px 8px;border-radius:12px;font-size:0.75rem;'>Level {level}</span>"
        if lvl <= 3:
            return f"<span style='background:#d4edda;color:#155724;padding:2px 8px;border-radius:12px;font-size:0.75rem;'>Level {lvl} · Entry–Intermediate</span>"
        elif lvl == 4:
            return f"<span style='background:#fff3cd;color:#856404;padding:2px 8px;border-radius:12px;font-size:0.75rem;'>Level {lvl} · Advanced — build toward this</span>"
        else:
            return f"<span style='background:#e2e3e5;color:#383d41;padding:2px 8px;border-radius:12px;font-size:0.75rem;'>Level {lvl} · Expert — long-term goal</span>"

    explore_mode = st.radio(
        "explore_mode",
        ["🎯  I know my target role", "📚  Explore from my courses"],
        horizontal=True,
        label_visibility="collapsed",
        key="explore_mode",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MODE 2: Course → Jobs ─────────────────────────────────────────────────
    if explore_mode == "📚  Explore from my courses":
        st.markdown("<div class='info-box'>Select NTU courses you've taken or are interested in — we'll find the best-matching career roles for you.</div>", unsafe_allow_html=True)

        all_courses = platform.get_all_courses()
        course_options = {f"{c['code']} — {c['name'].title()}": c["code"] for c in all_courses if c["code"]}

        selected_course_labels = st.multiselect(
            "Select your courses:",
            options=list(course_options.keys()),
            placeholder="Search and select courses…",
            key="course_explore_select",
        )

        if selected_course_labels:
            selected_codes = [course_options[l] for l in selected_course_labels]
            with st.spinner("Finding matching roles…"):
                matched_roles = platform.find_jobs_from_courses(selected_codes, top_n=10)

            if not matched_roles:
                st.info("No matching roles found. Try selecting more courses.")
            else:
                st.markdown(f"### 🎯 Top Matching Roles for Your Courses")
                if "course_explore_selected_role" not in st.session_state:
                    st.session_state["course_explore_selected_role"] = None

                for rank, role in enumerate(matched_roles, 1):
                    if rank <= 3:
                        match_label, match_class, badge_class = "Strong Match", "high-match", "similarity-high"
                    elif rank <= 7:
                        match_label, match_class, badge_class = "Good Match", "good-match", "similarity-good"
                    else:
                        match_label, match_class, badge_class = "Possible Match", "medium-match", "similarity-medium"

                    st.markdown(f"""
                    <div class='job-card {match_class}'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <div>
                                <h4 style='margin:0;'>{rank}. {str(role['job_title']).title()}</h4>
                                <p style='margin:0.3rem 0 0 0;color:#666;font-size:0.9rem;'>🏭 {str(role['sector']).title()}</p>
                            </div>
                            <div class='similarity-badge {badge_class}'>{match_label}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    with st.expander("View Details", expanded=False):
                        sel_sector = role["sector"]
                        sel_job = role["job_title"]
                        det_a, det_b = st.columns([3, 2])
                        with det_a:
                            job_desc = platform.get_job_description(sel_sector, sel_job) or ""
                            st.markdown("<div class='glass-card'><h4>📖 Job Description</h4></div>", unsafe_allow_html=True)
                            st.write(job_desc if job_desc else "No description available.")

                            tsc_skills = platform.get_raw_tsc_skills(sel_sector, sel_job)
                            if tsc_skills:
                                st.markdown("<div class='gradient-card'><h4>🛠️ Skills Required</h4></div>", unsafe_allow_html=True)
                                for s in tsc_skills:
                                    st.markdown(f"**{s['skill']}** &nbsp; {_level_badge(s['level'])}", unsafe_allow_html=True)
                                    if s['description']:
                                        st.caption(s['description'])

                        with det_b:
                            st.markdown("<div class='gradient-card-blue'><h4>📚 Recommended Courses</h4></div>", unsafe_allow_html=True)
                            if job_desc:
                                try:
                                    det_courses = platform.get_top_courses(sel_sector, sel_job, top_n=5)
                                except Exception:
                                    det_courses = []
                                for i, c in enumerate(det_courses, 1):
                                    st.markdown(f"<div class='course-card'><strong>{i}. {c['code']}</strong><br>{c['name'].title()}<br><small>Relevance: {c['score']*100:.0f}%</small></div>", unsafe_allow_html=True)
                            else:
                                st.info("No job description available for course matching.")

    # ── MODE 1: Role → Details (existing flow) ────────────────────────────────
    else:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("<div class='glass-card'><h4>🏢 Select Industry</h4></div>", unsafe_allow_html=True)
            sectors = platform.get_sectors()
            selected_sector = st.selectbox("Sector:", sectors, key="sector",
                                           label_visibility="collapsed",
                                           format_func=str.title)

        if selected_sector:
            job_titles = platform.get_job_titles(selected_sector)
            with col2:
                st.markdown("<div class='glass-card'><h4>🎯 Select Position</h4></div>", unsafe_allow_html=True)
                selected_job = st.selectbox("Position:", job_titles, key="job",
                                            label_visibility="collapsed",
                                            format_func=_job_label)

            if selected_job:
                if any(w in selected_job.lower().split() for w in _SENIOR_KEYWORDS):
                    st.info("💡 This is an advanced role — useful for long-term career planning. Most fresh graduates start at junior/associate level.", icon=None)
                col_a, col_b = st.columns([3, 2])

                with col_a:
                    # Salary ranges by sector (Singapore, 2024–2025)
                    _salary_map = {
                        "semiconductor":    ("S$3,800 – S$5,200", "S$5,500 – S$9,000", "S$9,000 – S$15,000+"),
                        "ict":              ("S$3,500 – S$4,800", "S$5,000 – S$8,500", "S$8,500 – S$14,000+"),
                        "power":            ("S$3,600 – S$4,800", "S$5,200 – S$8,000", "S$8,000 – S$13,000+"),
                        "energy":           ("S$3,600 – S$4,800", "S$5,200 – S$8,000", "S$8,000 – S$13,000+"),
                        "telecom":          ("S$3,500 – S$4,600", "S$5,000 – S$8,000", "S$8,000 – S$13,000+"),
                        "communication":    ("S$3,500 – S$4,600", "S$5,000 – S$8,000", "S$8,000 – S$13,000+"),
                        "defence":          ("S$3,800 – S$5,000", "S$5,500 – S$9,000", "S$9,000 – S$15,000+"),
                        "aerospace":        ("S$3,800 – S$5,000", "S$5,500 – S$9,000", "S$9,000 – S$15,000+"),
                        "biomedical":       ("S$3,600 – S$4,800", "S$5,000 – S$8,000", "S$8,000 – S$13,000+"),
                    }
                    _sal_key = next((k for k in _salary_map if k in selected_sector.lower()), None)
                    if _sal_key:
                        _fresh, _mid, _senior = _salary_map[_sal_key]
                        st.markdown(f"""<div style='background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-left:4px solid #4caf50;
                            border-radius:0 10px 10px 0;padding:10px 14px;margin-bottom:12px;'>
                            <strong style='color:#2e7d32;font-size:0.85rem;'>💰 Salary Benchmarks (Singapore 2025)</strong><br>
                            <span style='font-size:0.8rem;color:#444;'>
                            🎓 Fresh grad: <strong>{_fresh}</strong> &nbsp;|&nbsp;
                            📈 3–5 yrs: <strong>{_mid}</strong> &nbsp;|&nbsp;
                            🏆 Senior: <strong>{_senior}</strong>
                            </span></div>""", unsafe_allow_html=True)

                    st.markdown("<div class='glass-card'><h4>📖 Job Description</h4></div>", unsafe_allow_html=True)
                    job_desc = platform.get_job_description(selected_sector, selected_job) or ""
                    st.write(job_desc if job_desc else "No description available.")

                    st.markdown("<div class='gradient-card'><h4>🛠️ Skills Summary</h4></div>", unsafe_allow_html=True)
                    tsc_skills = platform.get_raw_tsc_skills(selected_sector, selected_job)
                    if tsc_skills:
                        with st.expander("View detailed skills", expanded=True):
                            for s in tsc_skills:
                                st.markdown(f"**{s['skill']}** &nbsp; {_level_badge(s['level'])}", unsafe_allow_html=True)
                                if s['description']:
                                    st.caption(s['description'])
                    else:
                        st.info("No technical skills data available for this role — the SkillsFuture source file does not have skills listed for this role.")

                with col_b:
                    # --- Recommended Courses ---
                    st.markdown("<div class='gradient-card-blue'><h4>📚 Recommended Courses</h4></div>", unsafe_allow_html=True)
                    if job_desc:
                        with st.spinner("Finding courses..."):
                            try:
                                courses = platform.get_top_courses(selected_sector, selected_job, top_n=5)
                            except Exception as e:
                                courses = []
                                st.warning(f"Course matching error: {e}")
                        for i, c in enumerate(courses, 1):
                            st.markdown(f"<div class='course-card'><strong>{i}. {c['code']}</strong><br>{c['name'].title()}<br><small>Relevance: {c['score']*100:.0f}%</small></div>", unsafe_allow_html=True)
                    else:
                        st.info("No job description available for course matching.")


# ==================== TAB 2: CV Analysis ====================
with tab2:
    st.markdown("<h2 class='section-header'>📄 CV Analysis & Job Matching</h2>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📤 Upload Your CV (PDF)", type=['pdf'], label_visibility="collapsed")

    if uploaded_file:
        # Cache all CV work by filename+size — only re-run when a new file is uploaded
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("_cv_file_key") != file_key:
            with st.spinner("🔍 Extracting skills and matching jobs…"):
                try:
                    cv_text = platform.extract_text_from_pdf(uploaded_file)
                except Exception as e:
                    st.error(f"❌ PDF extraction error: {e}")
                    st.stop()
                if not cv_text:
                    st.error("❌ Could not extract text from PDF")
                    st.stop()
                detected_skills = platform.extract_skills(cv_text)
                soft_skills_found = detect_soft_skills_from_text(cv_text)
                try:
                    matches = platform.find_matching_jobs(detected_skills, top_n=20)
                    strong = matches.get("strong", [])
                    good   = matches.get("good", [])
                    weak   = matches.get("weak", [])
                except Exception as e:
                    st.error(f"Job matching failed: {e}")
                    strong, good, weak = [], [], []
            st.session_state["_cv_file_key"] = file_key
            st.session_state["_cv_text"] = cv_text
            st.session_state["_cv_skills"] = detected_skills
            st.session_state["_cv_soft"] = soft_skills_found
            st.session_state["_cv_matches"] = (strong, good, weak)
        else:
            cv_text = st.session_state["_cv_text"]
            detected_skills = st.session_state["_cv_skills"]
            soft_skills_found = st.session_state["_cv_soft"]
            strong, good, weak = st.session_state["_cv_matches"]

        st.markdown("<div class='success-box'><strong>✅ CV Analysed!</strong></div>", unsafe_allow_html=True)

        # --- Skills ---
        st.markdown("<div class='gradient-card'><h4>🎯 Technical Skills Detected</h4></div>", unsafe_allow_html=True)
        if detected_skills:
            st.success(f"✅ Found {len(detected_skills)} skills")
            categorized = categorize_skills(detected_skills)
            categorized.pop('Soft Skills', None)  # remove from badge display

            sk_col, radar_col = st.columns([3, 2])

            with sk_col:
                for cat, cat_skills in categorized.items():
                    if not cat_skills:
                        continue
                    progress = min(len(cat_skills) / 10 * 100, 100)
                    st.markdown(f"**{cat}** ({len(cat_skills)})")
                    st.markdown(f"<div class='skill-progress'><div class='skill-progress-fill' style='width: {progress}%'></div></div>", unsafe_allow_html=True)
                    badges = " ".join(
                        f"<span style='display:inline-block;background:#e8f4fd;border:1px solid #4a90d9;"
                        f"border-radius:14px;padding:3px 10px;margin:2px;font-size:0.82rem;"
                        f"color:#1a5276'>{s}</span>"
                        for s in cat_skills
                    )
                    st.markdown(badges, unsafe_allow_html=True)
                    st.markdown("")

            with radar_col:
                st.markdown("**🧠 Soft Skills Profile**")
                fig = build_radar_chart(soft_skills_found)
                st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
                detected_dims = [dim for dim, score in soft_skills_found.items() if score > 0]
                if detected_dims:
                    st.caption("Detected: " + ", ".join(s.title() for s in detected_dims))
                else:
                    st.caption("No soft skills detected in this CV.")
        else:
            st.warning("⚠️ No technical skills detected.")

        # --- Job Matches ---
        st.markdown("<h3 class='section-header'>💼 Top Job Matches</h3>", unsafe_allow_html=True)
        if detected_skills:

            all_jobs = strong + good + weak

            def _is_intern(job):
                return "intern" in str(job.get("opportunity_type", "")).lower()

            def _is_fulltime(job):
                opp = str(job.get("opportunity_type", "")).lower()
                return "job" in opp or "graduate" in opp

            intern_jobs   = [j for j in all_jobs if _is_intern(j)][:5]
            fulltime_jobs = [j for j in all_jobs if _is_fulltime(j)][:5]

            if not all_jobs:
                st.info("No matches found. Upload a CV with more technical content.")
            else:
                def _get_tier(score_pct):
                    if score_pct >= 35:
                        return "Strong", "high-match", "similarity-high"
                    elif score_pct >= 20:
                        return "Good", "good-match", "similarity-good"
                    else:
                        return "Possible", "medium-match", "similarity-medium"

                def _render_match(idx, job):
                    sim_pct = job.get('score', 0) * 100
                    label, match_class, badge_class = _get_tier(sim_pct)
                    st.markdown(f"""
                    <div class='job-card {match_class}'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <div>
                                <h4 style='margin:0;'>{idx}. {str(job.get('position','Unknown')).title()}</h4>
                                <p style='margin:0.5rem 0;color:#666;'>🏢 {job.get('employer','N/A')} | 🏷️ {str(job.get('industry','N/A'))[:30]}</p>
                            </div>
                            <div class='similarity-badge {badge_class}'>{label}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                jm_col1, jm_col2 = st.columns(2)
                with jm_col1:
                    st.markdown("##### 🎓 Top Internship Matches")
                    if intern_jobs:
                        for i, job in enumerate(intern_jobs, 1):
                            _render_match(i, job)
                    else:
                        st.info("No internship matches found in top results.")
                with jm_col2:
                    st.markdown("##### 💼 Top Full-Time / Graduate Matches")
                    if fulltime_jobs:
                        for i, job in enumerate(fulltime_jobs, 1):
                            _render_match(i, job)
                    else:
                        st.info("No full-time matches found in top results.")
        else:
            st.info("No job matches found. Upload a CV with more technical content.")

        # --- AI CV Feedback ---
        st.markdown("<h3 class='section-header'>🤖 AI CV Feedback</h3>", unsafe_allow_html=True)
        all_jobs_for_feedback = (strong + good + weak) if detected_skills else []
        if st.button("✨ Get Personalised AI Feedback", type="primary", width='stretch'):
            with st.spinner("Analysing your CV with AI…"):
                feedback = _get_cv_ai_feedback(cv_text, detected_skills, all_jobs_for_feedback)
            st.session_state["_cv_ai_feedback"] = feedback

        if st.session_state.get("_cv_ai_feedback"):
            fb = st.session_state["_cv_ai_feedback"]
            safe_fb = _html.escape(fb)
            safe_fb = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe_fb)
            safe_fb = re.sub(r'^# (.+)$', r'<h3 style="color:#1e3c72;margin:16px 0 8px">\1</h3>', safe_fb, flags=re.MULTILINE)
            safe_fb = re.sub(r'^## (.+)$', r'<h4 style="color:#2a5298;margin:12px 0 6px">\1</h4>', safe_fb, flags=re.MULTILINE)
            safe_fb = safe_fb.replace('\n', '<br>')
            st.markdown(f"<div class='glass-card' style='line-height:1.8;font-size:14px;'>{safe_fb}</div>", unsafe_allow_html=True)

        # --- Practice Mock Interview ---
        st.markdown("<h3 class='section-header'>🎤 Practice Mock Interview</h3>", unsafe_allow_html=True)
        _cv_top_jobs = (strong + good + weak) if detected_skills else []
        _top_job = _cv_top_jobs[0] if _cv_top_jobs else {}
        _top_industry = str(_top_job.get("industry", "")).lower()
        _cv_sector_topic_map = {
            "semiconductor": "VLSI & Digital Design",
            "ict": "Data Structures & Algorithms",
            "power": "Power Electronics",
            "energy": "Power Electronics",
            "telecom": "Computer Networks & Communications",
            "communication": "Computer Networks & Communications",
            "defence": "Embedded Systems & Microcontrollers",
            "aerospace": "Control Systems",
            "biomedical": "Machine Learning & AI",
            "data": "Machine Learning & AI",
        }
        _cv_guessed_topic = next(
            (v for k, v in _cv_sector_topic_map.items() if k in _top_industry),
            "Signal Processing"
        )
        iv_c1, iv_c2 = st.columns(2)
        with iv_c1:
            if st.button("🧠 Behavioural Interview", width='stretch'):
                for k in ("iv_mode","iv_history","iv_report","iv_busy","iv_started","iv_chat","iv_client"):
                    st.session_state.pop(k, None)
                st.session_state.iv_mode = "active"
                st.session_state.iv_type = "🧠 Behavioural"
                st.session_state.iv_topic = None
                st.session_state.iv_history = []
                st.session_state.iv_started = False
                st.session_state.iv_busy = False
                st.info("✅ Behavioural interview ready. Go to the **🎤 Mock Interview** tab to begin!")
        with iv_c2:
            if st.button(f"⚙️ Technical: {_cv_guessed_topic}", width='stretch'):
                for k in ("iv_mode","iv_history","iv_report","iv_busy","iv_started","iv_chat","iv_client"):
                    st.session_state.pop(k, None)
                st.session_state.iv_mode = "active"
                st.session_state.iv_type = "⚙️ Technical"
                st.session_state.iv_topic = _cv_guessed_topic
                st.session_state.iv_history = []
                st.session_state.iv_started = False
                st.session_state.iv_busy = False
                st.info(f"✅ Technical interview set up for **{_cv_guessed_topic}**. Go to the **🎤 Mock Interview** tab to begin!")

# ==================== TAB 3: Mock Interview ====================
with tab3:
    st.markdown("<h2 class='section-header'>🎤 Mock Interview</h2>", unsafe_allow_html=True)

    for _k, _v in [("iv_mode","setup"),("iv_history",[]),("iv_report",""),("iv_busy",False)]:
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ── Progress Tracker ───────────────────────────────────────────────────
    iv_log = st.session_state.get("iv_log", [])
    if iv_log:
        st.markdown("<h3 class='section-header'>📈 Your Progress This Session</h3>", unsafe_allow_html=True)
        avg_rating = sum(e["rating"] for e in iv_log if e["rating"]) / max(1, sum(1 for e in iv_log if e["rating"]))
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            st.markdown(f"<div class='metric-container'><div class='metric-value'>{len(iv_log)}</div><div class='metric-label'>Interviews Completed</div></div>", unsafe_allow_html=True)
        with pc2:
            st.markdown(f"<div class='metric-container'><div class='metric-value'>{avg_rating:.1f}/10</div><div class='metric-label'>Average Rating</div></div>", unsafe_allow_html=True)
        with pc3:
            total_q = sum(e["q_count"] for e in iv_log)
            st.markdown(f"<div class='metric-container'><div class='metric-value'>{total_q}</div><div class='metric-label'>Questions Answered</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        for e in reversed(iv_log):
            rating_color = "#4caf50" if (e["rating"] or 0) >= 7 else "#ff9800" if (e["rating"] or 0) >= 5 else "#f44336"
            rating_str = f"{e['rating']}/10" if e["rating"] else "N/A"
            st.markdown(f"""<div style='background:white;border-radius:10px;padding:10px 16px;margin-bottom:8px;
                display:flex;justify-content:space-between;align-items:center;
                box-shadow:0 2px 8px rgba(0,0,0,0.07);border-left:4px solid {rating_color};'>
                <div><strong>{e['type']}</strong> · {e['topic']} · {e['q_count']} questions</div>
                <div style='display:flex;gap:16px;align-items:center;'>
                    <span style='color:{rating_color};font-weight:700;font-size:1.1rem;'>{rating_str}</span>
                    <span style='color:#aaa;font-size:0.8rem;'>{e['time']}</span>
                </div></div>""", unsafe_allow_html=True)
        st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)

    # ── SETUP ─────────────────────────────────────────────────────────────
    if st.session_state.iv_mode == "setup":
        st.markdown("<div class='info-box'>Practice your interview skills with an AI interviewer. Get personalised feedback after each answer, then a full report at the end.</div>", unsafe_allow_html=True)

        sc1, sc2 = st.columns([1, 1])
        with sc1:
            iv_type_sel = st.radio("**Interview Type**", ["🧠 Behavioural", "⚙️ Technical", "📄 CV Deep Dive"], key="iv_type_radio")
        with sc2:
            iv_topic_sel = None
            if "Technical" in iv_type_sel:
                iv_topic_sel = st.selectbox("**Technical Topic**", [
                    "Signal Processing", "Embedded Systems & Microcontrollers",
                    "Power Electronics", "Machine Learning & AI",
                    "Computer Networks & Communications",
                    "Control Systems", "VLSI & Digital Design",
                    "IoT & Sensors", "Data Structures & Algorithms",
                ], key="iv_topic_sel")
            elif "CV Deep Dive" in iv_type_sel:
                if st.session_state.get("_cv_text"):
                    st.success("✅ CV loaded — ready for deep dive!")
                else:
                    st.warning("⚠️ Upload your CV in the **CV Analysis** tab first.")

        if st.button("🚀 Start Interview", type="primary", width='stretch'):
            if "CV Deep Dive" in iv_type_sel and not st.session_state.get("_cv_text"):
                st.error("Please upload your CV in the CV Analysis tab first.")
            else:
                st.session_state.iv_mode = "active"
                st.session_state.iv_history = []
                st.session_state.iv_report = ""
                st.session_state.iv_busy = False
                st.session_state.iv_type = iv_type_sel
                st.session_state.iv_topic = iv_topic_sel
                st.session_state.iv_started = False
                for k in ("iv_chat", "iv_client"):
                    st.session_state.pop(k, None)
                st.rerun()

    # ── ACTIVE INTERVIEW ───────────────────────────────────────────────────
    elif st.session_state.iv_mode == "active":
        iv_label = st.session_state.get("iv_type", "")
        topic_label = f" · {st.session_state.get('iv_topic','')}" if st.session_state.get("iv_topic") else ""
        st.markdown(f"<div class='info-box'><strong>{iv_label}{topic_label}</strong> · 5 questions · speak or type your answers</div>", unsafe_allow_html=True)

        # First message — kick off interviewer
        if not st.session_state.get("iv_started"):
            with st.spinner("Interviewer is preparing…"):
                first_q = _iv_call("Begin the interview.")
            st.session_state.iv_history.append({
                "role": "interviewer",
                "text": first_q or "Hello! I'm your interviewer. Let's begin — tell me about yourself."
            })
            st.session_state.iv_started = True
            st.rerun()

        # Derive progress info
        iv_hist = st.session_state.iv_history
        interviewer_msgs = [m for m in iv_hist if m["role"] == "interviewer"]
        q_num = max(1, len(interviewer_msgs))
        latest_iv_msg = interviewer_msgs[-1]["text"].replace("[INTERVIEW_COMPLETE]", "").strip() if interviewer_msgs else ""
        msg_idx = len(iv_hist)

        # 2-column layout: chat | camera+progress
        chat_col, cam_col = st.columns([3, 2])
        with chat_col:
            components.html(_iv_chat_html(iv_hist), height=440, scrolling=False)
        with cam_col:
            components.html(_iv_camera_tts_html(latest_iv_msg, msg_idx, q_num), height=280, scrolling=False)

        # Answer input
        answer = st.text_area("Your answer", placeholder="Type here or use the mic button below…",
                              key="iv_answer_box", label_visibility="collapsed",
                              height=100, disabled=st.session_state.iv_busy)

        # Mic button
        components.html(_iv_mic_html(), height=90, scrolling=False)

        ba, bb = st.columns(2)
        with ba:
            if st.button("📨 Submit Answer", type="primary", width='stretch',
                         disabled=st.session_state.iv_busy):
                st.session_state.iv_busy = True
                st.session_state.iv_history.append({"role": "student", "text": answer.strip()})
                with st.spinner("Interviewer is responding…"):
                    reply = _iv_call(answer.strip())
                st.session_state.iv_history.append({"role": "interviewer", "text": reply})
                st.session_state.iv_busy = False
                if "[INTERVIEW_COMPLETE]" in reply:
                    with st.spinner("Generating your report…"):
                        report = _iv_call(
                            "Generate a comprehensive interview assessment report. "
                            "Include: overall rating (1-10), strengths, areas for improvement, "
                            "and 3 specific actionable tips. Format with clear sections and bullet points."
                        )
                    st.session_state.iv_report = report
                    _iv_log_result(report)
                    st.session_state.iv_mode = "done"
                st.rerun()
        with bb:
            if st.button("🏁 End & Get Report", width='stretch', disabled=st.session_state.iv_busy):
                st.session_state.iv_busy = True
                with st.spinner("Generating your report…"):
                    report = _iv_call(
                        "The student has ended the interview early. Based on the answers given so far, "
                        "generate a comprehensive assessment report with: overall rating (1-10), "
                        "strengths, areas for improvement, and 3 specific actionable tips. "
                        "Format with clear sections and bullet points."
                    )
                st.session_state.iv_report = report
                _iv_log_result(report)
                st.session_state.iv_busy = False
                st.session_state.iv_mode = "done"
                st.rerun()

    # ── REPORT ─────────────────────────────────────────────────────────────
    elif st.session_state.iv_mode == "done":
        st.markdown("<div class='success-box'><strong>✅ Interview Complete!</strong> Here is your personalised feedback report.</div>", unsafe_allow_html=True)

        report_text = st.session_state.get("iv_report", "")
        if report_text:
            clean = report_text.replace("[INTERVIEW_COMPLETE]", "").strip()
            safe_report = _html.escape(clean)
            safe_report = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe_report)
            safe_report = re.sub(r'^#{1,3} (.+)$', r'<h4 style="color:#1e3c72;margin:14px 0 6px">\1</h4>', safe_report, flags=re.MULTILINE)
            safe_report = safe_report.replace('\n', '<br>')
            st.markdown(f"<div class='glass-card' style='line-height:1.8;font-size:14px;'>{safe_report}</div>", unsafe_allow_html=True)
        else:
            st.info("No report generated.")

        if st.button("🔄 Start New Interview", type="primary", width='stretch'):
            for k in ("iv_mode","iv_history","iv_report","iv_busy","iv_started","iv_type","iv_topic","iv_chat","iv_client"):
                st.session_state.pop(k, None)
            st.rerun()


# ==================== TAB 5: Analytics ====================
with tab5:
    st.markdown("<h2 class='section-header'>📊 Analytics Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<div class='info-box'><strong>💡 Live data</strong> from CareerAxis job postings, SkillsFuture framework, Skill Taxonomy, and NTU Course Catalog.</div>", unsafe_allow_html=True)

    @st.cache_data(show_spinner=False)
    def _load_analytics():
        import pandas as pd
        ca = pd.read_excel("Data/careeraxis2025.xlsx")
        sf = pd.read_excel("Data/Myskillsfuture pdf extraction.xlsx")
        tx = pd.read_excel("Data/Taxonomy.xlsx")
        co = pd.read_excel("Data/Course Catalog AY2324.xlsx")
        return ca, sf, tx, co

    with st.spinner("Loading data…"):
        _ca, _sf, _tx, _co = _load_analytics()

    PALETTE = ["#1e3c72", "#2a5298", "#667eea", "#764ba2", "#11998e",
               "#38ef7d", "#f093fb", "#f5576c", "#fda085", "#43e97b"]

    # ── Row 1: Industry breakdown  +  Opportunity type donut ──────────────────
    r1c1, r1c2 = st.columns([3, 2])

    with r1c1:
        st.markdown("#### 🏢 Top Industries Hiring EEE Graduates")
        ind = _ca["Industry"].value_counts().head(10)
        fig_ind = go.Figure(go.Bar(
            x=ind.values[::-1], y=ind.index[::-1],
            orientation="h",
            marker=dict(
                color=list(range(10)),
                colorscale=[[i/9, c] for i, c in enumerate(PALETTE)],
                showscale=False,
            ),
            text=ind.values[::-1], textposition="outside",
        ))
        fig_ind.update_layout(
            margin=dict(t=10, b=10, l=10, r=60), height=360,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(tickfont=dict(size=12, color="#000000")),
            font=dict(color="#000000"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_ind, width='stretch', config={"displayModeBar": False})
        st.caption("📌 Source: CareerAxis job postings — includes all degree backgrounds, not filtered to EEE-specific roles")

    # ── Row 1b: Internship vs Full-Time top industries ────────────────────────
    st.markdown("#### 🎯 Top Industries by Opportunity Type")
    opp_col = _ca["Opportunity type(s)"].fillna("").str.lower()
    intern_df  = _ca[opp_col.str.contains("intern")]
    fulltime_df = _ca[opp_col.str.contains("job|graduate")]

    ib1, ib2 = st.columns(2)

    def _opp_bar(df, title, color):
        ind = df["Industry"].value_counts().head(5)
        fig = go.Figure(go.Bar(
            x=ind.values[::-1], y=ind.index[::-1],
            orientation="h",
            marker=dict(color=color),
            text=ind.values[::-1], textposition="outside",
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=13, color="#000000")),
            margin=dict(t=40, b=10, l=10, r=50), height=280,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(tickfont=dict(size=11, color="#000000")),
            font=dict(color="#000000"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    with ib1:
        st.plotly_chart(_opp_bar(intern_df, "🎓 Top 5 Industries — Internships", "#11998e"),
                        width='stretch', config={"displayModeBar": False})
    with ib2:
        st.plotly_chart(_opp_bar(fulltime_df, "💼 Top 5 Industries — Full-Time / Graduate", "#2a5298"),
                        width='stretch', config={"displayModeBar": False})
    st.caption("📌 Source: CareerAxis job postings — not NTU placement data")

    # ── Row 2: SkillsFuture sunburst  +  Taxonomy skill clusters ──────────────
    r2c1, r2c2 = st.columns([2, 3])

    with r2c1:
        st.markdown("#### 🌐 SkillsFuture: Sector → Track")
        sf_grp = _sf.groupby(["Sector", "Track"]).size().reset_index(name="count")
        sectors = _sf["Sector"].unique()
        sec_totals = _sf.groupby("Sector").size().to_dict()
        sun_ids     = list(sectors) + (sf_grp["Sector"] + " / " + sf_grp["Track"]).tolist()
        sun_labels  = list(sectors) + sf_grp["Track"].tolist()
        sun_parents = [""] * len(sectors) + sf_grp["Sector"].tolist()
        sun_values  = [sec_totals[s] for s in sectors] + sf_grp["count"].tolist()
        fig_sun = go.Figure(go.Sunburst(
            ids=sun_ids, labels=sun_labels,
            parents=sun_parents, values=sun_values,
            branchvalues="total",
            marker=dict(colorscale="Blues"),
            hovertemplate="<b>%{label}</b><br>%{value} roles<extra></extra>",
            insidetextorientation="radial",
        ))
        fig_sun.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), height=380,
            font=dict(color="#000000"),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_sun, width='stretch', config={"displayModeBar": False})

    with r2c2:
        st.markdown("#### 🧩 Skill Taxonomy: Top Clusters")
        cluster_counts = _tx["level_1 cluster labels"].value_counts()
        fig_clust = go.Figure(go.Bar(
            x=cluster_counts.values[::-1],
            y=cluster_counts.index[::-1],
            orientation="h",
            marker=dict(
                color=cluster_counts.values[::-1],
                colorscale="Purples", showscale=False,
            ),
            text=cluster_counts.values[::-1], textposition="outside",
        ))
        fig_clust.update_layout(
            margin=dict(t=10, b=10, l=10, r=80), height=380,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(tickfont=dict(size=11, color="#000000")),
            font=dict(color="#000000"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_clust, width='stretch', config={"displayModeBar": False})

    # ── Row 3: Course catalog breakdown  +  Contract type donut ──────────────
    r3c1, r3c2 = st.columns([2, 3])

    with r3c1:
        st.markdown("#### 📚 NTU Course Catalog (AY23/24)")
        _co_work = _co.copy()
        _co_work["Domain"] = _co_work["Course Code"].str[:2].map(
            {"EE": "Electrical & Electronic", "IE": "Integrated Engineering"}
        ).fillna("Other")
        dom_counts = _co_work["Domain"].value_counts()
        fig_dom = go.Figure(go.Pie(
            labels=dom_counts.index.tolist(),
            values=dom_counts.values.tolist(),
            hole=0.45,
            marker=dict(colors=["#1e3c72", "#667eea", "#11998e"]),
            textinfo="label+percent",
            hovertemplate="%{label}<br>%{value} courses<extra></extra>",
        ))
        fig_dom.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), height=300,
            showlegend=False,
            font=dict(color="#000000"),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_dom, width='stretch', config={"displayModeBar": False})

    with r3c2:
        st.markdown("#### 🔗 Taxonomy Skill Clusters → Sector Presence")
        # Cross-tab: how many unique tsc_titles each sector has per cluster
        cluster_sector = (
            _tx.groupby(["level_1 cluster labels", "sector"])["tsc_title"]
            .nunique()
            .reset_index(name="skills")
        )
        top_clusters = _tx["level_1 cluster labels"].value_counts().head(5).index.tolist()
        top_sectors  = _tx["sector"].value_counts().head(7).index.tolist()
        filt = cluster_sector[
            cluster_sector["level_1 cluster labels"].isin(top_clusters) &
            cluster_sector["sector"].isin(top_sectors)
        ]
        pivot = filt.pivot(index="level_1 cluster labels", columns="sector", values="skills").fillna(0)
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[s.title() for s in pivot.columns],
            y=[c.replace(" & ", " &\n") for c in pivot.index],
            colorscale="Blues",
            text=pivot.values.astype(int),
            texttemplate="%{text}",
            hovertemplate="Cluster: %{y}<br>Sector: %{x}<br>Unique skills: %{z}<extra></extra>",
        ))
        fig_heat.update_layout(
            margin=dict(t=10, b=80, l=10, r=10), height=300,
            xaxis=dict(tickangle=-30, tickfont=dict(size=10, color="#000000")),
            yaxis=dict(tickfont=dict(size=10, color="#000000")),
            font=dict(color="#000000"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_heat, width='stretch', config={"displayModeBar": False})

# ==================== TAB: AI Chat ====================
with tab_chat:
    st.markdown("<h2 class='section-header'>💬 AI Career Advisor</h2>", unsafe_allow_html=True)
    if st.session_state["sidebar_visible"]:
        st.markdown("<div class='success-box'>✅ Chat panel is open on the left — ask anything!</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='glass-card' style='text-align:center;padding:2.5rem;'>
            <h3>🤖 Your AI Career Advisor is ready</h3>
            <p>Get personalised advice on EEE careers, salaries, skills, internships, NTU courses and more.</p>
        </div>""", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            if st.button("💬 Open Chat Panel", type="primary", use_container_width=True, key="open_chat_from_tab"):
                st.session_state["sidebar_visible"] = True
                st.rerun()

# ==================== TAB: Imperial Platform ====================
with tab_imperial:
    st.markdown("<h2 class='section-header'>Imperial College London Platform</h2>", unsafe_allow_html=True)

    # ── Collaboration Banner ──────────────────────────────────────────────────
    _imp_logo_html = (
        f"<img src='data:image/png;base64,{_imp_logo_b64}' "
        f"style='height:56px;border-radius:8px;background:white;padding:6px 12px;flex-shrink:0;'>"
        if _imp_logo_b64 else
        "<div style='background:white;border-radius:8px;padding:10px 18px;"
        "font-weight:700;color:#003E74;font-size:0.9rem;'>Imperial EEE</div>"
    )
    _ntu_badge_html = (
        f"<img src='data:image/png;base64,{_logo_b64}' "
        f"style='height:56px;border-radius:8px;background:white;padding:6px 12px;flex-shrink:0;'>"
        if _logo_b64 else
        "<div style='background:white;border-radius:8px;padding:10px 18px;"
        "font-weight:700;color:#1e3c72;font-size:0.9rem;'>NTU EEE</div>"
    )
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#003E74 0%,#006EAF 55%,#1e3c72 100%);
                border-radius:1.2rem;padding:2rem 2.5rem;margin-bottom:2rem;
                box-shadow:0 10px 40px rgba(0,0,0,0.18);'>
        <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;'>
            <div style='flex:1;min-width:240px;'>
                <h2 style='color:white;margin:0;font-size:1.75rem;font-weight:700;'>
                    NTU x Imperial EEE Career Platforms
                </h2>
                <p style='color:rgba(255,255,255,0.88);margin:0.6rem 0 0 0;font-size:0.97rem;line-height:1.6;'>
                    A cross-university collaboration between Nanyang Technological University Singapore and
                    Imperial College London — two world-leading engineering schools exploring how AI can guide
                    EEE students toward meaningful careers, from Singapore's technology ecosystem to
                    London's global engineering and financial hub.
                </p>
            </div>
            <div style='display:flex;gap:1rem;align-items:center;flex-shrink:0;'>
                {_ntu_badge_html}
                <div style='color:white;font-size:1.6rem;font-weight:300;'>&#8596;</div>
                {_imp_logo_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How Imperial's Platform Works ────────────────────────────────────────
    st.markdown("<h3 class='section-header'>How the Imperial Platform Works</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#555;margin-bottom:1.2rem;'>
        Unlike the free-browse approach used here, the Imperial platform uses a <strong>goal-first AI flow</strong> —
        you provide your CV and career goal upfront, and an Azure AI agent generates a fully personalised
        suite of five tabs tailored to you.
    </p>
    <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem;'>
        <div style='background:linear-gradient(135deg,#003E74,#006EAF);color:white;
                    border-radius:1rem;padding:1.3rem;text-align:center;'>
            <div style='font-weight:700;font-size:1rem;margin-bottom:0.4rem;'>Step 1</div>
            <div style='font-size:0.85rem;opacity:0.88;'>Upload your CV</div>
        </div>
        <div style='background:linear-gradient(135deg,#006EAF,#0087C8);color:white;
                    border-radius:1rem;padding:1.3rem;text-align:center;'>
            <div style='font-weight:700;font-size:1rem;margin-bottom:0.4rem;'>Step 2</div>
            <div style='font-size:0.85rem;opacity:0.88;'>Set your career goal — pick from dropdown or describe it in free text</div>
        </div>
        <div style='background:linear-gradient(135deg,#667eea,#764ba2);color:white;
                    border-radius:1rem;padding:1.3rem;text-align:center;'>
            <div style='font-weight:700;font-size:1rem;margin-bottom:0.4rem;'>Step 3</div>
            <div style='font-size:0.85rem;opacity:0.88;'>Azure AI agent analyses your CV against your goal holistically</div>
        </div>
        <div style='background:linear-gradient(135deg,#11998e,#38ef7d);color:#1a1a2e;
                    border-radius:1rem;padding:1.3rem;text-align:center;'>
            <div style='font-weight:700;font-size:1rem;margin-bottom:0.4rem;'>Step 4</div>
            <div style='font-size:0.85rem;'>5 personalised tabs unlock instantly</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 5 Output Tabs ────────────────────────────────────────────────────────
    st.markdown("<p style='font-weight:600;font-size:1rem;color:#1a1a2e;margin-bottom:0.8rem;'>The 5 Personalised Output Tabs</p>", unsafe_allow_html=True)
    _imp_output_tabs = [
        ("My Profile",    "#003E74", "Imperial modules relevant to your goal + current skills extracted from your CV"),
        ("My Roadmap",    "#006EAF", "Recommended modules, future experiences (ML internships, UROP, projects), and skills to develop"),
        ("Job Match",     "#1e3c72", "Sector fit analysis, how your CV compares to the market, and optional match against a specific job posting"),
        ("Interview Prep","#764ba2", "AI-powered mock interview practice aligned to your stated career goal"),
        ("NTU Analytics", "#11998e", "SkillsFuture market data visualisations and a direct link back to this NTU platform"),
    ]
    _out_cols = st.columns(5)
    for col, (title, colour, desc) in zip(_out_cols, _imp_output_tabs):
        with col:
            st.markdown(f"""
            <div style='background:white;border-radius:1rem;padding:1rem 0.8rem;text-align:center;
                        box-shadow:0 4px 15px rgba(0,0,0,0.08);border-top:4px solid {colour};
                        min-height:140px;'>
                <div style='font-weight:700;font-size:0.82rem;color:{colour};margin-bottom:0.5rem;'>{title}</div>
                <div style='font-size:0.75rem;color:#555;line-height:1.4;'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Side-by-side Comparison ──────────────────────────────────────────────
    st.markdown("<h3 class='section-header'>Platform Comparison</h3>", unsafe_allow_html=True)

    _ntu_feats = [
        "Free-browse job explorer — by sector, role, or your courses",
        "CV upload: skills extraction, job matching, soft-skills radar",
        "Singapore salary benchmarks per sector (2025)",
        "Mock interview: Behavioural, Technical, CV Deep Dive",
        "SkillsFuture + Skill Taxonomy + CareerAxis market analytics",
        "Always-on AI career advisor chatbot in sidebar",
        "Groq / Llama 3.3-70B for all AI features",
        "Singapore job market and SkillsFuture TSC framework",
        "Course to Jobs: discover roles from NTU modules you have taken",
        "No login required — explore freely at any stage",
    ]
    _imp_feats = [
        "Goal-first flow — CV + career goal unlock everything at once",
        "My Profile: Imperial modules + skills mapped to your goal",
        "Personalised roadmap: modules, UROP, internship suggestions",
        "Job Match: sector fit + CV vs market + specific posting match",
        "Interview prep aligned specifically to your career goal",
        "SkillsFuture analytics + cross-links to NTU platform",
        "Azure AI agent for holistic, goal-aware analysis",
        "UK / London job market context",
        "Imperial EEE module catalog as the course backbone",
        "CV + goal submitted once — all tabs personalised together",
    ]

    _ntu_rows = "".join(
        f"<div style='background:rgba(255,255,255,0.13);border-radius:0.5rem;"
        f"padding:0.5rem 0.8rem;font-size:0.83rem;margin-bottom:0.4rem;'>{f}</div>"
        for f in _ntu_feats
    )
    _imp_rows = "".join(
        f"<div style='background:rgba(255,255,255,0.13);border-radius:0.5rem;"
        f"padding:0.5rem 0.8rem;font-size:0.83rem;margin-bottom:0.4rem;'>{f}</div>"
        for f in _imp_feats
    )

    cmp_l, cmp_r = st.columns(2)
    with cmp_l:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1e3c72,#2a5298);color:white;
                    border-radius:1.2rem;padding:1.5rem;'>
            <h3 style='color:white;margin:0 0 1rem 0;'>NTU EEE Platform</h3>
            {_ntu_rows}
        </div>""", unsafe_allow_html=True)
    with cmp_r:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#003E74,#006EAF);color:white;
                    border-radius:1.2rem;padding:1.5rem;'>
            <h3 style='color:white;margin:0 0 1rem 0;'>Imperial EEE Platform</h3>
            {_imp_rows}
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Shared Design Philosophy ─────────────────────────────────────────────
    st.markdown("<h3 class='section-header'>Shared Design Philosophy</h3>", unsafe_allow_html=True)

    _phil = [
        ("SkillsFuture Backbone",
         "Both platforms use Singapore's SkillsFuture TSC (Technical Skills & Competencies) framework "
         "as the shared skills ontology — ensuring the language of skills is consistent across both "
         "universities and both job markets."),
        ("EEE-First Design",
         "Built specifically for Electrical & Electronic Engineering students, not repurposed generic "
         "career tools. Course catalogs, sector data, AI system prompts, and job matching logic are "
         "all EEE-tailored from the ground up."),
        ("AI-Powered Personalisation",
         "Both platforms use large language models to go beyond keyword matching — providing "
         "contextual, actionable guidance. NTU uses Groq/Llama for real-time advice; "
         "Imperial uses Azure AI for holistic goal-driven analysis."),
        ("Local Context, Shared Method",
         "The methodology is intentionally mirrored so findings are comparable. NTU targets "
         "Singapore's semiconductor, ICT, and defence sectors; Imperial targets UK engineering "
         "and finance. Same framework, different labour markets."),
    ]
    ph_cols = st.columns(4)
    for col, (title, desc) in zip(ph_cols, _phil):
        with col:
            st.markdown(f"""
            <div class='glass-card' style='text-align:center;height:100%;'>
                <h4 style='color:#003E74;margin:0 0 0.5rem 0;font-size:0.9rem;'>{title}</h4>
                <p style='font-size:0.8rem;color:#555;line-height:1.5;margin:0;'>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Key Differences at a Glance ──────────────────────────────────────────
    st.markdown("<h3 class='section-header'>Key Differences at a Glance</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem;'>
        <div class='info-box'>
            <strong>Entry point</strong><br>
            <span style='font-size:0.85rem;'>
            NTU lets you explore freely — browse jobs, view analytics, or upload a CV at any time.<br><br>
            Imperial asks for CV + goal upfront, then personalises everything in one shot.
            </span>
        </div>
        <div class='info-box'>
            <strong>AI architecture</strong><br>
            <span style='font-size:0.85rem;'>
            NTU uses a conversational LLM (Llama 3.3) in a sidebar chatbot plus per-feature calls for CV feedback and interviews.<br><br>
            Imperial uses a single Azure AI agent that processes CV + goal together and drives all five output tabs.
            </span>
        </div>
        <div class='info-box'>
            <strong>Career roadmap</strong><br>
            <span style='font-size:0.85rem;'>
            NTU maps courses to roles and roles to required skills — you build your own path.<br><br>
            Imperial generates a fully structured roadmap: recommended modules, suggested experiences (UROP, internships), and a skills development plan.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='glass-card' style='text-align:center;padding:2.5rem 2rem;border-top:4px solid #003E74;'>
        <h3 style='color:#003E74;margin:0 0 0.5rem 0;'>Try the Imperial EEE Platform</h3>
        <p style='color:#555;margin:0 0 1.2rem 0;font-size:0.95rem;'>
            Upload your CV, state your career goal, and get a personalised roadmap, job match analysis,
            and interview prep — built by the Imperial EEE team.
        </p>
        <div style='display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;
                    font-size:0.85rem;color:#444;margin-bottom:1.5rem;'>
            <span>CV-driven personalisation</span>
            <span>&#183;</span>
            <span>AI career roadmap</span>
            <span>&#183;</span>
            <span>UK job market context</span>
            <span>&#183;</span>
            <span>Interview preparation</span>
            <span>&#183;</span>
            <span>SkillsFuture analytics</span>
        </div>
        <p style='font-size:0.8rem;color:#999;margin:0;'>
            Note: the platform requires a short sign-in via Streamlit Community Cloud.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _cta_l, _cta_m, _cta_r = st.columns([1, 2, 1])
    with _cta_m:
        st.link_button(
            "Open Imperial EEE Platform",
            "https://imperialntucareers.streamlit.app/",
            use_container_width=True,
            type="primary",
        )


# Footer
st.markdown("""<div class='footer'><h3>🎓 NTU EEE Career Pathways Platform</h3><p>NTU Singapore • 2026</p></div>""", unsafe_allow_html=True)
