import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import spacy
import re
import os
import pickle
from pathlib import Path

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

CAREERAXIS_FILE = "careeraxis2025.xlsx"
EMBEDDINGS_CACHE = "job_embeddings.pkl"
MODEL_NAME = "distiluse-base-multilingual-cased-v2"

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise SystemExit("Run: python -m spacy download en_core_web_sm")

CORE_CONCEPTS = {"power", "system", "circuit", "control", "signal", "voltage", "electrical", "electronic", "embedded", "smart"}

SKILL_TERMS = {
    # Programming / CS
    "python", "c", "c++", "java", "javascript", "typescript",
    "html", "css", "sql",
    "data structures", "algorithms", "data structures & algorithms",
    "object oriented programming", "oop",

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

    # EEE / signals (shortened from your earlier huge list to the most common)
    "signal processing", "digital signal processing",
    "image processing",
    "control systems",
    "embedded systems",
    "microcontrollers",
    "electrical machines",

    # Finance / business tech
    "financial modelling", "financial modeling",
    "valuation", "excel modelling", "excel modeling",
    "corporate finance",

    # Generic but still technical-ish
    "data analysis", "data analytics", "data engineering",
    "sql databases", "relational databases",

    # Programming / general software
    "python", "c", "c++", "java", "javascript", "typescript",
    "html", "css", "sql",
    "data structures", "algorithms", "data structures & algorithms",
    "object oriented programming", "oop",
    "matlab", "simulink", "labview", "shell scripting",
    "automation scripts", "data analysis",

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
    "earthing and grounding", "grounding systems",
    "lightning protection",

    # Control, automation, instrumentation
    "control systems", "feedback control", "pid control",
    "state space control", "state-space control", "robust control",
    "digital control", "model predictive control", "system identification",
    "scada", "dcs", "plc programming", "ladder logic",
    "industrial automation", "process control", "instrumentation",
    "sensors and actuators", "data acquisition", "daq systems",
    "hmi design", "robotics", "robot kinematics",
    "trajectory planning", "motion control",

    # Embedded, microcontrollers, and iot
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
    "link budget analysis", "channel coding",
    "error control coding",

    # DSP, signals, and imaging
    "digital signal processing", "dsp algorithms",
    "fourier transform", "z transform", "z-transform",
    "filter design", "fir filter", "iir filter",
    "multirate signal processing", "time frequency analysis",
    "audio signal processing", "image processing", "computer vision",

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

    # General tools / environments
    "matlab programming", "simulink modeling",
    "labview programming", "git", "linux",

    # Soft and professional skills
    "problem solving", "analytical thinking", "critical thinking",
    "teamwork", "communication skills", "technical writing",
    "documentation", "project management", "time management",
    "attention to detail",
}

SKILL_TERMS_NORM = {s.lower() for s in SKILL_TERMS}

job_match_model = None
careeraxis_df = pd.DataFrame()
cached_embeddings = None

def load_data_and_embeddings():
    """
    Initializes the dataset and handles the embedding cache.
    """
    global careeraxis_df, cached_embeddings, job_match_model
    if job_match_model is None:
        job_match_model = SentenceTransformer(MODEL_NAME)

    df = pd.read_excel(CAREERAXIS_FILE, sheet_name="in")
    df["Details"] = df["Details"].astype(str)
    careeraxis_df = df.reset_index(drop=True)

    if os.path.exists(EMBEDDINGS_CACHE):
        print("Checking existing cache")
        with open(EMBEDDINGS_CACHE, 'rb') as f:
            cache_data = pickle.load(f)
            
        if len(cache_data) == len(careeraxis_df):
            cached_embeddings = cache_data
            print("Successfully loaded embeddings from cache.")
        else:
            print("Excel file has changed (row count mismatch). Re-generating embeddings...")
            create_and_save_embeddings()
    else:
        print("First time setup: Generating embeddings (this will take a while)...")
        create_and_save_embeddings()

def create_and_save_embeddings():
    """
    Converts all job details into vectors and saves them to a file.
    """
    global cached_embeddings
    job_texts = careeraxis_df["Details"].tolist()
    
    cached_embeddings = job_match_model.encode(
        job_texts, 
        convert_to_numpy=True, 
        show_progress_bar=True
    )
    
    with open(EMBEDDINGS_CACHE, 'wb') as f:
        pickle.dump(cached_embeddings, f)
    print(f"Done! Created {len(cached_embeddings)} embeddings and saved to {EMBEDDINGS_CACHE}")

