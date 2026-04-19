import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from transformers import pipeline


# ---------- FILE LOCATIONS ----------
skillsfuture_file = "Myskillsfuture pdf extraction.xlsx"
courses_file = "Course Catalog AY2324.xlsx"
postings_file = "careeraxis2025.xlsx"
taxonomy_file = "Taxonomy.xlsx"


# ---------- LOAD DATA ----------
skillsfuture_df = pd.read_excel(skillsfuture_file)
courses_df = pd.read_excel(courses_file)
postings_df = pd.read_excel(postings_file)
taxonomy_df = pd.read_excel(taxonomy_file)


# ---------- NORMALIZE FOR ROBUST FILTERING ----------
def normalize_col(df, col):
    df[col] = df[col].astype(str).str.strip().str.lower()
    return df

skillsfuture_df = normalize_col(skillsfuture_df, 'Sector')
skillsfuture_df = normalize_col(skillsfuture_df, 'Job Title')
courses_df = normalize_col(courses_df, 'Course Name')
postings_df = normalize_col(postings_df, 'Position')
taxonomy_df = normalize_col(taxonomy_df, 'tsc_title')

# For building menus, only require Sector + Job Title to be present.
skillsfuture_df = skillsfuture_df.dropna(subset=['Sector', 'Job Title'])

# For courses and postings, keep your existing constraints.
courses_df = courses_df.dropna(subset=['Course Name', 'Course Description'])
postings_df = postings_df.dropna(subset=['Position', 'Details'])


# ---------- HELPERS ----------
def parse_tscs(tscs_text):
    # Example pattern: "Data Analytics Level 3; Machine Learning Level 4"
    pattern = r"([A-Za-z0-9 ()\-]+) Level (\d+)"
    matches = re.findall(pattern, str(tscs_text))
    tscs_level_pairs = [(tsc.strip().lower(), level) for (tsc, level) in matches]
    return tscs_level_pairs

def extract_requirements(text):
    text = str(text)
    match = re.search(r"(?i)(requirements:|requirement[s]?:)(.*)", text)
    return match.group(2).strip() if match else text


# ---------- MAIN USER FLOW ----------
# 1. Sector selection
sector_choices = sorted(skillsfuture_df['Sector'].dropna().unique())
print("\nChoose a sector:")
for i, sector in enumerate(sector_choices):
    print(f"{i+1}. {sector.title()}")  # Capitalize for display

sector_idx = int(input("Enter sector number: ")) - 1
selected_sector = sector_choices[sector_idx]

sector_jobs = skillsfuture_df[skillsfuture_df['Sector'] == selected_sector]

print(f"\n{len(sector_jobs)} job rows available in {selected_sector.title()}.")

# 2. Job title selection
# If you want one menu entry per DISTINCT job title string:
title_choices = sorted(sector_jobs['Job Title'].dropna().drop_duplicates())

print("\nChoose a job title:")
for i, title in enumerate(title_choices):
    print(f"{i+1}. {title.title()}")

title_idx = int(input("Enter job title number: ")) - 1
selected_title = title_choices[title_idx]

# Among rows with that title, just take the first for now.
selected_job_row = sector_jobs[sector_jobs['Job Title'] == selected_title].iloc[0]

selected_desc = selected_job_row.get('Job Description', None)
selected_tscs = selected_job_row.get('Technical Skills (with levels)', None)

print(f"\nYou selected: {selected_title.title()} in {selected_sector.title()}")


# ---------- (A) TOP 5 NTU COURSES ----------
print("\n[1] Top 5 NTU Courses:")

model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

if pd.isna(selected_desc) or not str(selected_desc).strip():
    print("- No job description available; cannot compute semantic similarity to courses.")
else:
    course_descs = courses_df['Course Description'].tolist()
    course_embeddings = model.encode(course_descs, convert_to_numpy=True)
    job_embedding = model.encode([str(selected_desc)], convert_to_numpy=True)

    cosines_courses = cosine_similarity(job_embedding, course_embeddings)[0]
    top_course_indices = cosines_courses.argsort()[-5:][::-1]

    for idx in top_course_indices:
        row = courses_df.iloc[idx]
        cname = row['Course Name']
        ccode = row['Course Code']   # adjust column name if needed
        # print code + name, no similarity score
        print(f"- {ccode} - {cname.title()}")


# ---------- (B) TOP 3 JOB LISTINGS ----------
print("\n[2] Top 3 Job Postings (use the row index for full details):")

if pd.isna(selected_desc) or not str(selected_desc).strip():
    print("- No job description available; cannot compute similarity to postings.")
else:
    posting_details = [extract_requirements(d) for d in postings_df['Details'].tolist()]
    postings_embeddings = model.encode(posting_details, convert_to_numpy=True)
    job_embedding = model.encode([str(selected_desc)], convert_to_numpy=True)

    cosines_postings = cosine_similarity(job_embedding, postings_embeddings)[0]
    top_job_indices = cosines_postings.argsort()[-3:][::-1]

    for idx in top_job_indices:
        position = postings_df.iloc[idx]['Position']
        score = cosines_postings[idx]
        print(f"- Row {idx}: '{position.title()}' (Similarity score: {score:.3f})")


# ---------- (C) TSC SUMMARIZER ----------
print("\n[3] Technical Skills Summary:")

if pd.isna(selected_tscs) or not str(selected_tscs).strip():
    print("No technical skills info found for this job; skipping summarization.")
else:
    tsc_level_pairs = parse_tscs(selected_tscs)

    desc_texts = []
    for tsc, level in tsc_level_pairs:
        match = taxonomy_df[
            (taxonomy_df['tsc_title'] == tsc) &
            (taxonomy_df['proficiency_level'].astype(str) == str(level))
        ]
        if not match.empty:
            desc_texts.append(str(match.iloc[0]['proficiency_description']))

    to_summarize = " ".join(desc_texts)

    if len(to_summarize.strip()) > 0:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(
            to_summarize,
            max_length=200,
            min_length=60,
            do_sample=False
        )[0]['summary_text']
        print(summary)
    else:
        print("No skill descriptions found to summarize.")

print("\nDone.")
