"""
EEE Career Pathways Platform - CONNECTED TO BACKEND
Uses backend_api.py (EEECareerPlatform) for all data and ML operations.
"""

import streamlit as st
import re
import os
import sys
import plotly.graph_objects as go
import streamlit.components.v1 as components
from agent_api import query_agent, query_job_match_agent, query_interview_agent, query_specific_job_agent, query_sector_match_agent, query_chat_agent
import streamlit_mic_recorder 
from tts_utils import text_to_speech_gtts
import html as _html

# ========== Page Configuration — MUST be first Streamlit command ==========
st.set_page_config(
    page_title="EEE Career Pathways",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Premium CSS ==========
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="collapsedControl"] {display: none;}

.main-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem 3rem; border-radius: 0 0 2rem 2rem;
    margin: -1rem -1rem 2rem -1rem; box-shadow: 0 10px 40px rgba(0,0,0,0.15);
}
.main-header h1 { color: white; font-size: 2.5rem; font-weight: 700; margin: 0; }
.main-header p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem; }

.stTabs [data-baseweb="tab-list"] { gap: 8px; background: white; padding: 0.5rem; border-radius: 1rem; }
.stTabs [data-baseweb="tab"] { padding: 0.8rem 1.5rem; border-radius: 0.8rem; font-weight: 600; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; }

.glass-card { background: rgba(255,255,255,0.95); border-radius: 1.2rem; padding: 1.8rem; box-shadow: 0 8px 32px rgba(0,0,0,0.08); margin: 1rem 0; }
.gradient-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1.2rem; padding: 1.8rem; margin: 1rem 0; }
.gradient-card-blue { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; border-radius: 1.2rem; padding: 1.8rem; margin: 1rem 0; }

