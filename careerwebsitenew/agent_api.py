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