"""
agent_api.py — Azure AI Agent integration for EEE Career Pathways Platform.
Builds the prompt exactly as the original Colab notebook does, calls the
Azure agent, and returns the parsed JSON response. No prompt logic here
— all intelligence lives in the Azure agent itself.
"""
from __future__ import annotations

import json
import re
from openai import OpenAI
import streamlit as st


@st.cache_resource(show_spinner=False)
def get_agent_client() -> OpenAI:
    return OpenAI(
        api_key=st.secrets["AZURE_API_KEY"],
        base_url=st.secrets["AZURE_API_URL"],
        default_query={"api-version": "2025-11-15-preview"},
    )

def query_agent(user_query: str, cv_text: str | None = None) -> dict:
    """
    Call the Azure agent with the same prompt structure as the Colab notebook.

    Returns the agent's response as a parsed dict. The agent is expected to
    return JSON matching the structure in the example output document.

    Raises RuntimeError if the call fails or the response can't be parsed.
    """
    # Build prompt exactly as in the Colab notebook
    if cv_text:
        prompt_content = (
            f"User Query: {user_query}\n\n"
            f"Here is some additional context from a PDF document:\n\n{cv_text}\n\n"
            f"Based on this information, provide a response."
        )
    else:
        prompt_content = user_query

    client = get_agent_client()
    response = client.responses.create(input=prompt_content)
    raw_text = response.output_text.strip()

    # Strip any accidental markdown fences the agent might wrap around JSON
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # Agent returned plain text rather than JSON — wrap it so the
        # display layer always gets a dict with at least a text field
        parsed = {"raw_text": raw_text}

    parsed["_raw"] = raw_text
    parsed["_output_tokens"] = getattr(response.usage, "output_tokens", None)
    return parsed

def query_job_match_agent(user_query: str, cv_text: str, parsed: str | None = None) -> dict:
    """
    Call the job matching agent. Returns the first item from the agent's
    JSON array response, with semicolon-delimited fields parsed into lists.

    Raises RuntimeError if the call fails or returns unparseable output.
    """
    if cv_text:
        prompt_content = (
            f"User Query: {user_query}\n\n"
            f"Here is some additional context from a PDF document:\n\n{cv_text}\n\n"
            f"Additionally, the same user query and PDF have been passed to an agent that provides information on current skills, relevant modules and experiences, recommended future modules, skills and experiences."
            f"You can find its output here as a basis for you: {parsed}"
            f"Based on this information, provide a response."
        )
    else:
        prompt_content = user_query

    client = OpenAI(
        api_key=st.secrets["AZURE_API_KEY"],
        base_url=st.secrets["AZURE_JOB_API_URL"],
        default_query={"api-version": "2025-11-15-preview"},
    )

    response = client.responses.create(input=prompt_content)
    raw_text = response.output_text.strip()

    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    try:
        parsed = json.loads(cleaned)
        # Agent returns a list — take the first item
        item = parsed[0] if isinstance(parsed, list) else parsed
    except json.JSONDecodeError:
        item = {"raw_text": raw_text}

    # Parse semicolon-delimited string fields into lists
    def split_semi(val: str) -> list[str]:
        if not val:
            return []
        return [s.strip() for s in val.split(";") if s.strip()]

    return {
        "match_level":               item.get("Match Level", 0),
        "top_applicant":             item.get("Top Applicant?", "").lower() == "yes",
        "required_skills_achieved":  split_semi(item.get("Required skills achieved", "")),
        "absent_required_skills":    split_semi(item.get("Absent required skills", "")),
        "additional_skills_others":  split_semi(item.get("Additional skills of other applicants", "")),
        "cv_tips":                   split_semi(item.get("CV tips", "")),
        "_raw":                      raw_text,
        "_output_tokens":            getattr(response.usage, "output_tokens", None),
    }

