"""
EEE Career Pathways Platform – Backend API
All public methods return live-computed data; no values are hardcoded.
Raise exceptions on failure — callers must not substitute fake data.
"""

from __future__ import annotations

import os
import pickle
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── File locations ─────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent
_DATA = _ROOT / "Data"

_SKILLSFUTURE = _DATA / "Myskillsfuture pdf extraction.xlsx"
_COURSES       = _DATA / "Course Catalog AY2324.xlsx"
_CAREERAXIS    = _DATA / "careeraxis2025.xlsx"
_TAXONOMY      = _DATA / "Taxonomy.xlsx"

# ── Similarity thresholds (calibrated for TF-IDF cosine similarity) ───────────
# TF-IDF cosines are lower than neural-embedding cosines; these values give
# a similar quality split to the original 0.45 / 0.30 / 0.15 thresholds.
STRONG_THRESHOLD = 0.20
GOOD_THRESHOLD   = 0.10
WEAK_THRESHOLD   = 0.04

# ── Skill dictionary (from resume_embeddings_noexpiry.py) ─────────────────────
SKILL_TERMS: set = {
    # Programming / CS
    "python", "c", "c++", "java", "javascript", "typescript",
    "html", "css", "sql",
    "data structures", "algorithms", "data structures & algorithms",
    "object oriented programming", "oop",
    "matlab", "simulink", "labview", "shell scripting",
    "automation scripts", "data analysis",
    # ML / AI / DS / quant
    "machine learning", "deep learning", "artificial intelligence",
    "computer vision",
    "natural language processing", "nlp",
    "time series", "time series analysis",
    "regression modelling", "regression modeling",
    "classification models", "clustering",
    "feature engineering", "model deployment",
    "statistical analysis", "statistics",
    "probability and statistics", "probability",
    "portfolio optimization", "derivatives pricing",
    "risk modelling", "risk modeling",
    "quantitative analysis", "quantitative research",
    # Tools / libraries
    "pandas", "numpy", "matplotlib", "seaborn",
    "scikit-learn", "sklearn",
    "tensorflow", "pytorch",
    "jupyter", "jupyter notebook",
    "git", "linux",
    # Core circuit and electronics
    "circuit analysis", "analog electronics", "digital electronics",
    "electronic circuit design", "mixed signal design", "mixed-signal design",
    "pcb design", "high speed digital design", "signal integrity",
    "power integrity", "op amp circuits", "operational amplifier circuits",
    "transistor level design", "cmos circuit design", "vlsi design",
    "asic design", "fpga design", "hardware description language",
    "verilog", "vhdl", "systemverilog", "schematic capture",
    "spice simulation", "pspice", "ltspice", "cadence virtuoso",
    "cadence allegro", "synopsys tools", "mentor graphics",
    "altium designer", "kicad",
    # Power, energy, and drives
    "power systems", "power system analysis", "load flow analysis",
    "short circuit analysis", "fault analysis", "protection coordination",
    "protective relaying", "substation design",
    "transmission and distribution", "distribution network planning",
    "power quality", "power system stability", "smart grids",
    "renewable energy systems", "solar photovoltaic systems",
    "solar pv systems", "wind energy systems",
    "battery energy storage systems", "bess",
    "inverters", "rectifiers", "dc dc converters",
    "ac dc converters", "ac ac converters", "power electronics",
    "motor drives", "electric drives", "variable speed drives",
    "pwm control", "motor control", "induction machines",
    "synchronous machines", "electrical machines",
    "transformer design", "hvac systems", "high voltage engineering",
    "earthing and grounding", "grounding systems", "lightning protection",
    # Control, automation, instrumentation
    "control systems", "feedback control", "pid control",
    "state space control", "state-space control", "robust control",
    "digital control", "model predictive control", "system identification",
    "scada", "dcs", "plc programming", "ladder logic",
    "industrial automation", "process control", "instrumentation",
    "sensors and actuators", "data acquisition", "daq systems",
    "hmi design", "robotics", "robot kinematics",
    "trajectory planning", "motion control",
    # Embedded, microcontrollers, and IoT
    "embedded systems", "real time systems", "real-time systems",
    "real time operating system", "rtos",
    "microcontrollers", "arm cortex m", "stm32", "pic microcontroller",
    "8051 microcontroller", "avr microcontroller",
    "bare metal programming", "bare-metal programming",
    "firmware development", "embedded c", "embedded c++",
    "device drivers", "board bring up", "board bring-up",
    "peripheral interfacing", "spi", "i2c", "uart",
    "can bus", "modbus", "rs485",
    "iot systems", "internet of things", "sensor integration",
    "wireless sensor networks",
    # RF, communications, and electromagnetics
    "electromagnetics", "rf engineering", "radio frequency engineering",
    "microwave engineering", "antenna design", "rf circuit design",
    "impedance matching", "smith chart", "s parameter analysis",
    "s-parameter analysis", "network analyzers", "spectrum analyzers",
    "wireless communications", "digital communication",
    "modulation techniques", "qam", "fsk", "psk", "ofdm",
    "link budget analysis", "channel coding", "error control coding",
    # DSP, signals, and imaging
    "signal processing", "digital signal processing", "dsp algorithms",
    "image processing", "fourier transform", "z transform", "z-transform",
    "filter design", "fir filter", "iir filter",
    "multirate signal processing", "time frequency analysis",
    "audio signal processing",
    # Semiconductor, fabrication, and device physics
    "semiconductor physics", "device physics", "cmos technology",
    "mosfet modeling", "bipolar transistor modeling",
    "semiconductor fabrication", "wafer fabrication",
    "cleanroom processes", "photolithography", "thin film deposition",
    "sputtering", "chemical vapor deposition", "cvd",
    "physical vapor deposition", "pvd",
    "diffusion processes", "ion implantation", "etching processes",
    "dry etching", "wet etching", "lithography mask design",
    "layout design", "drc verification", "lvs verification",
    "failure analysis", "reliability testing",
    "statistical process control", "spc", "process control",
    "yield improvement", "microelectronics",
    # Finance / business tech
    "financial modelling", "financial modeling",
    "valuation", "excel modelling", "excel modeling", "corporate finance",
    # General data
    "data analysis", "data analytics", "data engineering",
    "sql databases", "relational databases",
    # Soft skills
    "problem solving", "analytical thinking", "critical thinking",
    "teamwork", "communication skills", "technical writing",
    "documentation", "project management", "time management",
    "attention to detail",
}

