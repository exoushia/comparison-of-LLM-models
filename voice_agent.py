"""
KRDCL (imaginary distribution utility company) Hindi voice agent — local console only.

What this file does, end to end:
    1. You run `python voice_agent.py dev` → LiveKit worker starts and waits for jobs.
    2. You run `python voice_agent.py console` → mic/speaker session joins a room.
    3. `entrypoint()` wires Sarvam STT/TTS + OpenAI LLM into an AgentSession.
    4. You speak → Sarvam transcribes (codemix Hindi) → GPT replies in Hindi → Sarvam speaks back.

TODO (future): SIP / real phone calls via LiveKit Telephony — dispatch rules, phone number,
    `participant.kind == SIP`, and `sip.phoneNumber` logging (see LiveKit telephony docs).

Stack:
    - Transport : LiveKit console (laptop mic + speaker)
    - STT       : Sarvam Saaras v3  (hi-IN, codemix, flush_signal)
    - LLM       : OpenAI GPT-4o-mini
    - TTS       : Sarvam Bulbul v3   (hi-IN)

Run locally:
    python voice_agent.py dev       # terminal 1 — leave running
    python voice_agent.py console   # terminal 2 — talk to the agent

Observability (OpenLIT — tokens + approx cost):
    Same setup as ground_truth/openlit_monitoring.ipynb — one openlit.init() patches
    OpenAI + Sarvam SDK calls automatically (no manual span code per turn).

    1. Start OpenLIT platform (once):
           git clone https://github.com/openlit/openlit.git && cd openlit && docker compose up -d
    2. UI: http://127.0.0.1:3000  (user@openlit.io / openlituser)
    3. OTLP: http://127.0.0.1:4318  (set via OTEL_EXPORTER_OTLP_ENDPOINT or use default below)
    4. Run agent → talk in console → refresh dashboard for per-call tokens + estimated cost

    Or zero-code wrap (notebook alternative):
        openlit-instrument --service-name krdcl-voice-agent python voice_agent.py dev

.env needs:
    LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
    SARVAM_API_KEY, OPENAI_API_KEY
    optional: OPENAI_VOICE_MODEL, SARVAM_TTS_SPEAKER
    optional observability: OPENLIT_ENABLED=false to skip; else needs OpenLIT docker + dashboard :3000
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()  # must run before openlit + SDK imports read API keys


def _init_openlit() -> None:
    """Optional: track OpenAI/Sarvam tokens + cost in OpenLIT UI. Off by default if OPENLIT_ENABLED=false."""
    if os.getenv("OPENLIT_ENABLED", "true").lower() in ("0", "false", "no", "off"):
        print("[openlit] off (OPENLIT_ENABLED=false)")
        return

    import openlit
    openlit.init(
        otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4318"),
        application_name=os.getenv("OPENLIT_APP_NAME", "krdcl-voice-agent"),
        environment=os.getenv("OPENLIT_ENVIRONMENT", "development"),
    )
    print("[openlit] on — token/cost traces at http://127.0.0.1:3000 (needs OpenLIT docker; see openlit_monitoring.ipynb)")


_init_openlit()

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.beta.tools import EndCallTool
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.voice.events import UserStateChangedEvent
from livekit.plugins import openai, sarvam

# hang up if caller is silent this long while the agent is NOT speaking (both in "listening")
USER_SILENCE_TIMEOUT_SECONDS = float(os.getenv("USER_SILENCE_TIMEOUT_SECONDS", "15"))


# ── Prompts (KRDCL domain + how the agent should sound) ─────────────────
# Kept inline here so this script runs standalone — same content as krdcl-voice-agent/agent.py

SYSTEM_PROMPT = """
You are a Hindi-speaking customer service agent for KRDCL
(Krishnapur Rajya Distribution Company Limited), a state electricity
distribution company.

## Rules
- Always respond in Hindi (Devanagari script).
- Common English terms used naturally in Indian Hindi are fine inside
  Hindi sentences: bill, meter, smart meter, payment, online, app,
  UPI, Paytm, PhonePe, consumer number, complaint, check meter.
- Address the caller as "जी".
- Maximum 2 short sentences per turn.
- Think through steps internally. Do NOT read out bullet points,
  reasoning, or English notes — only the final Hindi reply.
- Never fabricate data. If unsure, say you will check and call back.

## KRDCL Facts
- Helpline: 1912
- App: KRDCL Mitra (Play Store / App Store)
- Online payment: Paytm, PhonePe, Google Pay — enter consumer number
- Digital payment: 1% rebate if paid online before due date
- Smart meter programme: under RDSS, prepaid meters being installed
- Smart prepaid benefits: real-time usage on app, no estimated billing,
  recharge like mobile, no security deposit, warnings before low balance
- Check meter: installed within 48 hours on complaint, bill revised
  if reading differs
