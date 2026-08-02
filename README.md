# Jarvis

Jarvis is a LiveKit-based AI assistant project with two parts:

- a Python agent backend in [agent.py](agent.py) that connects to LiveKit, uses Google Gemini Realtime, and can fetch live web results through SerpAPI
- a SwiftUI client app in [jarvis/VoiceAgent](jarvis/VoiceAgent) that provides voice, text, and video interaction across Apple platforms

The goal of the project is to provide a responsive assistant experience with short natural replies, optional live-data lookup, and a clean cross-platform LiveKit client.

## Project structure

- [agent.py](agent.py) - LiveKit agent entry point
- [requirements.txt](requirements.txt) - Python dependencies for the agent
- [jarvis/VoiceAgent](jarvis/VoiceAgent) - SwiftUI client app source
- [jarvis/VoiceAgent.xcodeproj](jarvis/VoiceAgent.xcodeproj) - Xcode project
- [jarvis/BroadcastExtension](jarvis/BroadcastExtension) - screen share broadcast extension for supported Apple platforms

## What the agent does

The Python agent:

- connects to a LiveKit room through `livekit-agents`
- uses Google Gemini Realtime as the model backend
- enables voice activity detection with Silero
- uses multilingual turn detection
- optionally searches the web through SerpAPI when a prompt appears to need current information

The agent is configured in [agent.py](agent.py). It looks for live-data intent using keywords such as `latest`, `today`, `weather`, `news`, `price`, and `current`, then augments the reply with search results when available.

## What the app does

The Swift app provides the user interface for the assistant:

- voice interaction for speaking to the agent
- text interaction for typing messages
- video and screen-share support when the connected agent/model supports it
- connection state, error display, and a simple control bar

The app entry point is [jarvis/VoiceAgent/VoiceAgentApp.swift](jarvis/VoiceAgent/VoiceAgentApp.swift).

## Requirements

You will need:

- Python 3.10+ recommended
- Xcode with the Apple platform SDKs you plan to target
- a LiveKit project and sandbox token source for development
- Google Gemini Realtime access for the model backend
- a SerpAPI key if you want live web search responses

## Python setup

Create and activate a virtual environment, then install the agent dependencies:

```bash
pip install -r requirements.txt
```

If you prefer to run the agent from a local environment file, create a [`.env`](.env) file in the repository root.

### Environment variables

The agent reads the following variables:

- `GOOGLE_REALTIME_MODEL` - optional, defaults to `gemini-3.1-flash-live-preview`
- `SERPAPI_KEY` - optional, enables live web search in the agent

## Running the Python agent

From the repository root, start the agent with:

```bash
python agent.py
```

The agent should connect to a LiveKit room and wait for a client session to join.

## Running the Swift app

Open [jarvis/VoiceAgent.xcodeproj](jarvis/VoiceAgent.xcodeproj) in Xcode and run the `VoiceAgent` scheme.

For development, the app uses `SandboxTokenSource` in [jarvis/VoiceAgent/VoiceAgentApp.swift](jarvis/VoiceAgent/VoiceAgentApp.swift), so you need a valid LiveKit sandbox ID configured through the project settings or environment configuration expected by the template.

If you use the broadcast extension for screen sharing, make sure the `BroadcastExtension` target is enabled and signed correctly in Xcode.

## Typical workflow

1. Start the Python agent with `python agent.py`.
2. Launch the Swift app from Xcode.
3. Connect the app to the LiveKit room.
4. Use voice, text, or video input depending on what you want to test.

## Notes

- The app template in [jarvis/README.md](jarvis/README.md) contains LiveKit-specific Swift client guidance.
- The agent is intentionally short-form and conversational by default.
- When a prompt needs fresh data, the agent attempts a live web search before replying.