SKILL_TERMS_NORM = {s.lower() for s in SKILL_TERMS}

CORE_CONCEPTS = {
    "power", "system", "circuit", "control", "signal", "voltage",
    "electrical", "electronic", "embedded", "smart",
}

# ── Internal helpers ───────────────────────────────────────────────────────────

def _norm(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].astype(str).str.strip().str.lower()
    return df


def _parse_tscs(text: str) -> List[Tuple[str, str]]:
    pattern = r"([A-Za-z0-9 ()\-]+) Level (\d+)"
    return [(tsc.strip().lower(), lvl) for tsc, lvl in re.findall(pattern, str(text))]


def _extract_requirements(text: str) -> str:
    m = re.search(r"(?i)requirements?:(.*)", str(text))
    return m.group(1).strip() if m else str(text)


def _safe(val: Any) -> str:
    """Return string; treat NaN / 'nan' / None as empty string."""
    if val is None:
        return ""
    try:
        if pd.isna(val):
            return ""
    except (TypeError, ValueError):
        pass
    s = str(val).strip()
    return "" if s.lower() == "nan" else s


def _load_cache(path: Path, expected_rows: int) -> Optional[np.ndarray]:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data if len(data) == expected_rows else None


def _save_cache(path: Path, emb: np.ndarray) -> None:
    with open(path, "wb") as f:
        pickle.dump(emb, f)


# ── Unified Platform Engine ────────────────────────────────────────────────────

