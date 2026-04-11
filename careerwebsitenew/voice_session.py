"""
voice_session.py — runs as a subprocess launched by Streamlit.
Connects to Agent126 via VoiceLive SDK, streams audio locally,
and writes transcript lines to stdout for Streamlit to read.
"""
from __future__ import annotations
import asyncio
import base64
import sys
import queue
import os
from typing import Optional, Any, Union
import pyaudio

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import AzureCliCredential
from azure.ai.voicelive.aio import connect, AgentSessionConfig
from azure.ai.voicelive.models import (
    InputAudioFormat, Modality, OutputAudioFormat,
    RequestSession, ServerEventType, MessageItem,
    InputTextContentPart, LlmInterimResponseConfig,
    InterimResponseTrigger,
)

ENDPOINT     = "https://imperialntures1.services.ai.azure.com/"
AGENT_NAME   = "Agent126:3"
PROJECT_NAME = "proj-default"

class AudioProcessor:
    def __init__(self, connection) -> None:
        self.connection  = connection
        self.audio       = pyaudio.PyAudio()
        self.format      = pyaudio.paInt16
        self.channels    = 1
        self.rate        = 24000
        self.chunk_size  = 1200
        self.input_stream  = None
        self.output_stream = None
        self.playback_queue: queue.Queue = queue.Queue()
        self.playback_base = 0
        self.next_seq     = 0
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def _seq(self):
        s = self.next_seq; self.next_seq += 1; return s

    def start_capture(self):
        def _cb(in_data, _fc, _ti, _sf):
            audio_b64 = base64.b64encode(in_data).decode()
            asyncio.run_coroutine_threadsafe(
                self.connection.input_audio_buffer.append(audio=audio_b64), self.loop
            )
            return (None, pyaudio.paContinue)
        self.loop = asyncio.get_event_loop()
        self.input_stream = self.audio.open(
            format=self.format, channels=self.channels, rate=self.rate,
            input=True, frames_per_buffer=self.chunk_size,
            stream_callback=_cb,
        )

    def start_playback(self):
        remaining = bytes()
        def _cb(_in, frame_count, _ti, _sf):
            nonlocal remaining
            frame_count *= pyaudio.get_sample_size(pyaudio.paInt16)
            out = remaining[:frame_count]
            remaining = remaining[frame_count:]
            while len(out) < frame_count:
                try:
                    pkt = self.playback_queue.get_nowait()
                except queue.Empty:
                    out += bytes(frame_count - len(out)); break
                if not pkt or not pkt[1]:
                    break
                seq, data = pkt
                if seq < self.playback_base:
                    remaining = bytes(); continue
                need = frame_count - len(out)
                out += data[:need]; remaining = data[need:]
            return (out[:frame_count], pyaudio.paContinue)
        self.output_stream = self.audio.open(
            format=self.format, channels=self.channels, rate=self.rate,
            output=True, frames_per_buffer=self.chunk_size,
            stream_callback=_cb,
        )

    def queue_audio(self, data: Optional[bytes]):
        self.playback_queue.put((self._seq(), data))

    def skip_audio(self):
        self.playback_base = self._seq()

    def shutdown(self):
        for s in [self.input_stream, self.output_stream]:
            if s:
                try: s.stop_stream(); s.close()
                except: pass
        try: self.audio.terminate()
        except: pass


async def run_session(career_goal: str, interview_type: str, cv_snippet: str):
    credential = AzureCliCredential()

    agent_config: AgentSessionConfig = {
        "agent_name":   AGENT_NAME,
        "project_name": PROJECT_NAME,
    }

    async with connect(
        endpoint=ENDPOINT,
        credential=credential,
        api_version="2026-01-01-preview",
        agent_config=agent_config,
    ) as conn:
        ap = AudioProcessor(conn)
        ap.start_playback()

        # Configure session
        await conn.session.update(session=RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            interim_response=LlmInterimResponseConfig(
                triggers=[InterimResponseTrigger.LATENCY],
                latency_threshold_ms=100,
                instructions="Give brief bridging responses if needed.",
            ),
        ))

        active_response = False
        session_ready   = False
        greeted         = False

        async for event in conn:
            etype = event.type

            if etype == ServerEventType.SESSION_UPDATED:
                session_ready = True
                ap.start_capture()

                if not greeted:
                    greeted = True
                    # Send career context as opening system message
                    opening = (
                        f"The student's career goal is: {career_goal}. "
                        f"They have selected: {interview_type}. "
                    )
                    if cv_snippet:
                        opening += f"Here is a snippet of their CV:\n{cv_snippet}"
                    opening += (
                        "\n\nGreet the student warmly, confirm their goal and "
                        "interview type, and ask them to say 'I am ready for "
                        "the interview. Let's start with the interview.' "
                        "when they want to begin."
                    )
                    await conn.conversation.item.create(
                        item=MessageItem(
                            role="system",
                            content=[InputTextContentPart(text=opening)]
                        )
                    )
                    await conn.response.create()

            elif etype == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
                transcript = event.get("transcript", "").strip()
                if transcript:
                    # Write to stdout — Streamlit reads this
                    print(f"USER:{transcript}", flush=True)

            elif etype == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
                transcript = event.get("transcript", "").strip()
                if transcript:
                    print(f"AGENT:{transcript}", flush=True)

            elif etype == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                ap.skip_audio()
                if active_response:
                    try: await conn.response.cancel()
                    except: pass

            elif etype == ServerEventType.RESPONSE_CREATED:
                active_response = True

            elif etype == ServerEventType.RESPONSE_AUDIO_DELTA:
                ap.queue_audio(event.delta)

            elif etype == ServerEventType.RESPONSE_DONE:
                active_response = False

            elif etype == ServerEventType.ERROR:
                msg = event.error.message
                if "no active response" not in msg.lower():
                    print(f"ERROR:{msg}", flush=True)
                    break

        ap.shutdown()


if __name__ == "__main__":
    # Args passed from Streamlit: career_goal | interview_type | cv_snippet
    career_goal    = sys.argv[1] if len(sys.argv) > 1 else ""
    interview_type = sys.argv[2] if len(sys.argv) > 2 else "Behavioural Interview"
    cv_snippet     = sys.argv[3] if len(sys.argv) > 3 else ""
    asyncio.run(run_session(career_goal, interview_type, cv_snippet))