.info-box { background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%); border-left: 5px solid #00bcd4; border-radius: 0 1rem 1rem 0; padding: 1.2rem 1.5rem; margin: 1rem 0; }
.success-box { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-left: 5px solid #4caf50; border-radius: 0 1rem 1rem 0; padding: 1.2rem 1.5rem; margin: 1rem 0; }
.warning-box { background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-left: 5px solid #ff9800; border-radius: 0 1rem 1rem 0; padding: 1.2rem 1.5rem; margin: 1rem 0; }

.metric-container { background: white; border-radius: 1rem; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
.metric-value { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-label { color: #666; font-size: 0.95rem; font-weight: 500; margin-top: 0.5rem; }

.skill-progress { background: #e0e0e0; border-radius: 1rem; height: 12px; overflow: hidden; margin: 0.5rem 0; }
.skill-progress-fill { height: 100%; border-radius: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }

.job-card { background: white; border-radius: 1rem; padding: 1.5rem; margin: 1rem 0; border-left: 5px solid #667eea; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
.job-card.high-match { border-left-color: #4caf50; }
.job-card.medium-match { border-left-color: #ff9800; }

.similarity-badge { display: inline-block; padding: 0.4rem 1rem; border-radius: 2rem; font-weight: 600; font-size: 0.9rem; }
.similarity-high { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
.similarity-medium { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }

.course-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1rem; padding: 1.5rem; margin: 0.8rem 0; }
.section-header { font-size: 1.8rem; font-weight: 700; color: #1e3c72; margin: 2rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 3px solid #667eea; display: inline-block; }
.footer { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 2rem; border-radius: 2rem 2rem 0 0; margin-top: 3rem; text-align: center; }
.main .block-container, [data-testid="stMarkdownContainer"],
[data-testid="stText"], [data-testid="stCaptionContainer"],
.stRadio label, .stSelectbox label, .stFileUploader label,
.stCheckbox label, .stTextArea label { color: #1a1a2e !important; }

/* Button text white */
.main button, .main button p, .main button span, .main button div { color: white !important; }

/* Header always above everything */
header[data-testid="stHeader"] {
    z-index: 2147483647 !important;
    position: fixed !important;
}

/* Hide native sidebar arrow */
[data-testid="collapsedControl"] { display: none !important; }

/* File uploader button */
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] button span {
    color: white !important;
    background-color: #3a3a5c !important;
}

/* Sidebar chat styles */
section[data-testid="stSidebar"] { background: #f8f9ff; }
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

/* Close Panel button — red tint */
section[data-testid="stSidebar"] button[key="close_sidebar_btn"] {
    background: rgba(220,53,69,0.08) !important;
    border: 1.5px solid rgba(220,53,69,0.4) !important;
    color: #c0392b !important;
}

</style>
""", unsafe_allow_html=True)
# ========== Sidebar Visibility ==========
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
st.markdown("""
<div class='main-header'>
    <h1>🎓 EEE Career Pathways Platform</h1>
    <p>AI-Powered Career Guidance for Electrical & Electronic Engineering Students</p>
</div>
""", unsafe_allow_html=True)

# ========== Backend Loading ==========
@st.cache_resource(show_spinner=False)
def _get_platform():
    from backend_api import EEECareerPlatform
    platform = EEECareerPlatform()
    platform.load()
    return platform


# def load_platform_with_status():
#     try:
#         return _get_platform(), None
#     except Exception as exc:
#         return None, str(exc)

# platform, err = load_platform_with_status()

# if err or platform is None:
#     st.error(
#         f"**Backend initialisation failed.**\n\n{err}\n\n"
#         "Check that all four Excel files exist in the `Data/` folder and that "
#         "all Python dependencies are installed."
#     )
#     st.stop()

def load_platform_with_status():
    try:
        return _get_platform(), None
    except Exception as exc:
        import traceback
        return None, traceback.format_exc()  # ← FULL traceback

platform, err = load_platform_with_status()

if err or platform is None:
    st.error("**Backend initialisation failed.**")
    st.code(err, language="python")  # ← shows exact file AND line number
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

def detect_soft_skills_from_text(cv_text: str) -> list:
    """Scan raw CV text for soft skill indicators using broad keyword matching."""
    text_lower = cv_text.lower()
    found = []
    for dim, keywords in SOFT_SKILL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(dim)
    return found



def _build_system_prompt() -> str:
    try:
        sectors = platform.get_sectors()
        sector_list = ", ".join(s.title() for s in sectors)
    except Exception:
        sector_list = "Semiconductor, ICT, Power & Energy, Telecommunications, Defence, Biomedical, Aerospace"
    return f"""You are an EEE (Electrical & Electronic Engineering) Career Advisor chatbot \
embedded in the EEE Career Pathways platform.

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
When asked about specific roles or skills, give concrete, practical advice for EEE students."""


def build_radar_chart(soft_skills_found):
    """Radar chart across all 10 soft skill dimensions; 100 if found, 0 if not."""
    found_set = {s.lower() for s in soft_skills_found}
    labels = [s.title() for s in SOFT_SKILL_DIMS]
    values = [100 if dim in found_set else 0 for dim in SOFT_SKILL_DIMS]
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

def _render_skills_graph(skills_tree: list) -> None:
    import json as _json

    category_colors = {
        "Foundational": "#4caf50",
        "Advanced":     "#2196f3",
        "Future":       "#ff9800",
        "Mastery":      "#9c27b0",
        "Implied":      "#9e9e9e",  # ghost nodes for unlisted dependencies
    }

    # ── Build node list, adding implied nodes for missing dependencies ────────
    existing_names = {s["name"] for s in skills_tree}

    # Collect all dependency names that have no corresponding node
    implied_names = set()
    for skill in skills_tree:
        for dep in skill.get("dependencies", []):
            if dep not in existing_names:
                implied_names.add(dep)

    # Full node list = real nodes + implied nodes appended at the end
    all_skills = list(skills_tree) + [
        {
            "name":         name,
            "category":     "Implied",
            "proficiency":  0,
            "importance":   2,   # small but visible
            "dependencies": [],
            "description":  "Referenced as a prerequisite — not yet in your roadmap.",
            "justification": "",
            "resources":    "",
        }
        for name in sorted(implied_names)
    ]

    nodes = []
    links = []
    name_to_id = {s["name"]: i for i, s in enumerate(all_skills)}

    for i, skill in enumerate(all_skills):
        nodes.append({
            "id":            i,
            "name":          skill.get("name", ""),
            "category":      skill.get("category", "Other"),
            "proficiency":   skill.get("proficiency", 0),
            "importance":    skill.get("importance", 3),
            "color":         category_colors.get(skill.get("category", ""), "#9e9e9e"),
            "description":   skill.get("description", ""),
            "justification": skill.get("justification", ""),
            "prerequisites": skill.get("dependencies", []),
            "resources":     skill.get("resources", ""),
            "implied":       skill.get("category") == "Implied",
        })
        for dep in skill.get("dependencies", []):
            if dep in name_to_id:
                links.append({"source": name_to_id[dep], "target": i})

    nodes_json = _json.dumps(nodes)
    links_json = _json.dumps(links)

    # ── List view — only show real nodes, not implied ones ────────────────────
    category_order = ["Foundational", "Advanced", "Future", "Mastery"]

    list_html_parts = []
    for cat in category_order:
        cat_skills = [s for s in skills_tree if s.get("category") == cat]
        if not cat_skills:
            continue
        color = category_colors.get(cat, "#9e9e9e")
        list_html_parts.append(
            f"<p style='margin:0.8rem 0 0.3rem;font-weight:600;"
            f"color:{color};font-size:0.95rem'>{cat}</p>"
        )
        for skill in cat_skills:
            name          = skill.get("name", "")
            prof          = int(skill.get("proficiency", 0))
            importance    = int(skill.get("importance", 3))
            pct           = prof * 20
            deps          = skill.get("dependencies", [])
            desc          = skill.get("description", "")
            justification = skill.get("justification", "")
            resources     = skill.get("resources", "")

            deps_html = (
                f"<p style='font-size:0.82rem;color:#888;margin:0.3rem 0'>"
                f"Builds on: {', '.join(deps)}</p>"
                if deps else ""
            )
            desc_html = (
                f"<p style='font-size:0.82rem;color:#444;margin:0.3rem 0'>"
                f"<strong>About:</strong> {desc}</p>"
                if desc else ""
            )
            just_html = (
                f"<p style='font-size:0.82rem;color:#444;margin:0.3rem 0'>"
                f"<strong>Why:</strong> {justification}</p>"
                if justification else ""
            )
            res_html = (
                f"<p style='font-size:0.82rem;color:#555;margin:0.3rem 0'>"
                f"<strong>Resources:</strong> {resources}</p>"
                if resources else ""
            )

            list_html_parts.append(
                f"<div style='background:#f8f9fa;border-radius:8px;padding:0.7rem 1rem;"
                f"margin:0.3rem 0;border-left:4px solid {color}'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                f"<span style='font-size:0.9rem;font-weight:600'>{name}</span>"
                f"<span style='font-size:0.8rem;color:#666'>"
                f"Proficiency {prof}/5 · Importance {importance}/5</span></div>"
                f"<div style='background:#e0e0e0;border-radius:1rem;height:8px;"
                f"overflow:hidden;margin:5px 0'>"
                f"<div style='height:100%;border-radius:1rem;width:{pct}%;"
                f"background:{color}'></div></div>"
                f"{desc_html}{just_html}{deps_html}{res_html}"
                f"</div>"
            )

    list_html = "\n".join(list_html_parts)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: sans-serif; }}

  #toggle-bar {{
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
    justify-content: flex-end;
  }}
  .toggle-btn {{
    padding: 5px 14px;
    border-radius: 20px;
    border: 1.5px solid #667eea;
    background: white;
    color: #667eea;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }}
  .toggle-btn.active {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-color: transparent;
  }}

  #graph-wrap {{ display: block; }}
  #list-wrap  {{ display: none;  }}

  #graph-container {{
    width: 100%;
    height: 680px;
    background: linear-gradient(135deg, #f8f9ff 0%, #f0f2fa 100%);
    border-radius: 1rem;
    overflow: hidden;
    position: relative;
    cursor: grab;
  }}
  #graph-container:active {{ cursor: grabbing; }}
  svg {{ width: 100%; height: 100%; }}

  .node circle {{
    stroke-width: 3px;
    cursor: pointer;
    transition: filter 0.2s;
  }}
  .node:hover circle {{ filter: brightness(1.2); }}
  .node.selected circle {{
    filter: brightness(1.1) drop-shadow(0 0 10px rgba(0,0,0,0.3));
  }}
  .node text {{
    font-size: 20px;
    fill: #333;
    pointer-events: none;
    font-weight: 500;
  }}
  .node.implied-node circle {{
    stroke-dasharray: 5 3;
    stroke-width: 2px;
  }}
  .node.implied-node text {{
    fill: #999;
    font-style: italic;
  }}
  .link {{
    stroke: #c0c8e0;
    stroke-width: 1.5px;
    stroke-dasharray: 4 3;
    fill: none;
    marker-end: url(#arrowhead);
  }}
  .link.highlighted {{
    stroke: #667eea;
    stroke-width: 2.5px;
    stroke-dasharray: none;
    marker-end: url(#arrowhead-hl);
  }}

  #detail-panel {{
    display: none;
    background: white;
    border-radius: 0.8rem;
    padding: 1.2rem 1.4rem;
    margin-top: 0.8rem;
    border-left: 5px solid #667eea;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    animation: slideIn 0.18s ease;
  }}
  @keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(-6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  .dp-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.6rem;
  }}
  #dp-name {{
    color: #1e3c72;
    font-size: 1.05rem;
    margin: 0;
    flex: 1;
    font-weight: 600;
  }}
  #dp-close {{
    background: none; border: none; font-size: 1.1rem;
    cursor: pointer; color: #999; padding: 0 0 0 12px; line-height: 1;
  }}
  #dp-close:hover {{ color: #333; }}
  .badge {{
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 0.78rem; color: white; margin-right: 6px; margin-bottom: 8px;
  }}
  .dp-stat {{
    display: inline-block; background: #f0f2fa; border-radius: 8px;
    padding: 3px 10px; font-size: 0.8rem; color: #444;
    margin-right: 6px; margin-bottom: 8px;
  }}
  .dp-section-label {{
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em; color: #888; margin: 0.8rem 0 0.25rem;
  }}
  .dp-text {{
    font-size: 0.88rem; color: #444; line-height: 1.55; margin: 0;
  }}
  .dp-pill {{
    display: inline-block; background: #e8f4fd; border: 1px solid #4a90d9;
    border-radius: 14px; padding: 2px 10px; margin: 2px 3px;
    font-size: 0.8rem; color: #1a5276;
  }}
  .implied-notice {{
    display: inline-block; background: #f5f5f5; border: 1px solid #ddd;
    border-radius: 8px; padding: 4px 10px; font-size: 0.8rem;
    color: #888; font-style: italic; margin-bottom: 6px;
  }}

  .legend {{
    position: absolute; bottom: 12px; left: 16px;
    display: flex; gap: 14px; align-items: center; pointer-events: none;
  }}
  .legend-item {{
    display: flex; align-items: center; gap: 5px;
    font-size: 11px; color: #555;
  }}
  .legend-dot {{
    width: 10px; height: 10px; border-radius: 50%;
  }}
  .legend-dot.implied {{
    background: white !important;
    border: 2px dashed #9e9e9e;
  }}
  .hint {{
    position: absolute; top: 10px; right: 14px;
    font-size: 10px; color: #aaa; pointer-events: none;
  }}
</style>
</head>
<body>

<div id="toggle-bar">
  <button class="toggle-btn active" id="btn-graph" onclick="showView('graph')">&#9901; Graph view</button>
  <button class="toggle-btn"        id="btn-list"  onclick="showView('list')">&#9776; List view</button>
</div>

<div id="graph-wrap">
  <div id="graph-container">
    <svg id="graph-svg">
      <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="17" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#c0c8e0"/>
        </marker>
        <marker id="arrowhead-hl" markerWidth="8" markerHeight="6" refX="17" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#667eea"/>
        </marker>
      </defs>
      <g id="zoom-group"></g>
    </svg>
    <div class="legend">
      <div class="legend-item"><div class="legend-dot" style="background:#4caf50"></div>Foundational</div>
      <div class="legend-item"><div class="legend-dot" style="background:#2196f3"></div>Advanced</div>
      <div class="legend-item"><div class="legend-dot" style="background:#ff9800"></div>Future</div>
      <div class="legend-item"><div class="legend-dot" style="background:#9c27b0"></div>Mastery</div>
      <div class="legend-item"><div class="legend-dot implied"></div>Prerequisite</div>
    </div>
    <div class="hint">Scroll to zoom · Drag to pan · Click node for details</div>
  </div>

  <div id="detail-panel">
    <div class="dp-header">
      <h4 id="dp-name"></h4>
      <button id="dp-close" onclick="closePanel()">&#x2715;</button>
    </div>
    <div id="dp-implied-notice" style="display:none">
      <span class="implied-notice">&#x26AC; Prerequisite — not yet in your roadmap</span>
    </div>
    <div id="dp-badges"></div>
    <div id="dp-description-section" style="display:none">
      <div class="dp-section-label">About</div>
      <p class="dp-text" id="dp-description"></p>
    </div>
    <div id="dp-justification-section" style="display:none">
      <div class="dp-section-label">Why this matters</div>
      <p class="dp-text" id="dp-justification"></p>
    </div>
    <div id="dp-prereqs-section" style="display:none">
      <div class="dp-section-label">Builds on</div>
      <div id="dp-prereqs"></div>
    </div>
    <div id="dp-resources-section" style="display:none">
      <div class="dp-section-label">Resources</div>
      <p class="dp-text" id="dp-resources"></p>
    </div>
  </div>
</div>

<div id="list-wrap">
  {list_html}
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
function showView(v) {{
  document.getElementById("graph-wrap").style.display = v === "graph" ? "block" : "none";
  document.getElementById("list-wrap").style.display  = v === "list"  ? "block" : "none";
  document.getElementById("btn-graph").classList.toggle("active", v === "graph");
  document.getElementById("btn-list").classList.toggle("active",  v === "list");
  if (v === "graph") centreGraph();
}}

const nodes = {nodes_json};
const links = {links_json};

const container = document.getElementById("graph-container");

setTimeout(() => {{
  const W = container.clientWidth  || 800;
  const H = container.clientHeight || 680;

  const svg  = d3.select("#graph-svg");
  const g    = d3.select("#zoom-group");

  const zoom = d3.zoom()
    .scaleExtent([0.3, 3])
    .on("zoom", e => g.attr("transform", e.transform));
  svg.call(zoom);

  function centreGraph() {{
    const xs = nodes.map(d => d.x).filter(x => x != null && isFinite(x));
    const ys = nodes.map(d => d.y).filter(y => y != null && isFinite(y));
    if (!xs.length) return;
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const gW = maxX - minX + 120;
    const gH = maxY - minY + 120;
    const scale = Math.min(W / gW, H / gH, 1.0) * 0.85;
    const tx = (W - scale * (minX + maxX)) * 2;
    const ty = (H - scale * (minY + maxY)) / 2;
    svg.transition().duration(500).call(
      zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale)
    );
  }}

  // Implied nodes are smaller; real nodes scale with importance
  function nodeRadius(d) {{
    return d.implied ? 24 : 40 + d.importance * 6;
  }}

  const sim = d3.forceSimulation(nodes)
    .force("link",    d3.forceLink(links).id(d => d.id).distance(180).strength(0.5))
    .force("charge",  d3.forceManyBody().strength(-500))
    .force("center",  d3.forceCenter(W / 2, H / 2))
    .force("collide", d3.forceCollide().radius(d => nodeRadius(d) + 24));

  const link = g.append("g")
    .selectAll("path").data(links).join("path").attr("class", "link");

  const node = g.append("g")
    .selectAll("g").data(nodes).join("g")
    .attr("class", d => d.implied ? "node implied-node" : "node")
    .call(d3.drag()
      .on("start", (e, d) => {{ if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
      .on("drag",  (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
      .on("end",   (e, d) => {{ if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }})
    );

  node.append("circle")
    .attr("r",      nodeRadius)
    .attr("fill",   d => d.implied ? "#f5f5f5" : d.color + "22")
    .attr("stroke", d => d.implied ? "#bbb"    : d.color);

  // Proficiency arc — only on real nodes
  node.each(function(d) {{
    if (!d.implied && d.proficiency > 0) {{
      const r = nodeRadius(d);
      const arc = d3.arc()
        .innerRadius(r - 4).outerRadius(r)
        .startAngle(0)
        .endAngle((d.proficiency / 5) * 2 * Math.PI);
      d3.select(this).append("path")
        .attr("d", arc).attr("fill", d.color).attr("opacity", 0.9);
    }}
  }});

  node.append("text")
    .attr("text-anchor", "middle")
    .attr("dy", d => nodeRadius(d) + 15)
    .each(function(d) {{
      const words = d.name.split(" ");
      const lines = [];
      let cur = "";
      words.forEach(w => {{
        if ((cur + " " + w).trim().length > 16 && cur) {{
          lines.push(cur.trim()); cur = w;
        }} else {{
          cur = (cur + " " + w).trim();
        }}
      }});
      if (cur) lines.push(cur);
      lines.forEach((line, i) => {{
        d3.select(this).append("tspan")
          .attr("x", 0).attr("dy", i === 0 ? 0 : "1.15em").text(line);
      }});
    }});

  node.on("click", (e, d) => {{
    e.stopPropagation();

    link
      .attr("class",      l => (l.source.id === d.id || l.target.id === d.id) ? "link highlighted" : "link")
      .attr("marker-end", l => (l.source.id === d.id || l.target.id === d.id) ? "url(#arrowhead-hl)" : "url(#arrowhead)");
    node.classed("selected", n => n.id === d.id);

    document.getElementById("dp-name").textContent = d.name;
    document.getElementById("detail-panel").style.borderLeftColor = d.implied ? "#bbb" : d.color;

    // Show/hide implied notice
    document.getElementById("dp-implied-notice").style.display = d.implied ? "block" : "none";

    document.getElementById("dp-badges").innerHTML = d.implied
      ? "<span class='dp-stat' style='color:#999'>Prerequisite node</span>"
      : "<span class='badge' style='background:" + d.color + "'>" + d.category + "</span>" +
        "<span class='dp-stat'>Proficiency " + d.proficiency + " / 5</span>" +
        "<span class='dp-stat'>Importance " + d.importance + " / 5</span>";

    function toggleSection(sectionId, elId, content) {{
      const section = document.getElementById(sectionId);
      if (content) {{
        document.getElementById(elId).textContent = content;
        section.style.display = "block";
      }} else {{
        section.style.display = "none";
      }}
    }}

    toggleSection("dp-description-section",   "dp-description",   d.description);
    toggleSection("dp-justification-section", "dp-justification", d.justification);
    toggleSection("dp-resources-section",     "dp-resources",     d.resources);

    const prereqSection = document.getElementById("dp-prereqs-section");
    if (d.prerequisites && d.prerequisites.length > 0) {{
      document.getElementById("dp-prereqs").innerHTML =
        d.prerequisites.map(p => "<span class='dp-pill'>" + p + "</span>").join("");
      prereqSection.style.display = "block";
    }} else {{
      prereqSection.style.display = "none";
    }}

    const panel = document.getElementById("detail-panel");
    panel.style.display = "block";
    setTimeout(() => panel.scrollIntoView({{ behavior: "smooth", block: "nearest" }}), 50);
  }});

  function closePanel() {{
    document.getElementById("detail-panel").style.display = "none";
    link.attr("class", "link").attr("marker-end", "url(#arrowhead)");
    node.classed("selected", false);
  }}

  svg.on("click", () => closePanel());

  let tickCount = 0;
  sim.on("tick", () => {{
    tickCount++;
    link.attr("d", d => {{
      const dx = d.target.x - d.source.x;
      const dy = d.target.y - d.source.y;
      const dr = Math.sqrt(dx * dx + dy * dy) * 1.3;
      return `M${{d.source.x}},${{d.source.y}}A${{dr}},${{dr}} 0 0,1 ${{d.target.x}},${{d.target.y}}`;
    }});
    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
    if (tickCount === 80) centreGraph();
  }});

  sim.on("end", () => centreGraph());

}}, 120);
</script>
</body>
</html>
"""
    components.html(html, height=1000, scrolling=True)

def generate_interview_pdf(conversation: list, career_goal: str, interview_type: str) -> bytes:
    """
    Generate a PDF transcript of the interview session.
    Returns raw PDF bytes for st.download_button.
    """
    from fpdf import FPDF
    import datetime

    class InterviewPDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(30, 60, 114)
            self.cell(0, 10, "EEE Career Pathways — Interview Transcript", ln=True, align="C")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%d %B %Y, %H:%M')}", ln=True, align="C")
            self.ln(4)
            self.set_draw_color(102, 126, 234)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = InterviewPDF()
    pdf.set_margins(15, 20, 15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Session metadata
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 114)
    pdf.cell(0, 8, "Session Details", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(40, 6, "Career Goal:", ln=False)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, career_goal or "Not specified", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(40, 6, "Interview Type:", ln=False)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, interview_type or "Not specified", ln=True)
    pdf.ln(4)

    # Conversation
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    for msg in conversation:
        is_agent = msg["role"] == "assistant"

        # Speaker label
        if is_agent:
            pdf.set_fill_color(240, 242, 250)
            pdf.set_text_color(30, 60, 114)
            label = "Interviewer (AI)"
        else:
            pdf.set_fill_color(232, 245, 233)
            pdf.set_text_color(27, 94, 32)
            label = "Student"

        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, label, ln=True, fill=False)

        # Message body
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)

        # Handle long text with multi_cell — encode safely
        content = msg["content"].encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 5.5, content, border=0)
        pdf.ln(3)

    return bytes(pdf.output())

# ========== Sidebar Chat HTML Renderer ==========

def _build_chat_html(history: list) -> str:
    """
    Renders the full conversation as a self-contained HTML bubble layout
    with auto-scroll to the latest message.
    """
    msgs = ""
    for msg in history:
        # Sanitise and lightly format the text
        safe = _html.escape(msg["text"])
        safe = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe)
        safe = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         safe)
        safe = safe.replace('\n', '<br>')

        if msg["role"] == "bot":
            msgs += f"""
            <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:14px;">
              <div style="min-width:32px;height:32px;border-radius:50%;
                background:linear-gradient(135deg,#1e3c72,#2a5298);
                display:flex;align-items:center;justify-content:center;
                font-size:16px;flex-shrink:0;">🤖</div>
              <div style="background:white;border-radius:4px 18px 18px 18px;
                padding:10px 14px;max-width:86%;font-size:12.5px;line-height:1.65;
                color:#1a1a2e;box-shadow:0 2px 10px rgba(0,0,0,0.09);">{safe}</div>
            </div>"""
        else:
            msgs += f"""
            <div style="display:flex;align-items:flex-start;gap:8px;
              margin-bottom:14px;flex-direction:row-reverse;">
              <div style="min-width:32px;height:32px;border-radius:50%;
                background:linear-gradient(135deg,#667eea,#764ba2);
                display:flex;align-items:center;justify-content:center;
                font-size:16px;flex-shrink:0;">🎓</div>
              <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                border-radius:18px 4px 18px 18px;padding:10px 14px;max-width:86%;
                font-size:12.5px;line-height:1.65;color:white;">{safe}</div>
            </div>"""

    if not msgs:
        msgs = (
            '<p style="text-align:center;color:#aaa;font-size:12px;padding:24px 0;">'
            'Ask me anything below 👇</p>'
        )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(160deg, #f0f4ff 0%, #f5f0ff 100%);
    padding: 12px 10px;
  }}
</style></head>
<body>
  {msgs}
  <div id="scroll-anchor"></div>
  <script>
    document.getElementById("scroll-anchor").scrollIntoView({{ behavior: "smooth" }});
  </script>
</body></html>"""

# ========== Sidebar Chatbot (Azure AI Agent) ==========

# Initialise chat history with a welcome message
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {
            "role": "bot",
            "text": (
                "Hi! 👋 I'm your EEE Career Advisor, powered by Azure AI.\n\n"
                "I can help with:\n"
                "• **Career paths** for EEE graduates\n"
                "• **Salary benchmarks** in Singapore\n"
                "• **Skills** to develop for your target role\n"
                "• **Internship & job search** tips\n\n"
                "Ask me anything, or tap a suggestion below!"
            ),
        }
    ]

with st.sidebar:
    st.markdown("### 🤖 EEE Career Advisor")
    st.markdown(
        "<small style='color:#888'>Powered by Azure AI Foundry</small>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Busy indicator ────────────────────────────────────────────────────
    is_busy = st.session_state.get("_chat_busy", False)
    if is_busy:
        st.markdown(
            "<div style='text-align:center;font-size:0.78rem;color:#999;padding:4px 0;'>"
            "⏳ Thinking…</div>",
            unsafe_allow_html=True,
        )

    # ── Chat bubble display ───────────────────────────────────────────────
    components.html(
        _build_chat_html(st.session_state["chat_history"]),
        height=420,
        scrolling=True,
    )

    # ── Chat input ────────────────────────────────────────────────────────
    user_msg = st.chat_input("Ask about EEE careers…", key="chatbot_input")

    if user_msg and not is_busy:
        st.session_state["_chat_busy"] = True
        st.session_state["chat_history"].append({"role": "user", "text": user_msg})

        # Pass CV and career goal as context if available
        _cv_ctx    = st.session_state.get("_cv_text")
        _goal_ctx  = st.session_state.get("_agent_result_key", "").split("|")[-1] or None

        with st.spinner("Thinking…"):
            try:
                reply = query_chat_agent(
                    conversation=st.session_state["chat_history"],
                    cv_text=_cv_ctx,
                    career_goal=_goal_ctx,
                )
            except Exception as _e:
                reply = f"⚠️ Agent error: {_e}"

        st.session_state["chat_history"].append({"role": "bot", "text": reply})
        st.session_state["_chat_busy"] = False
        st.rerun()

    # ── Smart follow-up suggestions ───────────────────────────────────────
    if st.session_state["chat_history"] and not is_busy:
        last_bot = next(
            (m["text"] for m in reversed(st.session_state["chat_history"])
             if m["role"] == "bot"),
            "",
        )
        # _follow_map = [
        #     (
        #         ["salary", "pay", "compensation", "earn"],
        #         [
        #             ("💰 Fresh grad pay?",
        #              "What is the typical fresh graduate salary for EEE in Singapore?"),
        #             ("📈 Salary growth?",
        #              "How does EEE salary grow with years of experience?"),
        #         ],
        #     ),
        #     (
        #         ["skill", "python", "matlab", "machine learn", "learn"],
        #         [
        #             ("🛠️ Must-have skills?",
        #              "What are the top 3 must-have technical skills for EEE graduates?"),
        #             ("📚 Best resources?",
        #              "What are the best free resources to learn these skills?"),
        #         ],
        #     ),
        #     (
        #         ["internship", "intern", "placement"],
        #         [
        #             ("🔍 How to find one?",
        #              "How do I find EEE internships in Singapore?"),
        #             ("📄 Application tips?",
        #              "What should I include in my internship application?"),
        #         ],
        #     ),
        #     (
        #         ["cv", "resume", "portfolio"],
        #         [
        #             ("✅ CV checklist?",
        #              "What should every EEE student include in their CV?"),
        #             ("⚠️ Common mistakes?",
        #              "What are the most common CV mistakes EEE students make?"),
        #         ],
        #     ),
        #     (
        #         ["career", "path", "role", "job", "sector", "industry"],
        #         [
        #             ("🚀 Best entry roles?",
        #              "What are the best entry-level roles for EEE graduates?"),
        #             ("🏢 Top employers?",
        #              "Which companies hire the most EEE graduates in Singapore?"),
        #         ],
        #     ),
        # ]

        suggestions = []
        last_lower = last_bot.lower()
        # for keywords, prompts in _follow_map:
        #     if any(k in last_lower for k in keywords):
        #         suggestions = prompts
        #         break

        if suggestions:
            st.markdown(
                "<p style='font-size:0.72rem;color:#aaa;margin:6px 0 4px;"
                "text-align:center;'>💡 Suggested follow-ups</p>",
                unsafe_allow_html=True,
            )
            s_cols = st.columns(len(suggestions))
            for ci, (label, prompt) in enumerate(suggestions):
                with s_cols[ci]:
                    if st.button(label, key=f"sugg_{ci}_{label[:8]}"):
                        st.session_state["_chat_busy"] = True
                        st.session_state["chat_history"].append(
                            {"role": "user", "text": prompt}
                        )
                        _cv_ctx   = st.session_state.get("_cv_text")
                        _goal_ctx = st.session_state.get("_agent_result_key", "").split("|")[-1] or None
                        with st.spinner("Thinking…"):
                            try:
                                reply = query_chat_agent(
                                    conversation=st.session_state["chat_history"],
                                    cv_text=_cv_ctx,
                                    career_goal=_goal_ctx,
                                )
                            except Exception as _e:
                                reply = f"⚠️ Agent error: {_e}"
                        st.session_state["chat_history"].append(
                            {"role": "bot", "text": reply}
                        )
                        st.session_state["_chat_busy"] = False
                        st.rerun()

    st.markdown("---")

    # ── Clear & Close ─────────────────────────────────────────────────────
    clear_col, close_col = st.columns(2)
    with clear_col:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_chat_btn"):
            st.session_state["chat_history"] = [
                {
                    "role": "bot",
                    "text": "Chat cleared! What would you like to know about EEE careers?",
                }
            ]
            st.rerun()
    with close_col:
        if st.button(
            "✕ Close",
            key="close_sidebar_btn",
            use_container_width=True,
        ):
            st.session_state["sidebar_visible"] = False
            st.rerun()

# ── Chat open button (sits below the main header) ─────────────────────────
_hcol1, _hcol2 = st.columns([5, 1])
with _hcol2:
    if st.button(
        "💬 AI Advisor",
        type="primary",
        use_container_width=True,
        key="open_chat_header_btn",
    ):
        st.session_state["sidebar_visible"] = True
        st.rerun()
# ========== Tabs ==========
# tab_profile, tab_roadmap = st.tabs(["👤 My Profile", "🗺️ My Roadmap"])

# ==================== TAB 1: Explore Jobs ====================
# with tab1:
#     st.markdown("<h2 class='section-header'>🔍 Explore Career Opportunities</h2>", unsafe_allow_html=True)
#     col1, col2 = st.columns([1, 2])

#     with col1:
#         st.markdown("<div class='glass-card'><h4>🏢 Select Industry</h4></div>", unsafe_allow_html=True)
#         sectors = platform.get_sectors()
#         selected_sector = st.selectbox("Sector:", sectors, key="sector",
#                                        label_visibility="collapsed",
#                                        format_func=str.title)

#     if selected_sector:
#         job_titles = platform.get_job_titles(selected_sector)
#         with col2:
#             st.markdown("<div class='glass-card'><h4>🎯 Select Position</h4></div>", unsafe_allow_html=True)
#             selected_job = st.selectbox("Position:", job_titles, key="job",
#                                         label_visibility="collapsed",
#                                         format_func=str.title)

#         if selected_job:
#             m1, m2, m3, m4 = st.columns(4)
#             for col, (icon, label) in zip([m1, m2, m3, m4], [
#                 ("🏢", selected_sector.title()[:15]),
#                 ("💼", selected_job.title()[:15]),
#                 ("📍", "General"),
#                 ("⭐", "Featured")
#             ]):
#                 with col:
#                     st.markdown(f"<div class='metric-container'><div class='metric-value'>{icon}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

#             col_a, col_b = st.columns([3, 2])

#             with col_a:
#                 st.markdown("<div class='glass-card'><h4>📖 Job Description</h4></div>", unsafe_allow_html=True)
#                 job_desc = platform.get_job_description(selected_sector, selected_job) or ""
#                 st.write(job_desc if job_desc else "No description available.")

#                 st.markdown("<div class='gradient-card'><h4>🛠️ Skills Summary</h4></div>", unsafe_allow_html=True)
#                 tsc_skills = platform.get_raw_tsc_skills(selected_sector, selected_job)
#                 if tsc_skills:
#                     with st.expander("View detailed skills"):
#                         for s in tsc_skills:
#                             st.markdown(f"**{s['skill']}** — Level {s['level']}")
#                             if s['description']:
#                                 st.caption(s['description'])
#                     with st.spinner("Generating AI summary…"):
#                         try:
#                             summary = platform.get_tsc_summary(selected_sector, selected_job)
#                             st.info(summary)
#                         except Exception as e:
#                             st.warning(f"AI summary unavailable: {e}")
#                 else:
#                     st.info("No technical skills data available for this role.")

#             with col_b:
#                 # --- Recommended Courses ---
#                 st.markdown("<div class='gradient-card-blue'><h4>📚 Recommended Courses</h4></div>", unsafe_allow_html=True)
#                 if job_desc:
#                     with st.spinner("Finding courses..."):
#                         try:
#                             courses = platform.get_top_courses(selected_sector, selected_job, top_n=5)
#                         except Exception as e:
#                             courses = []
#                             st.warning(f"Course matching error: {e}")
#                     for i, c in enumerate(courses, 1):
#                         st.markdown(f"<div class='course-card'><strong>{i}. {c['code']}</strong><br>{c['name'].title()}<br><small>Relevance: {c['score']*100:.0f}%</small></div>", unsafe_allow_html=True)
#                 else:
#                     st.info("No job description available for course matching.")


# # ==================== TAB 2: CV Analysis ====================
# ==================== TAB 2: AI CV Analysis ====================
# ==================== TAB 2: AI CV Analysis ====================
from agent_api import query_agent, query_job_match_agent, query_interview_agent  # lazy import keeps startup fast

st.markdown(
    "<h2 class='section-header'>📄 CV Analysis & AI Career Advisor</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='success-box'><strong>✅ Powered by Azure AI Agent:</strong> "
    "Upload your CV and select or type a career goal for personalised advice, "
    "job matches, skills analysis, and course recommendations.</div>",
    unsafe_allow_html=True,
)

# ── CV Upload ──────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📤 Upload Your CV (PDF)",
    type=["pdf"],
    label_visibility="collapsed",
    key="cv_upload",
)

cv_text = None
if uploaded_file:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.get("_cv_file_key") != file_key:
        with st.spinner("Extracting CV text…"):
            try:
                cv_text = platform.extract_text_from_pdf(uploaded_file)
                st.session_state["_cv_file_key"] = file_key
                st.session_state["_cv_text"] = cv_text
            except Exception as e:
                st.error(f"❌ PDF extraction failed: {e}")
    else:
        cv_text = st.session_state.get("_cv_text")

    if cv_text:
        st.success(f"✅ CV loaded — {len(cv_text):,} characters extracted")
        with st.expander("🔍 Preview extracted text"):
            st.text_area("First 2000 chars", cv_text[:2000], height=120)

# ── Career Goal ────────────────────────────────────────────────────────────
st.markdown("### 🎯 Career Goal")

PRESET_GOALS = [
    "— type your own below —",
    "I want to become a Machine Learning Engineer",
    "I want to work in Power Systems / Renewable Energy",
    "I want to become an Embedded Systems Engineer",
    "I want to work in VLSI / Chip Design",
    "I want to pursue a career in RF / Communications Engineering",
    "I want to become a Control Systems / Robotics Engineer",
    "I want to move into Data Engineering or Data Science",
    "I want to work in Semiconductor / Fab / Process Engineering",
    "I want to enter Finance / Quantitative Analysis",
    "I want to work in IoT / Smart Systems",
]

goal_col, custom_col = st.columns([2, 3])
with goal_col:
    selected_preset = st.selectbox("Choose a preset goal:", PRESET_GOALS)
with custom_col:
    prefill = selected_preset if selected_preset != PRESET_GOALS[0] else ""
    custom_query = st.text_input(
        "Or type / refine your goal:",
        value=prefill,
        placeholder="e.g. I want to specialise in power electronics at a startup",
    )

final_query = custom_query.strip() or (
    selected_preset if selected_preset != PRESET_GOALS[0] else ""
)
if final_query:
    st.markdown(
        f"<div class='info-box'>🎯 <strong>Goal:</strong> {final_query}</div>",
        unsafe_allow_html=True,
    )

# ── Submit ─────────────────────────────────────────────────────────────────
analyse_clicked = st.button(
    "🤖 Analyse with AI Agent",
    disabled=not bool(final_query),
)

# Cache invalidation: re-run only when CV or query actually changes
result_key = f"{st.session_state.get('_cv_file_key', 'nocv')}|{final_query}"
if analyse_clicked:
    st.session_state["_agent_result_key"] = None  # force fresh call

if analyse_clicked and final_query:
    with st.spinner("🤖 Agent is analysing your CV and career goal…"):
        try:
            result = query_agent(user_query=final_query, cv_text=cv_text)
            st.session_state["_agent_result"] = result
            st.session_state["_agent_result_key"] = result_key
        except Exception as e:
            st.error(f"❌ Agent call failed: {e}")
            with st.expander("Debug info"):
                st.exception(e)
            result = None
else:
    cached = st.session_state.get("_agent_result")
    result = (
        cached
        if st.session_state.get("_agent_result_key") == result_key
        else None
    )

# ── Results ────────────────────────────────────────────────────────────────
if result:

    if "raw_text" in result and len(result) <= 3:
        st.markdown("### 🤖 Agent Response")
        st.markdown(result["raw_text"])

    else:
        tab_profile, tab_roadmap, tab_jobs, tab_interview = st.tabs([
            "👤 My Profile", "🗺️ My Roadmap", "🎯 Job Match", "🎤 Interview Prep"
        ])

        # ══════════════════════════════════════════════════════════════════
        # TAB: MY PROFILE
        # ══════════════════════════════════════════════════════════════════
        with tab_profile:

            # ── Relevant Modules ──────────────────────────────────────────
            my_modules = result.get("my_modules", [])
            if my_modules:
                st.markdown(
                    "<div class='gradient-card-blue'><h4>📚 Relevant Modules</h4></div>",
                    unsafe_allow_html=True,
                )
                cols = st.columns(3)
                for i, mod in enumerate(my_modules):
                    with cols[i % 3]:
                        name = mod.get("Name of Module", "Module")
                        desc = mod.get("Description of Module", "")
                        st.markdown(
                            f"<div class='glass-card' style='min-height:130px'>"
                            f"<strong>{name}</strong><br>"
                            f"<small style='color:#666'>{desc[:160]}{'…' if len(desc) > 160 else ''}</small>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

            # ── Relevant Experiences ──────────────────────────────────────
            my_experiences = result.get("my_experiences", [])
            if my_experiences:
                st.markdown(
                    "<div class='gradient-card'><h4>💼 Relevant Experiences</h4></div>",
                    unsafe_allow_html=True,
                )
                type_colors = {
                    "Industry": "#4caf50",
                    "Academia": "#2196f3",
                    "Personal": "#ff9800",
                }
                for exp in my_experiences:
                    title = exp.get("Title of Experience", "Experience")
                    exp_type = exp.get("Type of Experience", "")
                    desc = exp.get("Description of Experience", "")
                    color = type_colors.get(exp_type, "#9e9e9e")
                    st.markdown(
                        f"<div class='job-card high-match'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
                        f"<strong>{title}</strong>"
                        f"<span style='background:{color};color:white;padding:2px 10px;"
                        f"border-radius:12px;font-size:0.8rem;white-space:nowrap;margin-left:8px'>"
                        f"{exp_type}</span></div>"
                        f"<p style='margin:0.4rem 0 0;font-size:0.9rem;color:#444'>{desc}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            # ── Current Skills ────────────────────────────────────────────
            my_skills = result.get("my_skills", [])
            if my_skills:
                st.markdown(
                    "<div class='gradient-card-blue'><h4>🛠️ Current Skills</h4></div>",
                    unsafe_allow_html=True,
                )
                skill_cols = st.columns(2)
                for i, skill in enumerate(my_skills):
                    with skill_cols[i % 2]:
                        name = skill.get("Name of Skill", "Skill")
                        prof = int(skill.get("Proficiency of Skill", 0))
                        justification = skill.get("Justification", "")
                        pct = prof * 20
                        st.markdown(
                            f"<div style='margin:0.4rem 0'>"
                            f"<div style='display:flex;justify-content:space-between'>"
                            f"<span><strong>{name}</strong></span>"
                            f"<span style='color:#667eea;font-weight:600'>{prof}/5</span></div>"
                            f"<div class='skill-progress'>"
                            f"<div class='skill-progress-fill' style='width:{pct}%'></div></div>"
                            f"<small style='color:#666'>{justification}</small>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

        # ══════════════════════════════════════════════════════════════════
        # TAB: MY ROADMAP
        # ══════════════════════════════════════════════════════════════════
        with tab_roadmap:

            # ── Future Modules ────────────────────────────────────────────
            future_modules = result.get("future_modules", [])
            if future_modules:
                st.markdown(
                    "<div class='gradient-card'><h4>🎓 Recommended Future Modules</h4></div>",
                    unsafe_allow_html=True,
                )
                for mod in future_modules:
                    title = mod.get("Module Title", "Module")
                    desc = mod.get("Description", "")
                    year = mod.get("Year", "")
                    justification = mod.get("Justification", "")
                    st.markdown(
                        f"<div class='course-card'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                        f"<strong>{title}</strong>"
                        f"<span style='opacity:0.8;font-size:0.85rem'>{year}</span></div>"
                        f"<p style='margin:0.4rem 0;font-size:0.88rem;opacity:0.9'>{justification}</p>"
                        f"<details><summary style='font-size:0.82rem;cursor:pointer;opacity:0.75'>"
                        f"Full description</summary>"
                        f"<p style='font-size:0.82rem;margin-top:0.4rem;opacity:0.85'>{desc}</p>"
                        f"</details></div>",
                        unsafe_allow_html=True,
                    )

            # ── Future Experiences ────────────────────────────────────────
            future_experiences = result.get("future_experiences", [])
            if future_experiences:
                st.markdown(
                    "<div class='gradient-card-blue'><h4>🚀 Recommended Future Experiences</h4></div>",
                    unsafe_allow_html=True,
                )
                fe_cols = st.columns(2)
                for i, exp in enumerate(future_experiences):
                    with fe_cols[i % 2]:
                        name = exp.get("Name of Experience", "Experience")
                        exp_type = exp.get("Type of Experience", "")
                        justification = exp.get("Justification", "")
                        desc = exp.get("Description", "")
                        # acad = exp.get("Academic", "")
                        st.markdown(
                            f"<div class='glass-card'>"
                            f"<strong>{name}</strong>"
                            f"<span style='background:#667eea;color:white;padding:2px 8px;"
                            f"border-radius:10px;font-size:0.75rem;margin-left:8px'>{exp_type}</span><br>"
                            f"<small style='color:#444'>{justification}</small><br><br>"
                            f"<small style='color:#666'>{desc[:200]}{'…' if len(desc) > 200 else ''}</small>"
                            # f"<small style='color:#666'>{acad[:200]}{'…' if len(acad) > 0 else ''}</small>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

            # ── Future Skills ─────────────────────────────────────────────
            future_skills = result.get("future_skills", [])
            if future_skills:
                st.markdown(
                    "<div class='gradient-card'><h4>📈 Skills to Develop</h4></div>",
                    unsafe_allow_html=True,
                )
                for skill in future_skills:
                    name = skill.get("Name of Skill", "Skill")
                    difficulty = int(skill.get("Difficulty", 0))
                    importance = int(skill.get("Importance", 0))
                    justification = skill.get("Justification", "")
                    resources = skill.get("Resources", "")
                    prereqs = skill.get("Prerequisites", [])
                    diff_color = ["#4caf50", "#8bc34a", "#ff9800", "#f44336", "#b71c1c"][
                        min(difficulty - 1, 4)
                    ] if difficulty else "#9e9e9e"
                    prereqs_html = (
                        f"<p style='font-size:0.82rem;color:#666'>Prerequisites: {', '.join(prereqs)}</p>"
                        if prereqs else ""
                    )
                    resources_html = (
                        f"<p style='font-size:0.82rem;color:#555'>Resources: {resources}</p>"
                        if resources else ""
                    )
                    st.markdown(
                        f"<div class='job-card medium-match'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                        f"<strong>{name}</strong>"
                        f"<span style='display:flex;gap:8px;align-items:center'>"
                        f"<span style='background:{diff_color};color:white;padding:2px 8px;"
                        f"border-radius:10px;font-size:0.8rem'>Difficulty {difficulty}/5</span>"
                        f"<span style='background:#667eea;color:white;padding:2px 8px;"
                        f"border-radius:10px;font-size:0.8rem'>Importance {importance}/5</span>"
                        f"</span></div>"
                        f"<p style='margin:0.4rem 0;font-size:0.88rem;color:#444'>{justification}</p>"
                        f"{prereqs_html}"
                        f"{resources_html}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            # ── Skills Tree — force-directed graph ────────────────────────
            skills_tree = result.get("skills_tree", [])
            if skills_tree:
                st.markdown(
                    "<div class='gradient-card-blue'><h4>🌳 Skills Roadmap</h4></div>",
                    unsafe_allow_html=True,
                )
                _render_skills_graph(skills_tree)
        # ══════════════════════════════════════════════════════════════════
        # TAB: JOB MATCH
        # ══════════════════════════════════════════════════════════════════
        with tab_jobs:
            st.markdown(
                "<div class='info-box'><strong>🎯 Job Match Analysis:</strong> "
                "See which sectors suit you best, how your CV compares to the "
                "general market, and optionally match against a specific posting.</div>",
                unsafe_allow_html=True,
            )

            cv_text_for_match = st.session_state.get("_cv_text")
            run_job_match = False

            if not cv_text_for_match:
                st.markdown(
                    "<div class='warning-box'><strong>📄 No CV uploaded yet.</strong><br>"
                    "Upload your CV using the file uploader above to enable job match analysis."
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.success(f"✅ Using uploaded CV ({len(cv_text_for_match):,} characters)")

                st.markdown("#### 📋 Specific Job Description (optional)")
                st.markdown(
                    "<small style='color:#666'>Paste a job posting you are targeting "
                    "for a tailored match score alongside the general analysis.</small>",
                    unsafe_allow_html=True,
                )
                specific_job_input = st.text_area(
                    "Job description:",
                    placeholder="Paste the full job description here including "
                                "responsibilities, required skills, and qualifications…",
                    height=180,
                    key="specific_job_input",
                    label_visibility="collapsed",
                )

                job_match_key = (
                    f"jobmatch|{st.session_state.get('_cv_file_key', 'nocv')}"
                    f"|{hash(specific_job_input)}"
                )
                run_job_match = st.button("🔍 Analyse Job Match", key="job_match_btn")

            if run_job_match:
                st.session_state["_job_match_key"]          = None
                st.session_state["_specific_job_match_key"] = None
                st.session_state["_sector_match_key"]       = None

            if run_job_match and cv_text_for_match:
                parsed_str = str(result) if result else None

                # ── Specific job agent (if description provided) ──────────
                specific_jm = None
                if specific_job_input.strip():
                    with st.spinner("🔍 Analysing match against specific job posting…"):
                        try:
                            specific_jm = query_specific_job_agent(
                                cv_text=cv_text_for_match,
                                job_description=specific_job_input.strip(),
                                parsed=parsed_str,
                            )
                            st.session_state["_specific_jm"]            = specific_jm
                            st.session_state["_specific_job_match_key"] = job_match_key
                        except Exception as e:
                            st.error(f"❌ Specific job match failed: {e}")
                            with st.expander("Debug"):
                                st.exception(e)

                # ── Sector agent ──────────────────────────────────────────
                sector_result = None
                with st.spinner("🏭 Identifying best-fit sectors…"):
                    try:
                        sector_result = query_sector_match_agent(
                            cv_text=cv_text_for_match,
                            parsed=parsed_str,
                        )
                        st.session_state["_sector_result"]    = sector_result
                        st.session_state["_sector_match_key"] = job_match_key
                    except Exception as e:
                        st.error(f"❌ Sector match failed: {e}")
                        with st.expander("Debug"):
                            st.exception(e)

                # ── General job match agent ───────────────────────────────
                jm = None
                with st.spinner("🔍 Analysing general market match…"):
                    try:
                        jm = query_job_match_agent(
                            user_query=final_query,
                            cv_text=cv_text_for_match,
                            parsed=parsed_str,
                        )
                        st.session_state["_job_match"]     = jm
                        st.session_state["_job_match_key"] = job_match_key
                    except Exception as e:
                        st.error(f"❌ General job match failed: {e}")
                        with st.expander("Debug"):
                            st.exception(e)

            else:
                # Restore from cache
                def _from_cache(result_key, cache_key):
                    cached = st.session_state.get(result_key)
                    return (
                        cached
                        if cv_text_for_match
                        and st.session_state.get(cache_key) == job_match_key
                        else None
                    )

                jm          = _from_cache("_job_match",    "_job_match_key")
                specific_jm = _from_cache("_specific_jm",  "_specific_job_match_key")
                sector_result = _from_cache("_sector_result", "_sector_match_key")

            # ── Render helper (shared by specific + general blocks) ───────
            def render_match_block(m: dict, heading: str) -> None:
                match_pct   = m["match_level"]
                top_flag    = m["top_applicant"]
                score_color = (
                    "#4caf50" if match_pct >= 80
                    else "#ff9800" if match_pct >= 55
                    else "#f44336"
                )
                score_label = (
                    "Strong match" if match_pct >= 80
                    else "Partial match" if match_pct >= 55
                    else "Developing match"
                )
                top_badge = (
                    "<span style='background:#4caf50;color:white;padding:4px 14px;"
                    "border-radius:20px;font-size:0.85rem;font-weight:600;"
                    "margin-left:12px'>⭐ Top Applicant</span>"
                    if top_flag else ""
                )

                st.markdown(f"### {heading}")
                st.markdown(
                    f"<div style='background:white;border-radius:1.2rem;padding:1.8rem;"
                    f"box-shadow:0 8px 32px rgba(0,0,0,0.08);margin:1rem 0;"
                    f"border-left:6px solid {score_color};display:flex;"
                    f"align-items:center;gap:1.5rem'>"
                    f"<div style='font-size:3.5rem;font-weight:700;"
                    f"color:{score_color};line-height:1'>{match_pct}%</div>"
                    f"<div>"
                    f"<div style='font-size:1.1rem;font-weight:600;color:#1e3c72'>"
                    f"{score_label}</div>"
                    f"<div style='color:#666;font-size:0.9rem;margin-top:4px'>"
                    f"{heading}{top_badge}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

                col_have, col_missing = st.columns(2)
                with col_have:
                    st.markdown(
                        "<div class='gradient-card-blue'><h4>✅ Skills You Have</h4></div>",
                        unsafe_allow_html=True,
                    )
                    for skill in m["required_skills_achieved"]:
                        st.markdown(
                            f"<div style='background:#e8f5e9;border-radius:8px;"
                            f"padding:0.5rem 0.9rem;margin:0.25rem 0;"
                            f"border-left:3px solid #4caf50;"
                            f"font-size:0.88rem;color:#1b5e20'>{skill}</div>",
                            unsafe_allow_html=True,
                        )
                with col_missing:
                    st.markdown(
                        "<div class='gradient-card'><h4>⚠️ Skills to Develop</h4></div>",
                        unsafe_allow_html=True,
                    )
                    for skill in m["absent_required_skills"]:
                        st.markdown(
                            f"<div style='background:#fff8e1;border-radius:8px;"
                            f"padding:0.5rem 0.9rem;margin:0.25rem 0;"
                            f"border-left:3px solid #ff9800;"
                            f"font-size:0.88rem;color:#e65100'>{skill}</div>",
                            unsafe_allow_html=True,
                        )

                if m["additional_skills_others"]:
                    st.markdown(
                        "<div class='gradient-card-blue'>"
                        "<h4>👥 Skills Other Applicants Have</h4></div>",
                        unsafe_allow_html=True,
                    )
                    comp_cols = st.columns(2)
                    for i, skill in enumerate(m["additional_skills_others"]):
                        with comp_cols[i % 2]:
                            st.markdown(
                                f"<div style='background:#f3e5f5;border-radius:8px;"
                                f"padding:0.5rem 0.9rem;margin:0.25rem 0;"
                                f"border-left:3px solid #9c27b0;"
                                f"font-size:0.88rem;color:#4a148c'>{skill}</div>",
                                unsafe_allow_html=True,
                            )

                if m["cv_tips"]:
                    st.markdown(
                        "<div class='gradient-card'><h4>✏️ CV Tips</h4></div>",
                        unsafe_allow_html=True,
                    )
                    for i, tip in enumerate(m["cv_tips"], 1):
                        st.markdown(
                            f"<div style='background:white;border-radius:8px;"
                            f"padding:0.7rem 1rem;margin:0.4rem 0;"
                            f"box-shadow:0 2px 8px rgba(0,0,0,0.06);"
                            f"border-left:4px solid #667eea;"
                            f"font-size:0.88rem;color:#333'>"
                            f"<span style='font-weight:600;color:#667eea'>{i}.</span> {tip}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                with st.expander("🔧 Debug: raw output"):
                    st.text_area("Raw", m.get("_raw", ""), height=120, key=f"debug_{heading[:8]}")
                    if m.get("_output_tokens"):
                        st.caption(f"Output tokens: {m['_output_tokens']}")

            # ── 1. Sector match (always shown first if available) ─────────
            if sector_result and sector_result.get("sectors"):
                st.markdown("### 🏭 Best-Fit Sectors")

                degree_colors = {
                    "High":   ("#4caf50", "#e8f5e9", "#1b5e20"),
                    "Medium": ("#ff9800", "#fff8e1", "#e65100"),
                    "Low":    ("#9e9e9e", "#f5f5f5", "#424242"),
                }
                degree_order = {"High": 0, "Medium": 1, "Low": 2}
                sectors_sorted = sorted(
                    sector_result["sectors"],
                    key=lambda x: degree_order.get(x.get("Degree", "Low"), 3),
                )

                # Display as a responsive grid of cards
                n = len(sectors_sorted)
                cols_per_row = min(n, 3)
                rows = [
                    sectors_sorted[i : i + cols_per_row]
                    for i in range(0, n, cols_per_row)
                ]
                for row in rows:
                    row_cols = st.columns(len(row))
                    for col, sector in zip(row_cols, row):
                        area   = sector.get("Area", "")
                        degree = sector.get("Degree", "")
                        border, bg, text = degree_colors.get(
                            degree, ("#9e9e9e", "#f5f5f5", "#424242")
                        )
                        with col:
                            st.markdown(
                                f"<div style='background:{bg};border-radius:1rem;"
                                f"padding:1.2rem 1rem;text-align:center;"
                                f"border-top:4px solid {border};margin:0.3rem 0'>"
                                f"<div style='font-size:1rem;font-weight:600;"
                                f"color:{text};margin-bottom:0.4rem'>{area}</div>"
                                f"<span style='background:{border};color:white;"
                                f"padding:3px 12px;border-radius:12px;"
                                f"font-size:0.78rem;font-weight:600'>{degree} match</span>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )

                st.markdown("<br>", unsafe_allow_html=True)

            # ── 2. Specific job match (if description was provided) ───────
            if specific_jm:
                st.markdown("<hr>", unsafe_allow_html=True)
                render_match_block(specific_jm, "🎯 Specific Job Match")

            # ── 3. General market match ───────────────────────────────────
            if jm:
                if specific_jm:
                    st.markdown("<hr>", unsafe_allow_html=True)
                render_match_block(jm, "🌐 General Market Match")

            if not jm and not specific_jm and not sector_result and cv_text_for_match:
                st.info("Click 'Analyse Job Match' to see your results.")
                # ══════════════════════════════════════════════════════════════════
        # TAB: INTERVIEW PREP
        # ══════════════════════════════════════════════════════════════════
        with tab_interview:
            from streamlit_mic_recorder import speech_to_text
            from tts_utils import text_to_speech_gtts

            st.markdown(
                "<h2 class='section-header'>🎤 Interview Prep</h2>",
                unsafe_allow_html=True,
            )

            # ── Privacy notices ───────────────────────────────────────────
            st.markdown(
                "<div class='info-box'>"
                "<strong>📷 Camera notice:</strong> Your camera feed is displayed "
                "locally in your browser only. No frames are captured, transmitted, "
                "or recorded at any point."
                "</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div class='warning-box'>"
                "<strong>🎙️ Audio notice:</strong> Speech is transcribed to text "
                "in your browser via the Web Speech API. The transcript is then "
                "processed by Azure AI Foundry agents in the same way as your CV "
                "and career aspirations. No raw audio is stored or transmitted."
                "</div>",
                unsafe_allow_html=True,
            )

            # ── Initialise session state ──────────────────────────────────
            for _k, _v in {
                "interview_started":  False,
                "interview_history":  [],
                "interview_type":     "",
                "interview_goal":     "",
                "tts_enabled":        True,
                "last_audio":         None,
            }.items():
                if _k not in st.session_state:
                    st.session_state[_k] = _v

            # ══════════════════════════════════════════════════════════════
            # PRE-SESSION SETUP
            # ══════════════════════════════════════════════════════════════
            if not st.session_state["interview_started"]:

                st.markdown("### ⚙️ Session Setup")

                iv_type_col, iv_tts_col = st.columns([2, 1])

                with iv_type_col:
                    iv_type = st.selectbox(
                        "Interview type:",
                        [
                            "Behavioural Interview",
                            "Technical Interview",
                            "CV Deep Dive",
                        ],
                        key="iv_type",
                    )

                with iv_tts_col:
                    st.markdown("<br>", unsafe_allow_html=True)
                    tts_toggle = st.toggle(
                        "🔊 Agent voice (TTS)",
                        value=True,
                        key="iv_tts_toggle",
                        help="When enabled, the interviewer's replies are read aloud using Azure Neural TTS.",
                    )
                    st.session_state["tts_enabled"] = tts_toggle

                # Career goal carried over from the main analysis
                iv_final_goal = final_query
                if iv_final_goal:
                    st.markdown(
                        f"<div class='info-box'>🎯 <strong>Career goal for this session:</strong> "
                        f"{iv_final_goal}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='warning-box'>⚠️ No career goal detected. "
                        "Please enter your goal in the Career Goal section above "
                        "before starting the interview.</div>",
                        unsafe_allow_html=True,
                    )

                cv_available = bool(st.session_state.get("_cv_text"))
                if not cv_available:
                    st.markdown(
                        "<div class='warning-box'>📄 No CV uploaded — upload your CV "
                        "above for a personalised CV Deep Dive or tailored questions."
                        "</div>",
                        unsafe_allow_html=True,
                    )

                # ── Camera preview ────────────────────────────────────────
                st.markdown("### 📷 Camera Preview")
                components.html("""
<style>
  #cam-wrap { position: relative; width: 100%; max-width: 1440px; }
  #cam {
    width: 100%; border-radius: 12px;
    background: #1a1a2e; display: none;
  }
  #cam-status {
    position: absolute; bottom: 10px; left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.55); color: white;
    font-size: 11px; padding: 3px 10px; border-radius: 20px;
    pointer-events: none; display: none;
  }
  #cam-toggle {
    padding: 7px 18px; border-radius: 20px; border: none;
    background: #667eea; color: white; font-size: 0.85rem;
    font-weight: 600; cursor: pointer; margin-bottom: 8px;
    transition: background 0.2s;
  }
  #cam-toggle.on { background: #f44336; }
  #cam-error { color: #999; font-size: 0.85rem; padding: 0.5rem 0; }
</style>
<button id="cam-toggle" onclick="toggleCam()">📷 Enable Camera</button>
<div id="cam-wrap">
  <video id="cam" autoplay playsinline muted></video>
  <div id="cam-status">🔴 Live — not recorded</div>
</div>
<p id="cam-error"></p>
<script>
  let camStream = null;
  async function toggleCam() {
    const btn    = document.getElementById("cam-toggle");
    const vid    = document.getElementById("cam");
    const status = document.getElementById("cam-status");
    const err    = document.getElementById("cam-error");
    if (camStream) {
      camStream.getTracks().forEach(t => t.stop());
      camStream = null;
      vid.srcObject = null;
      vid.style.display = "none";
      status.style.display = "none";
      btn.textContent = "📷 Enable Camera";
      btn.classList.remove("on");
      return;
    }
    try {
      camStream = await navigator.mediaDevices.getUserMedia(
        { video: true, audio: false }
      );
      vid.srcObject = camStream;
      vid.style.display = "block";
      status.style.display = "block";
      btn.textContent = "📷 Disable Camera";
      btn.classList.add("on");
      err.textContent = "";
    } catch(e) {
      err.textContent = "Camera unavailable: " + e.message;
    }
  }
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && camStream) {
      camStream.getTracks().forEach(t => t.stop());
      camStream = null;
      const vid = document.getElementById("cam");
      const btn = document.getElementById("cam-toggle");
      const status = document.getElementById("cam-status");
      if (vid)    { vid.srcObject = null; vid.style.display = "none"; }
      if (status) { status.style.display = "none"; }
      if (btn)    { btn.textContent = "📷 Enable Camera"; btn.classList.remove("on"); }
    }
  });
