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

# ========== Tabs ==========
tab1, tab2, tab5 = st.tabs(["🔍 Explore Jobs", "📄 CV Analysis", "📊 Power BI"])

# ==================== TAB 1: Explore Jobs ====================
with tab1:
    st.markdown("<h2 class='section-header'>🔍 Explore Career Opportunities</h2>", unsafe_allow_html=True)
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
                                        format_func=str.title)

        if selected_job:
            m1, m2, m3, m4 = st.columns(4)
            for col, (icon, label) in zip([m1, m2, m3, m4], [
                ("🏢", selected_sector.title()[:15]),
                ("💼", selected_job.title()[:15]),
                ("📍", "General"),
                ("⭐", "Featured")
            ]):
                with col:
                    st.markdown(f"<div class='metric-container'><div class='metric-value'>{icon}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns([3, 2])

            with col_a:
                st.markdown("<div class='glass-card'><h4>📖 Job Description</h4></div>", unsafe_allow_html=True)
                job_desc = platform.get_job_description(selected_sector, selected_job) or ""
                st.write(job_desc if job_desc else "No description available.")

                st.markdown("<div class='gradient-card'><h4>🛠️ Skills Summary</h4></div>", unsafe_allow_html=True)
                tsc_skills = platform.get_raw_tsc_skills(selected_sector, selected_job)
                if tsc_skills:
                    with st.expander("View detailed skills"):
                        for s in tsc_skills:
                            st.markdown(f"**{s['skill']}** — Level {s['level']}")
                            if s['description']:
                                st.caption(s['description'])
                    with st.spinner("Generating AI summary…"):
                        try:
                            summary = platform.get_tsc_summary(selected_sector, selected_job)
                            st.info(summary)
                        except Exception as e:
                            st.warning(f"AI summary unavailable: {e}")
                else:
                    st.info("No technical skills data available for this role.")

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
    st.markdown("<div class='success-box'><strong>✅ Backend Connected:</strong> Using backend_api.py — spaCy N-gram skill extraction + TF-IDF job matching</div>", unsafe_allow_html=True)

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
                    matches = platform.find_matching_jobs(detected_skills, top_n=5)
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
        st.caption(f"📄 {len(cv_text):,} characters extracted")

        with st.expander("🔍 Debug: View extracted text"):
            st.text_area("First 2000 chars", cv_text[:2000], height=150)

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
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                if soft_skills_found:
                    st.caption("Detected: " + ", ".join(s.title() for s in soft_skills_found))
                else:
                    st.caption("No soft skills detected in this CV.")
        else:
            st.warning("⚠️ No technical skills detected.")

        # --- Job Matches ---
        st.markdown("<h3 class='section-header'>💼 Top Job Matches</h3>", unsafe_allow_html=True)
        if detected_skills:

            strong_jobs = strong + good   # labelled "Strong"
            possible_jobs = weak          # labelled "Possible"

            if not strong_jobs and not possible_jobs:
                st.info("No matches found. Upload a CV with more technical content.")
            else:
                def _render_match(idx, job, label, match_class, badge_class):
                    sim_pct = job.get('score', 0) * 100
                    st.markdown(f"""
                    <div class='job-card {match_class}'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <div>
                                <h4 style='margin:0;'>{idx}. {str(job.get('position','Unknown')).title()}</h4>
                                <p style='margin:0.5rem 0;color:#666;'>🏢 {job.get('employer','N/A')} | 🏷️ {str(job.get('industry','N/A'))[:30]}</p>
                            </div>
                            <div class='similarity-badge {badge_class}'>{label} ({sim_pct:.0f}%)</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                if strong_jobs:
                    st.markdown("#### 🟢 Strong")
                    for i, job in enumerate(strong_jobs, 1):
                        _render_match(i, job, "Strong", "high-match", "similarity-high")

                if possible_jobs:
                    st.markdown("#### 🟡 Possible")
                    for i, job in enumerate(possible_jobs, 1):
                        _render_match(i, job, "Possible", "medium-match", "similarity-medium")
        else:
            st.info("No job matches found. Upload a CV with more technical content.")

# ==================== TAB 5: Power BI ====================
with tab5:
    st.markdown("<h2 class='section-header'>📊 Power BI Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<div class='info-box'><strong>💡 Interactive Dashboard:</strong> Click segments to drill down!</div>", unsafe_allow_html=True)
    powerbi_html = """<iframe title="Power BI" width="100%" height="650" src="https://app.powerbi.com/view?r=eyJrIjoiN2U5ZGU3NWYtMDAxZC00ZjJkLWI4ZmEtYTllOGYxNjIyMDNkIiwidCI6IjFmOWEwZDIyLTY0YWMtNDkwMS04NWJiLTI3YThhODAyNDUzZiIsImMiOjEwfQ%3D%3D" frameborder="0" allowFullScreen="true" style="border-radius: 1rem;"></iframe>"""
    components.html(powerbi_html, height=670)

# Footer
st.markdown("""<div class='footer'><h3>🎓 EEE Career Pathways Platform</h3><p>NTU Singapore • 2026</p></div>""", unsafe_allow_html=True)
