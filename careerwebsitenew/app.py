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
from agent_api import query_agent, query_job_match_agent

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
section[data-testid="stSidebar"] {display: none;}

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
</style>
""", unsafe_allow_html=True)

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

def detect_soft_skills_from_text(cv_text: str) -> list:
    """Scan raw CV text for soft skill indicators using broad keyword matching."""
    text_lower = cv_text.lower()
    found = []
    for dim, keywords in SOFT_SKILL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(dim)
    return found


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
from agent_api import query_agent  # lazy import keeps startup fast

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
        tab_profile, tab_roadmap, tab_jobs = st.tabs([
            "👤 My Profile", "🗺️ My Roadmap", "🎯 Job Match"
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
            from agent_api import query_job_match_agent

            st.markdown(
                "<div class='info-box'><strong>🎯 Job Match Analysis:</strong> "
                "See how your CV compares against target roles and get specific "
                "tips to improve your application.</div>",
                unsafe_allow_html=True,
            )

            # Read CV from session state — same upload as My Profile tab
            cv_text_for_match = st.session_state.get("_cv_text")

            if not cv_text_for_match:
                # No CV yet — prompt the user to go upload one
                st.markdown(
                    "<div class='warning-box'>"
                    "<strong>📄 No CV uploaded yet.</strong><br>"
                    "Upload your CV using the file uploader above to enable "
                    "job match analysis."
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.success(
                    f"✅ Using uploaded CV "
                    f"({len(cv_text_for_match):,} characters)"
                )

                job_match_key = f"jobmatch|{st.session_state.get('_cv_file_key', 'nocv')}"

                run_job_match = st.button(
                    "🔍 Analyse Job Match",
                    key="job_match_btn",
                )

            if run_job_match:
                st.session_state["_job_match_key"] = None  # force re-run

            if run_job_match and cv_text:
                with st.spinner("🔍 Matching your CV against target roles…"):
                    try:
                        jm = query_job_match_agent(
                            user_query=final_query, cv_text=cv_text
                        )
                        st.session_state["_job_match"]     = jm
                        st.session_state["_job_match_key"] = job_match_key
                    except Exception as e:
                        st.error(f"❌ Job match agent failed: {e}")
                        with st.expander("Debug info"):
                            st.exception(e)
                        jm = None
            else:
                cached_jm = st.session_state.get("_job_match")
                jm = (
                    cached_jm
                    if st.session_state.get("_job_match_key") == job_match_key
                    else None
                )

            if jm:

                # ── Match score hero ──────────────────────────────────────
                match_pct = jm["match_level"]
                top_flag  = jm["top_applicant"]

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

                st.markdown(
                    f"<div style='background:white;border-radius:1.2rem;padding:1.8rem;"
                    f"box-shadow:0 8px 32px rgba(0,0,0,0.08);margin:1rem 0;"
                    f"border-left:6px solid {score_color};display:flex;"
                    f"align-items:center;gap:1.5rem'>"
                    f"<div style='font-size:3.5rem;font-weight:700;color:{score_color};line-height:1'>"
                    f"{match_pct}%</div>"
                    f"<div>"
                    f"<div style='font-size:1.1rem;font-weight:600;color:#1e3c72'>{score_label}</div>"
                    f"<div style='color:#666;font-size:0.9rem;margin-top:4px'>"
                    f"Match against target role{top_badge}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

                # ── Two-column skill breakdown ─────────────────────────────
                col_have, col_missing = st.columns(2)

                with col_have:
                    st.markdown(
                        "<div class='gradient-card-blue'><h4>✅ Skills You Have</h4></div>",
                        unsafe_allow_html=True,
                    )
                    for skill in jm["required_skills_achieved"]:
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
                    for skill in jm["absent_required_skills"]:
                        st.markdown(
                            f"<div style='background:#fff8e1;border-radius:8px;"
                            f"padding:0.5rem 0.9rem;margin:0.25rem 0;"
                            f"border-left:3px solid #ff9800;"
                            f"font-size:0.88rem;color:#e65100'>{skill}</div>",
                            unsafe_allow_html=True,
                        )

                # ── Competitor skills ─────────────────────────────────────
                if jm["additional_skills_others"]:
                    st.markdown(
                        "<div class='gradient-card-blue'>"
                        "<h4>👥 Skills Other Applicants Have</h4></div>",
                        unsafe_allow_html=True,
                    )
                    comp_cols = st.columns(2)
                    for i, skill in enumerate(jm["additional_skills_others"]):
                        with comp_cols[i % 2]:
                            st.markdown(
                                f"<div style='background:#f3e5f5;border-radius:8px;"
                                f"padding:0.5rem 0.9rem;margin:0.25rem 0;"
                                f"border-left:3px solid #9c27b0;"
                                f"font-size:0.88rem;color:#4a148c'>{skill}</div>",
                                unsafe_allow_html=True,
                            )

                # ── CV tips ───────────────────────────────────────────────
                if jm["cv_tips"]:
                    st.markdown(
                        "<div class='gradient-card'><h4>✏️ CV Tips</h4></div>",
                        unsafe_allow_html=True,
                    )
                    for i, tip in enumerate(jm["cv_tips"], 1):
                        st.markdown(
                            f"<div style='background:white;border-radius:8px;"
                            f"padding:0.7rem 1rem;margin:0.4rem 0;"
                            f"box-shadow:0 2px 8px rgba(0,0,0,0.06);"
                            f"border-left:4px solid #667eea;font-size:0.88rem;color:#333'>"
                            f"<span style='font-weight:600;color:#667eea'>{i}.</span> {tip}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                # Debug
                with st.expander("🔧 Debug: raw job match output"):
                    st.text_area("Raw response", jm.get("_raw", ""), height=150)
                    if jm.get("_output_tokens"):
                        st.caption(f"Output tokens: {jm['_output_tokens']}")

            elif not cv_text:
                st.info("Upload a CV above to enable job match analysis.")

    # Debug expander
    with st.expander("🔧 Debug: raw agent output"):
        st.text_area("Raw response", result.get("_raw", ""), height=200)
        if result.get("_output_tokens"):
            st.caption(f"Output tokens: {result['_output_tokens']}")

# Footer
st.markdown("""<div class='footer'><h3>🎓 EEE Career Pathways Platform</h3><p>Imperial College London & NTU Singapore • 2026</p></div>""", unsafe_allow_html=True)