</script>
""", height=810)

                # ── Begin session button ──────────────────────────────────
                st.markdown("### 🚀 Start Session")
                st.markdown(
                    "Click **Begin Session** when you are ready. "
                    "The AI interviewer will introduce itself and then begin "
                    "asking questions. Respond by **speaking** (click the mic button) "
                    "or **typing** in the chat box."
                )

                if st.button(
                    "▶ Begin Session",
                    disabled=not bool(iv_final_goal),
                    key="iv_begin",
                ):
                    st.session_state["interview_started"] = True
                    st.session_state["interview_type"]    = iv_type
                    st.session_state["interview_goal"]    = iv_final_goal
                    st.session_state["interview_history"] = []
                    st.session_state["last_audio"]        = None

                    # Opening message to agent
                    opening = (
                        f"My career goal is: {iv_final_goal}. "
                        f"I would like to do a {iv_type}."
                    )
                    if cv_available:
                        opening += " I have uploaded my CV for your reference."

                    st.session_state["interview_history"].append(
                        {"role": "user", "content": opening}
                    )

                    with st.spinner("Starting session…"):
                        try:
                            r = query_interview_agent(
                                conversation=st.session_state["interview_history"],
                                cv_text=st.session_state.get("_cv_text"),
                                career_goal=iv_final_goal,
                            )
                            reply = r["reply"]
                            st.session_state["interview_history"].append(
                                {"role": "assistant", "content": reply}
                            )
                            # Generate opening TTS if enabled
                            if st.session_state["tts_enabled"]:
                                try:
                                    st.session_state["last_audio"] = text_to_speech_gtts(reply)
                                    audio_bytes = st.session_state["last_audio"]
                                    st.audio(audio_bytes, format = "audio/mp3",autoplay = True)
                                except Exception as tts_err:
                                    st.warning(f"TTS unavailable: {tts_err}")
                        except Exception as e:
                            st.error(f"❌ Could not start session: {e}")
                            st.session_state["interview_started"] = False
                    st.rerun()

            # ══════════════════════════════════════════════════════════════
            # ACTIVE INTERVIEW SESSION
            # ══════════════════════════════════════════════════════════════
            else:
                from streamlit_mic_recorder import speech_to_text
                from tts_utils import text_to_speech_gtts

                goal_disp = st.session_state["interview_goal"]
                type_disp = st.session_state["interview_type"]

                # ── Session metadata strip ────────────────────────────────
                col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
                with col_meta1:
                    st.markdown(
                        f"<div class='metric-container'>"
                        f"<div class='metric-value'>🎯</div>"
                        f"<div class='metric-label'>"
                        f"{goal_disp[:28]}{'…' if len(goal_disp) > 28 else ''}"
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )
                with col_meta2:
                    st.markdown(
                        f"<div class='metric-container'>"
                        f"<div class='metric-value'>📋</div>"
                        f"<div class='metric-label'>{type_disp}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_meta3:
                    q_count = sum(
                        1 for m in st.session_state["interview_history"]
                        if m["role"] == "user"
                    )
                    st.markdown(
                        f"<div class='metric-container'>"
                        f"<div class='metric-value'>{q_count}</div>"
                        f"<div class='metric-label'>Responses given</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_meta4:
                    tts_status = "🔊 On" if st.session_state["tts_enabled"] else "🔇 Off"
                    st.markdown(
                        f"<div class='metric-container'>"
                        f"<div class='metric-value'>{tts_status}</div>"
                        f"<div class='metric-label'>Agent voice</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── TTS playback for latest agent reply ───────────────────
                if st.session_state.get("last_audio"):
                    st.audio(
                        st.session_state["last_audio"],
                        format="audio/wav",
                        autoplay=True,
                    )

                # ── Camera toggle (compact, in-session) ───────────────────
                components.html("""