- Billing cycle: monthly, due date 15th of following month

## Conversation Flow
1. Greet warmly.
2. Listen to the issue.
3. Billing complaint → empathise → ask consumer number → offer check meter.
4. Payment query → guide through UPI steps → mention 1% discount.
5. Smart meter question → explain prepaid benefits simply.
6. End by asking if anything else is needed.
7. When the caller says they are done, thank them briefly (धन्यवाद / शुभ दिन) and use
   end_call when appropriate. If the caller says nothing for a few seconds while you
   are not speaking, the line disconnects automatically.
"""

# One-off instruction for the first spoken turn only (not the full system prompt)
GREETING = (
    "Greet the caller in Hindi. Say: नमस्ते जी, KRDCL helpline में "
    "आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ? "
    "Keep it to these two sentences only."
)


class KRDCLVoiceAgent(Agent):
    """
    Hindi DISCOM voice agent — wires Sarvam + OpenAI into LiveKit's Agent class.

    I followed krdcl-voice-agent/agent.py for the pipeline settings that actually
    behaved well in testing (flush_signal, STT turn detection, no extra VAD).
    """

    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,

            # ── STT: Sarvam POST speech-to-text (Saaras v3) ──
            # API: streaming audio in → transcript out, per LiveKit sarvam plugin
            # mode="codemix" : keeps English words (bill, UPI) in Latin — matches how callers speak
            # flush_signal=True : tells Sarvam when a turn ended; required for clean turn-taking
            stt=sarvam.STT(
                language="hi-IN",
                model="saaras:v3",
                mode="codemix",
                flush_signal=True,
            ),

            # ── LLM: OpenAI chat completion ──
            # API: messages[] in → assistant text out (LiveKit plugin wraps the HTTP call)
            # gpt-4o-mini default — good enough for short Hindi replies, lower cost than gpt-4o
            llm=openai.LLM(
                model=os.getenv("OPENAI_VOICE_MODEL", "gpt-4o-mini"),
            ),

            # ── TTS: Sarvam POST text-to-speech (Bulbul v3) ──
            # API: Hindi text in → audio stream out
            # speaker "shubh"
            tts=sarvam.TTS(
                target_language_code="hi-IN",
                model="bulbul:v3",
                speaker=os.getenv("SARVAM_TTS_SPEAKER", "shubh"),
                pace=1.0,
                temperature=0.5,
            ),

            # ── Turn detection (who decides "user finished speaking") ──
            # "stt" = use Sarvam endpointing, not Silero VAD — avoids fighting two VADs
            # 0.07s delay ≈ Sarvam's ~70ms processing latency before we treat utterance as final
            turn_detection="stt",
            min_endpointing_delay=0.07,

            # ── Tools ──
            # EndCallTool lets the LLM hang up when the caller is done (LiveKit ends the session)
            tools=[EndCallTool()],
        )

    async def on_enter(self) -> None:
        """
        LiveKit calls this when the agent joins the room.
        We trigger the opening Hindi greeting via a one-shot LLM+TTS generation.
        """
        self.session.generate_reply(instructions=GREETING)


def _attach_user_silence_hangup(session: AgentSession) -> None:
    """
    Close the call when the consumer says nothing for N seconds continuously,
    but only while the agent is not speaking.

    LiveKit's user_away_timeout already waits until agent + user are both in
    "listening" before starting the timer (timer is cancelled while agent speaks).
    We shutdown when the user flips to "away".
    """

    @session.on("user_state_changed")
    def _on_user_state(ev: UserStateChangedEvent) -> None:
        if ev.new_state != "away":
            return
        # don't hang up mid-agent-speech — away should only fire when both were listening
        if session.agent_state in ("speaking", "thinking"):
            return
        print(f"[krdcl] caller silent {USER_SILENCE_TIMEOUT_SECONDS:.0f}s — closing session")
        session.shutdown()


async def entrypoint(ctx: JobContext) -> None:
    """
    LiveKit job entry — runs when console mode connects to a room.

    Flow: wait for participant → start AgentSession → mic → STT → LLM → TTS → speaker.
    """
    participant = await ctx.wait_for_participant()
    print(f"[krdcl] console connected — user {participant.identity}, room {ctx.room.name}")

    # AgentSession orchestrates the voice pipeline — do NOT pass vad= here;
    # Sarvam STT already does voice activity + endpointing when turn_detection="stt"
    session = AgentSession(user_away_timeout=USER_SILENCE_TIMEOUT_SECONDS)
    _attach_user_silence_hangup(session)
    await session.start(agent=KRDCLVoiceAgent(), room=ctx.room)


if __name__ == "__main__":
    # LiveKit Agents CLI — subcommands: dev (worker), console (local mic), etc.
    # WorkerOptions.entrypoint_fnc is the hook LiveKit invokes per incoming job
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