def extract_text_from_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            text_parts.append(txt)
    return "\n".join(text_parts)

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def extract_skills(full_text: str):
    if not full_text.strip():
        return []

    doc = nlp(full_text)
    tokens = [t.text for t in doc]
    lowered = [t.lower() for t in tokens]
    found = set()

    for n in range(1, 6):
        for i in range(len(tokens) - n + 1):
            span_text = " ".join(lowered[i:i + n])
            if span_text in SKILL_TERMS_NORM:
                original = " ".join(tokens[i:i + n])
                found.add(original.strip(" ,.-"))

    return sorted(found, key=str.lower)

def calculate_hybrid_score(resume_skills, resume_concepts, job_idx, semantic_sim):
    """Combines AI meaning with a 'Fuzzy Keyword Overlap' score."""
    job_text = careeraxis_df.iloc[job_idx]["Details"].lower()
    
    skill_match_count = 0
    for skill in resume_skills:
        if skill in job_text:
            skill_match_count += 1
        else:
            skill_words = skill.split()
            if len(skill_words) > 1 and all(word in job_text for word in skill_words):
                skill_match_count += 0.8  
                
    concept_matches = sum(1 for c in resume_concepts if c in job_text)
    
    skill_score = skill_match_count / len(resume_skills) if resume_skills else 0
    concept_score = concept_matches / len(resume_concepts) if resume_concepts else 0
    
    final_score = (semantic_sim * 0.5) + (skill_score * 0.3) + (concept_score * 0.2)
    return final_score

def find_matching_jobs_from_skills(skills, top_n=5, strong_threshold=0.45, good_threshold=0.30, weak_threshold=0.15):
    if not skills or cached_embeddings is None:
        return [], []

    resume_text = ", ".join(sorted({s.lower() for s in skills}))
    resume_vec = job_match_model.encode([resume_text], convert_to_numpy=True)

    sims = cosine_similarity(resume_vec, cached_embeddings)[0]

    tmp = careeraxis_df.copy()
    tmp["skill_similarity"] = sims
    tmp = tmp.sort_values("skill_similarity", ascending=False).head(top_n)

    strong_matches = []
    good_matches = []
    weak_matches = []

    for _, row in tmp.iterrows():
        sim = row["skill_similarity"]
        job_info = {
            "Position": row.get("Position", "Unknown"),
            "Employer": row.get("Employer", "Unknown"),
            "Industry": row.get("Industry", "Unknown"),
            "Similarity": float(sim),
        }

        if sim >= strong_threshold:
            strong_matches.append(job_info)
        elif sim >= good_threshold:
            good_matches.append(job_info)
        elif sim >= weak_threshold:
            weak_matches.append(job_info)

    return strong_matches, good_matches, weak_matches


def select_and_analyze_resume():
    file_path = filedialog.askopenfilename(title="Select Resume", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    try:
        raw_text = extract_text_from_pdf(file_path)
        cleaned = clean_text(raw_text)
        skills = extract_skills(cleaned)

        if not skills:
            messagebox.showwarning("No Skills", "No skills from the dictionary were found in your resume.")
            return

        strong, good, weak = find_matching_jobs_from_skills(skills)

        result_text = f"Detected Skills:\n{', '.join(skills)}\n\n"
        
        if strong:
            result_text += "--- STRONG MATCHES ---\n"
            for j in strong:
                result_text += f"- {j['Position']} @ {j['Employer']} ({j['Similarity']:.2f})\n"
        
        if good:
            result_text += "\n--- GOOD MATCHES ---\n"
            for j in good:
                result_text += f"- {j['Position']} @ {j['Employer']} ({j['Similarity']:.2f})\n"

        if weak:
            result_text += "\n--- WEAK MATCHES ---\n"
            for j in weak:
                result_text += f"- {j['Position']} @ {j['Employer']} ({j['Similarity']:.2f})\n"

        if not strong and not good and not weak:
            result_text += "No matches found above the similarity thresholds."

        res_window = tk.Toplevel()
        res_window.title("Analysis Results")
        txt_area = tk.Text(res_window, wrap="word", width=80, height=25)
        txt_area.insert("1.0", result_text)
        txt_area.pack(padx=10, pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def main():
    load_data_and_embeddings()

    root = tk.Tk()
    root.title("CareerAxis Demo Matcher")
    root.geometry("400x200")

    lbl = tk.Label(root, text="Resume Job Matcher (Optimized)", pady=20)
    lbl.pack()

    btn = tk.Button(root, text="Upload Resume PDF", command=select_and_analyze_resume, width=20, height=2)
    btn.pack()

    root.mainloop()

if __name__ == "__main__":
    main()