<style>
  #cam-section { display:flex; align-items:flex-start; gap:12px; margin:8px 0; }
  #cam { width:1440px; border-radius:10px; background:#1a1a2e; display:none; }
  #cam-controls { display:flex; flex-direction:column; gap:6px; }
  #cam-toggle {
    padding:6px 16px; border-radius:16px; border:none;
    background:#667eea; color:white; font-size:0.82rem;
    font-weight:600; cursor:pointer;
  }
  #cam-toggle.on { background:#f44336; }
  #cam-status { font-size:0.75rem; color:#999; }
</style>
<div id="cam-section">
  <video id="cam" autoplay playsinline muted></video>
  <div id="cam-controls">
    <button id="cam-toggle" onclick="toggleCam()">📷 Enable Camera</button>
    <div id="cam-status">Camera off — not recorded</div>
  </div>
</div>
<script>
  let stream = null;
  async function toggleCam() {
    const btn    = document.getElementById("cam-toggle");
    const vid    = document.getElementById("cam");
    const status = document.getElementById("cam-status");
    if (stream) {
      stream.getTracks().forEach(t => t.stop()); stream = null;
      vid.srcObject = null; vid.style.display = "none";
      btn.textContent = "📷 Enable Camera"; btn.classList.remove("on");
      status.textContent = "Camera off";
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video:true, audio:false });
      vid.srcObject = stream; vid.style.display = "block";
      btn.textContent = "📷 Disable Camera"; btn.classList.add("on");
      status.textContent = "🔴 Live — not recorded";
    } catch(e) { status.textContent = "Camera unavailable: " + e.message; }
  }
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && stream) {
      stream.getTracks().forEach(t => t.stop()); stream = null;
      const vid = document.getElementById("cam");
      const btn = document.getElementById("cam-toggle");
      if (vid) { vid.srcObject = null; vid.style.display = "none"; }
      if (btn) { btn.textContent = "📷 Enable Camera"; btn.classList.remove("on"); }
    }
  });
