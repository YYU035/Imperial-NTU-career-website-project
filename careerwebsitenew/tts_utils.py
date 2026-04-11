"""
tts_utils.py — Azure Cognitive Services Text-to-Speech utility.
Returns raw WAV bytes that can be passed directly to st.audio().
"""
from __future__ import annotations

import streamlit as st
from gtts import gTTS
import io

def text_to_speech_gtts(text: str) -> bytes:
    """
    Convert text to MP3 bytes using gTTS (Google Translate TTS).
    Free, no API key required.
    """
    tts = gTTS(
        text=text,
        lang="en",
        tld="co.uk",   # British accent — use "com" for American
        slow=False,
    )
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()

# def text_to_speech_bytes(text: str) -> bytes | None:
#     """
#     Convert a text string to WAV audio bytes using Azure Neural TTS.

#     Returns:
#         Raw WAV bytes on success, or None if TTS is unavailable/disabled.

#     Raises:
#         RuntimeError if the Azure Speech SDK call fails.
#     """
#     # Gracefully skip if secrets are not configured
#     if "AZURE_SPEECH_KEY" not in st.secrets or "AZURE_SPEECH_REGION" not in st.secrets:
#         return None

#     try:
#         import azure.cognitiveservices.speech as speechsdk
#     except ImportError:
#         st.warning(
#             "⚠️ `azure-cognitiveservices-speech` is not installed. "
#             "Run `pip install azure-cognitiveservices-speech` to enable TTS."
#         )
#         return None

#     speech_config = speechsdk.SpeechConfig(
#         subscription=st.secrets["AZURE_SPEECH_KEY"],
#         region=st.secrets["AZURE_SPEECH_REGION"],
#     )

#     # Professional, neutral English voice — change to preference
#     # Full list: https://learn.microsoft.com/azure/ai-services/speech-service/language-support
#     speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"

#     # Synthesise to in-memory buffer (no speakers on the server)
#     synthesizer = speechsdk.SpeechSynthesizer(
#         speech_config=speech_config,
#         audio_config=None,   # None = return bytes, don't play on server
#     )

#     result = synthesizer.speak_text_async(text).get()

#     if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#         return result.audio_data   # raw WAV bytes

#     cancellation = result.cancellation_details
#     raise RuntimeError(
#         f"TTS synthesis failed.\n"
#         f"Reason : {result.reason}\n"
#         f"Details: {cancellation.reason} — {cancellation.error_details}"
#     )