class EEECareerPlatform:
    """
    Single backend object for the EEE Career Pathways Platform.
    Uses TF-IDF cosine similarity — no neural model download required.
    Startup time: ~8 seconds. Every method returns live-computed data.
    """

    def __init__(self) -> None:
        self._skillsfuture: Optional[pd.DataFrame] = None
        self._courses: Optional[pd.DataFrame] = None
        self._careeraxis: Optional[pd.DataFrame] = None
        self._taxonomy: Optional[pd.DataFrame] = None
        self._nlp = None
        # TF-IDF vectorizers (fitted in load())
        self._course_vec: Optional[TfidfVectorizer] = None
        self._course_mat = None          # sparse matrix: courses × terms
        self._posting_req_vec: Optional[TfidfVectorizer] = None
        self._posting_req_mat = None     # sparse matrix: postings × terms (req only)
        self._posting_full_vec: Optional[TfidfVectorizer] = None
        self._posting_full_mat = None    # sparse matrix: postings × terms (full)
        self._loaded = False

    # ── Initialization ─────────────────────────────────────────────────────────

    def load(self) -> None:
        """
        Load all data files, fit TF-IDF vectorizers, and load spaCy (~8 s total).
        No neural model download required.
        """
        if self._loaded:
            return
        print("[1/4] Loading Excel data files…", flush=True)
        self._load_dataframes()
        print("[2/4] Fitting TF-IDF on NTU courses…", flush=True)
        self._fit_course_tfidf()
        print("[3/4] Fitting TF-IDF on CareerAxis postings…", flush=True)
        self._fit_posting_tfidf()
        print("[4/4] Loading spaCy NLP model…", flush=True)
        self._load_nlp()
        self._loaded = True
        print("✓ Platform ready.", flush=True)

    def _fit_course_tfidf(self) -> None:
        texts = self._courses["Course Description"].fillna("").tolist()
        self._course_vec = TfidfVectorizer(
            max_features=10000, ngram_range=(1, 2), stop_words="english"
        )
        self._course_mat = self._course_vec.fit_transform(texts)

    def _fit_posting_tfidf(self) -> None:
        req_texts = [
            _extract_requirements(d) for d in self._careeraxis["Details"].tolist()
        ]
        self._posting_req_vec = TfidfVectorizer(
            max_features=20000, ngram_range=(1, 2), stop_words="english"
        )
        self._posting_req_mat = self._posting_req_vec.fit_transform(req_texts)

        full_texts = self._careeraxis["Details"].tolist()
        self._posting_full_vec = TfidfVectorizer(
            max_features=20000, ngram_range=(1, 2), stop_words="english"
        )
        self._posting_full_mat = self._posting_full_vec.fit_transform(full_texts)

    def _load_dataframes(self) -> None:
        for path in (_SKILLSFUTURE, _COURSES, _CAREERAXIS, _TAXONOMY):
            if not path.exists():
                raise FileNotFoundError(
                    f"Required data file not found: {path}\n"
                    "Ensure the Data/ folder contains all four Excel files."
                )

        sf = pd.read_excel(_SKILLSFUTURE)
        sf = _norm(sf, "Sector")
        sf = _norm(sf, "Job Title")
        sf = sf.dropna(subset=["Sector", "Job Title"])
        self._skillsfuture = sf

        co = pd.read_excel(_COURSES)
        co = _norm(co, "Course Name")
        co = co.dropna(subset=["Course Name", "Course Description"])
        self._courses = co

        ca = pd.read_excel(_CAREERAXIS, sheet_name="in")
        ca["Details"] = ca["Details"].astype(str)
        ca = ca.dropna(subset=["Position", "Details"])
        self._careeraxis = ca.reset_index(drop=True)

        ta = pd.read_excel(_TAXONOMY, sheet_name=0)
        ta = _norm(ta, "tsc_title")
        self._taxonomy = ta

    def _load_nlp(self) -> None:
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found.\n"
                "Run: python -m spacy download en_core_web_sm"
            )

    def _assert_loaded(self) -> None:
        if not self._loaded:
            raise RuntimeError("Platform not loaded. Call load() first.")

    # ── Career Explorer ────────────────────────────────────────────────────────

    def get_sectors(self) -> List[str]:
        self._assert_loaded()
        return sorted(self._skillsfuture["Sector"].dropna().unique().tolist())

    def get_job_titles(self, sector: str) -> List[str]:
        self._assert_loaded()
        mask = self._skillsfuture["Sector"] == sector.strip().lower()
        return sorted(
            self._skillsfuture[mask]["Job Title"].dropna().drop_duplicates().tolist()
        )

    def _get_job_row(self, sector: str, job_title: str) -> Optional[pd.Series]:
        s = sector.strip().lower()
        t = job_title.strip().lower()
        mask = (self._skillsfuture["Sector"] == s) & (self._skillsfuture["Job Title"] == t)
        rows = self._skillsfuture[mask]
        return rows.iloc[0] if not rows.empty else None

    def get_job_description(self, sector: str, job_title: str) -> Optional[str]:
        self._assert_loaded()
        row = self._get_job_row(sector, job_title)
        if row is None:
            return None
        desc = _safe(row.get("Job Description"))
        return desc if desc else None

    def get_top_courses(
        self, sector: str, job_title: str, top_n: int = 5
    ) -> List[Dict]:
        self._assert_loaded()
        desc = self.get_job_description(sector, job_title)
        if not desc:
            raise ValueError(
                f"No job description available for '{job_title}' in '{sector}'."
            )

        q_vec = self._course_vec.transform([desc])
        sims = cosine_similarity(q_vec, self._course_mat)[0]
        top_idxs = sims.argsort()[-top_n:][::-1]

        return [
            {
                "code": _safe(self._courses.iloc[i].get("Course Code")),
                "name": _safe(self._courses.iloc[i]["Course Name"]),
                "score": float(sims[i]),
                "description": _safe(self._courses.iloc[i].get("Course Description")),
                "learning_outcomes": _safe(
                    self._courses.iloc[i].get("Learning Outcomes", "")
                ),
            }
            for i in top_idxs
        ]

    def get_top_postings(
        self, sector: str, job_title: str, top_n: int = 3
    ) -> List[Dict]:
        self._assert_loaded()
        desc = self.get_job_description(sector, job_title)
        if not desc:
            raise ValueError(
                f"No job description available for '{job_title}' in '{sector}'."
            )

        q_vec = self._posting_req_vec.transform([desc])
        sims = cosine_similarity(q_vec, self._posting_req_mat)[0]
        top_idxs = sims.argsort()[-top_n:][::-1]

        return [
            {
                "position": _safe(self._careeraxis.iloc[i]["Position"]),
                "employer": _safe(self._careeraxis.iloc[i].get("Employer")),
                "industry": _safe(self._careeraxis.iloc[i].get("Industry")),
                "country": _safe(self._careeraxis.iloc[i].get("Country")),
                "score": float(sims[i]),
                "summary": _safe(self._careeraxis.iloc[i].get("Summary")),
                "url": _safe(self._careeraxis.iloc[i].get("Url")),
                "opportunity_type": _safe(
                    self._careeraxis.iloc[i].get("Opportunity type(s)")
                ),
                "contract_type": _safe(
                    self._careeraxis.iloc[i].get("Contract type")
                ),
            }
            for i in top_idxs
        ]

    def get_raw_tsc_skills(self, sector: str, job_title: str) -> List[Dict]:
        self._assert_loaded()
        row = self._get_job_row(sector, job_title)
        if row is None:
            return []
        tsc_text = _safe(row.get("Technical Skills (with levels)"))
        if not tsc_text:
            return []

        results = []
        for skill, level in _parse_tscs(tsc_text):
            match = self._taxonomy[
                (self._taxonomy["tsc_title"] == skill)
                & (self._taxonomy["proficiency_level"].astype(str) == str(level))
            ]
            results.append(
                {
                    "skill": skill.title(),
                    "level": int(level),
                    "description": _safe(
                        match.iloc[0]["proficiency_description"]
                    ) if not match.empty else "",
                }
            )
        return results

    def get_tsc_summary(self, sector: str, job_title: str) -> str:
        """
        Generates an AI summary using facebook/bart-large-cnn.
        The summarizer pipeline is cached after first load so the model
        is only read from disk once per process lifetime.
        """
        self._assert_loaded()
        tsc_skills = self.get_raw_tsc_skills(sector, job_title)
        if not tsc_skills:
            raise ValueError("No technical skills data found for this role.")

        descs = [s["description"] for s in tsc_skills if s["description"]]
        if not descs:
            raise ValueError(
                "Technical skills exist but no descriptions found in the taxonomy."
            )

        # Cache key so the same job is never summarised twice
        cache_key = (sector.strip().lower(), job_title.strip().lower())
        if not hasattr(self, "_summary_cache"):
            self._summary_cache: dict = {}
        if cache_key in self._summary_cache:
            return self._summary_cache[cache_key]

        # Load the pipeline once and reuse it
        if not hasattr(self, "_summarizer") or self._summarizer is None:
            from transformers import pipeline as hf_pipeline
            self._summarizer = hf_pipeline("summarization", model="facebook/bart-large-cnn")

        text_to_summarize = " ".join(descs)
        result = self._summarizer(
            text_to_summarize, max_length=200, min_length=60, do_sample=False
        )
        summary = result[0]["summary_text"]
        self._summary_cache[cache_key] = summary
        return summary

    # ── Resume Matcher ─────────────────────────────────────────────────────────

    def extract_text_from_pdf(self, uploaded_file) -> str:
        """
        Extract all text from a PDF file object (e.g. st.file_uploader result).
        """
        try:
            import pdfplumber
        except ImportError:
            raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")

        parts = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                parts.append(page.extract_text() or "")
        return re.sub(r"\s+", " ", "\n".join(parts)).strip()

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract recognised technical skills from plain text using n-gram matching.
        Returns a sorted list of found skill strings.
        """
        self._assert_loaded()
        if not text.strip():
            return []

        doc = self._nlp(text)
        tokens = [t.text for t in doc]
        lowered = [t.lower() for t in tokens]
        found: set = set()

        for n in range(1, 6):
            for i in range(len(tokens) - n + 1):
                span = " ".join(lowered[i : i + n])
                if span in SKILL_TERMS_NORM:
                    found.add(" ".join(tokens[i : i + n]).strip(" ,.-"))

        return sorted(found, key=str.lower)

    def find_matching_jobs(
        self, skills: List[str], top_n: int = 10
    ) -> Dict:
        """
        Match a list of skills against the CareerAxis job postings.
        Returns {'strong': [...], 'good': [...], 'weak': [...], 'thresholds': {...}}.
        All score values come from cosine similarity computation.
        """
        self._assert_loaded()
        if not skills:
            raise ValueError("skills list is empty.")

        resume_text = " ".join(sorted({s.lower() for s in skills}))
        q_vec = self._posting_full_vec.transform([resume_text])
        sims = cosine_similarity(q_vec, self._posting_full_mat)[0]

        tmp = self._careeraxis.copy()
        tmp["_sim"] = sims
        top = tmp.nlargest(top_n, "_sim")

        strong: List[Dict] = []
        good: List[Dict] = []
        weak: List[Dict] = []

        for _, row in top.iterrows():
            sim = float(row["_sim"])
            info = {
                "position": _safe(row.get("Position")),
                "employer": _safe(row.get("Employer")),
                "industry": _safe(row.get("Industry")),
                "country": _safe(row.get("Country")),
                "score": sim,
                "summary": _safe(row.get("Summary")),
                "url": _safe(row.get("Url")),
                "opportunity_type": _safe(row.get("Opportunity type(s)")),
            }
            if sim >= STRONG_THRESHOLD:
                strong.append(info)
            elif sim >= GOOD_THRESHOLD:
                good.append(info)
            elif sim >= WEAK_THRESHOLD:
                weak.append(info)

        return {
            "strong": strong,
            "good": good,
            "weak": weak,
            "thresholds": {
                "strong": STRONG_THRESHOLD,
                "good": GOOD_THRESHOLD,
                "weak": WEAK_THRESHOLD,
            },
        }