</script>
""", height=810)
                # ── Input: Speech-to-Text ─────────────────────────────────
                st.markdown("#### 🎙️ Your Response")
                st.markdown(
                    "<small style='color:#666'>Click the microphone to speak, "
                    "or type your answer in the box below. "
                    "Both inputs are treated identically.</small>",
                    unsafe_allow_html=True,
                )

                # STT via streamlit-mic-recorder
                voice_transcript = speech_to_text(
                    language="en",
                    start_prompt="🎙️ Click to speak",
                    stop_prompt="⏹ Stop recording",
                    just_once=True,
                    use_container_width=False,
                    key="iv_stt",
                )

                # Text fallback
                typed_response = st.chat_input(
                    "Or type your answer here…",
                    key="iv_chat_input",
                )

                # Determine which input to use (voice takes priority)
                user_input = None
                if voice_transcript and voice_transcript.strip():
                    user_input = voice_transcript.strip()
                    st.markdown(
                        f"<div class='success-box'>"
                        f"🎙️ <strong>Transcribed:</strong> {user_input}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                elif typed_response and typed_response.strip():
                    user_input = typed_response.strip()

                # ── Process user input → agent → TTS ─────────────────────
                if user_input:
                    st.session_state["interview_history"].append(
                        {"role": "user", "content": user_input}
                    )
                    st.session_state["last_audio"] = None  # clear old audio

                    with st.spinner("🤖 Interviewer is thinking…"):
                        try:
                            r = query_interview_agent(
                                conversation=st.session_state["interview_history"],
                                cv_text=st.session_state.get("_cv_text"),
                                career_goal=st.session_state["interview_goal"],
                            )
                            reply = r["reply"]
                            st.session_state["interview_history"].append(
                                {"role": "assistant", "content": reply}
                            )

                            # TTS — convert reply to audio
                            if st.session_state["tts_enabled"]:
                                with st.spinner("🔊 Generating audio…"):
                                    try:
                                        st.session_state["last_audio"] = (
                                            text_to_speech_gtts(reply)
                                        )
                                    except Exception as tts_err:
                                        st.warning(
                                            f"⚠️ TTS failed (text response still shown): "
                                            f"{tts_err}"
                                        )

                        except Exception as e:
                            st.error(f"❌ Agent error: {e}")
                            with st.expander("Debug"):
                                st.exception(e)

                    st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Conversation history ───────────────────────────────────

                st.markdown("#### 💬 Interview Conversation")

                # Filter out the silent opening context message
                display_history = [
                    m for m in st.session_state["interview_history"]
                    if not (
                        m["role"] == "user"
                        and m["content"].startswith("My career goal is:")
                    )
                ]

                if not display_history:
                    st.info("The conversation will appear here as you speak or type.")

                for msg in display_history:
                    is_agent = msg["role"] == "assistant"
                    label    = "🤖 Interviewer" if is_agent else "🎓 You"
                    bg       = "#f0f2fa" if is_agent else "#e8f5e9"
                    border   = "#667eea" if is_agent else "#4caf50"
                    st.markdown(
                        f"<div style='background:{bg};border-left:4px solid {border};"
                        f"border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin:0.4rem 0'>"
                        f"<strong style='font-size:0.8rem;color:#666'>{label}</strong><br>"
                        f"<span style='font-size:0.9rem;color:#333;"
                        f"white-space:pre-wrap'>{msg['content']}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── TTS toggle mid-session ────────────────────────────────
                with st.expander("⚙️ Session settings"):
                    new_tts = st.toggle(
                        "🔊 Agent voice (TTS)",
                        value=st.session_state["tts_enabled"],
                        key="iv_tts_mid",
                        help="Toggle agent voice on or off mid-session.",
                    )
                    if new_tts != st.session_state["tts_enabled"]:
                        st.session_state["tts_enabled"] = new_tts
                        st.rerun()

                # ── Actions row ───────────────────────────────────────────
                st.markdown("---")
                act_col1, act_col2 = st.columns(2)

                with act_col1:
                    # PDF transcript download
                    if len(display_history) > 0:
                        try:
                            pdf_bytes = generate_interview_pdf(
                                conversation=display_history,
                                career_goal=st.session_state["interview_goal"],
                                interview_type=st.session_state["interview_type"],
                            )
                            st.download_button(
                                label="📄 Download Transcript (PDF)",
                                data=pdf_bytes,
                                file_name="interview_transcript.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        except Exception as e:
                            st.warning(f"PDF generation unavailable: {e}")
                    else:
                        st.button(
                            "📄 Download Transcript (PDF)",
                            disabled=True,
                            use_container_width=True,
                            help="Complete at least one exchange to download the transcript.",
                        )

                with act_col2:
                    if st.button(
                        "🔄 Start New Session",
                        key="iv_reset",
                        use_container_width=True,
                    ):
                        for k in [
                            "interview_started", "interview_history",
                            "interview_type", "interview_goal",
                            "last_audio",
                        ]:
                            st.session_state.pop(k, None)
                        st.rerun()
    # Debug expander
    with st.expander("🔧 Debug: raw agent output"):
        st.text_area("Raw response", result.get("_raw", ""), height=200)
        if result.get("_output_tokens"):
            st.caption(f"Output tokens: {result['_output_tokens']}")

# Footer
st.markdown("""<div class='footer'><h3>🎓 EEE Career Pathways Platform</h3><p>Imperial College London & NTU Singapore • 2026</p></div>""", unsafe_allow_html=True)