def query_specific_job_agent(
    cv_text: str,
    job_description: str,
    parsed: str | None = None,
) -> dict:
    """
    Rate the CV against a specific job description provided by the user.
    Returns the same structure as query_job_match_agent for consistent display.
    """
    prompt_parts = [
        f"Here is the candidate's CV:\n\n{cv_text}",
        f"Here is the specific job description and requirements:\n\n{job_description}",
    ]
    if parsed:
        prompt_parts.append(
            f"For additional context, here is a career analysis of the same candidate "
            f"including their current skills, relevant modules, and recommended development: "
            f"{parsed}"
        )
    prompt_parts.append("Based on this information, provide a response.")
    prompt_content = "\n\n".join(prompt_parts)

    client = OpenAI(
        api_key=st.secrets["AZURE_API_KEY"],
        base_url=st.secrets["AZURE_SPECIFIC_JOB_API_URL"],
        default_query={"api-version": "2025-11-15-preview"},
    )

    response = client.responses.create(input=prompt_content)
    raw_text = response.output_text.strip()

    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    try:
        parsed_json = json.loads(cleaned)
        item = parsed_json[0] if isinstance(parsed_json, list) else parsed_json
    except json.JSONDecodeError:
        item = {"raw_text": raw_text}

    def split_semi(val: str) -> list[str]:
        if not val:
            return []
        return [s.strip() for s in val.split(";") if s.strip()]

    return {
        "match_level":              item.get("Match Level", 0),
        "top_applicant":            item.get("Top Applicant?", "").lower() == "yes",
        "required_skills_achieved": split_semi(item.get("Required skills achieved", "")),
        "absent_required_skills":   split_semi(item.get("Absent required skills", "")),
        "additional_skills_others": split_semi(item.get("Additional skills of other applicants", "")),
        "cv_tips":                  split_semi(item.get("CV tips", "")),
        "_raw":                     raw_text,
        "_output_tokens":           getattr(response.usage, "output_tokens", None),
    }

import os
def query_interview_agent(
    conversation: list,
    cv_text: str | None = None,
    career_goal: str | None = None,
) -> dict:
    """
    Send the conversation history to the Azure AI Foundry interview agent.
    Uses the Responses API (the only supported protocol for Agent Applications).
    Conversation history is manually concatenated into a single input string
    because Agent Applications are stateless.
    """
    history_lines = []

    if career_goal:
        history_lines.append(f"Career Goal: {career_goal}")
    if cv_text:
        history_lines.append(f"CV (first 4000 chars):\n{cv_text[:4000]}")
    if career_goal or cv_text:
        history_lines.append("---")

    for msg in conversation:
        speaker = "Student" if msg["role"] == "user" else "Interviewer"
        history_lines.append(f"{speaker}: {msg['content']}")

    full_input = "\n\n".join(history_lines)

    client = OpenAI(
        api_key=st.secrets["AZURE_API_KEY"],
        base_url=st.secrets["AZURE_INTERVIEW_API_URL"],
        default_query={"api-version": "2025-11-15-preview"},
    )

    try:
        response = client.responses.create(input=full_input)
        raw = response.output_text.strip()
    except Exception as e:
        raise RuntimeError(f"Interview agent call failed: {e}") from e

    return {
        "reply": raw,
        "_output_tokens": getattr(response.usage, "output_tokens", None),
    }

def query_sector_match_agent(
    cv_text: str,
    parsed: str | None = None,
) -> list[dict]:
    """
    Returns a ranked list of sectors the candidate is best suited for.
    Each item has 'Area' and 'Degree' (High / Medium / Low).
    """
    prompt_parts = [f"Here is the candidate's CV:\n\n{cv_text}"]
    if parsed:
        prompt_parts.append(
            f"Here is a career analysis of the same candidate for additional context: {parsed}"
        )
    prompt_parts.append("Based on this information, provide a response.")

    client = OpenAI(
        api_key=st.secrets["AZURE_API_KEY"],
        base_url=st.secrets["AZURE_SECTOR_API_URL"],
        default_query={"api-version": "2025-11-15-preview"},
    )

    response = client.responses.create(input="\n\n".join(prompt_parts))
    raw_text = response.output_text.strip()

    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    try:
        parsed_json = json.loads(cleaned)
        # Agent returns {"match_level": [...]} — extract the list
        if isinstance(parsed_json, dict):
            sectors = parsed_json.get("match_level", [])
        elif isinstance(parsed_json, list):
            sectors = parsed_json
        else:
            sectors = []
    except json.JSONDecodeError:
        sectors = []

    return {
        "sectors":        sectors,
        "_raw":           raw_text,
        "_output_tokens": getattr(response.usage, "output_tokens", None),
    }