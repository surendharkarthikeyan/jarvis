import os
import asyncio
import aiohttp
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    TurnHandlingOptions,
    room_io,
)
from livekit.plugins import google, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv(".env")

REALTIME_MODEL = os.getenv(
    "GOOGLE_REALTIME_MODEL",
    "gemini-3.1-flash-live-preview"
)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# --------------------------------------------------
# Detect if question needs live data
# --------------------------------------------------
def needs_live_data(text: str) -> bool:
    text = text.lower()

    keywords = [
        "today","latest","current","now","recent","live",
        "score","price","weather","news","result",
        "election","stock","rate","update","winner",
        "open now","near me"
    ]

    if any(k in text for k in keywords):
        return True

    # questions with dates / years
    if "2026" in text or "this week" in text or "this month" in text:
        return True

    return False

# --------------------------------------------------
# Search Web (SerpAPI)
# --------------------------------------------------
async def search_web(query: str) -> str:
    if not SERPAPI_KEY:
        return "Live search key is missing."

    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "engine": "google",
        "api_key": SERPAPI_KEY
    }

    try:
        async with aiohttp.ClientSession() as client:
            async with client.get(url, params=params, timeout=8) as response:
                data = await response.json()

        results = []
        for item in data.get("organic_results", [])[:3]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            if title or snippet:
                results.append(f"{title}: {snippet}")

        return "\n".join(results) if results else "No fresh results found."

    except Exception as e:
        print("Search Error:", e)
        return "Unable to fetch live results right now."

# --------------------------------------------------
# Assistant Personality
# --------------------------------------------------
class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are Jarvis, a smart AI personal assistant.

Rules:
- Reply naturally and confidently.
- Keep answers short unless user asks for detail.
- Be accurate and helpful.
- If live search context is provided, use it.
- Sound human and clear.
"""
        )

# --------------------------------------------------
# Create Server
# --------------------------------------------------
server = AgentServer()

# --------------------------------------------------
# Main Agent Session
# --------------------------------------------------
@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: agents.JobContext):

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model=REALTIME_MODEL,
            voice="Puck",
            temperature=0.4,
            instructions="""
You are Jarvis, a fast and accurate voice assistant.
Reply in under 3 sentences unless user asks more.
"""
        ),
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(
            turn_detection=MultilingualModel(),
        ),
    )

    # Start Session
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        ),
    )

    print("Jarvis is ready...")

    # --------------------------------------------------
    # Process User Input
    # --------------------------------------------------
    async def process_message(text: str):
        try:
            print("User Said:", text)

            final_prompt = text

            if needs_live_data(text):
                print("Searching live data...")
                live_info = await search_web(text)

                final_prompt = f"""
User Question:
{text}

Latest Search Results:
{live_info}

Answer clearly, naturally, and briefly using the latest information.
"""

            await session.generate_reply(
                instructions=final_prompt
            )

        except Exception as e:
            print("Reply Error:", e)

    # --------------------------------------------------
    # LiveKit Event Handler (Sync only)
    # --------------------------------------------------
    def handle_message(text: str):
        asyncio.create_task(process_message(text))

    session.on("user_input_transcribed", handle_message)

# --------------------------------------------------
# Run App
# --------------------------------------------------
if __name__ == "__main__":
    agents.cli.run_app(server)