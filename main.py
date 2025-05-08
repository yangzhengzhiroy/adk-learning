import os
import json
import asyncio
import typing
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from google.genai.types import (
    Part,
    Content,
)

from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from story_teller.agent import root_agent



APP_NAME = "gemini_live_api_demo"
STATIC_DIR = Path("static")


def start_agent_session(
    app_name: str,
    session_id: str,
    session_service: InMemorySessionService
) -> tuple[AsyncGenerator[Event, None], LiveRequestQueue]:
    """Start the agent session for each user session

    Args:
        app_name (str): the application name
        session_id (str): the unique session id

    Returns:
        tuple[AsyncGenerator, LiveRequestQueue]: the agent events and the live request queue
    """

    # Create a Session
    session = session_service.create_session(
        app_name=app_name,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=app_name,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality = TEXT
    run_config = RunConfig(
        response_modalities=["TEXT"],
        # streaming_mode=StreamingMode.SSE,
    )

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket: WebSocket, live_events: AsyncGenerator[Event, None]):
    """Agent to client communication"""
    while True:
        async for event in live_events:
            # turn_complete
            if event.turn_complete:
                await websocket.send_text(json.dumps({"turn_complete": True}))
                print("[TURN COMPLETE]")

            if event.interrupted:
                await websocket.send_text(json.dumps({"interrupted": True}))
                print("[INTERRUPTED]")

            # Read the Content and its first Part
            part: Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part or not event.partial:
                continue

            # Get the text
            text = event.content and event.content.parts and event.content.parts[0].text
            if not text:
                continue

            # Send the text to the client
            await websocket.send_text(json.dumps({"message": text}))
            print(f"[AGENT TO CLIENT]: {text}")
            await asyncio.sleep(0.5)


async def client_to_agent_messaging(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    """Websocket client sending audio bytes to agent

    Args:
        websocket (WebSocket): websocket
        live_request_queue (LiveRequestQueue): the bi-di request queue
    """
    print("client to agent messaging")
    while True:
        message = await websocket.receive()
        if "bytes" in message:
            # with open('recording.webm', 'rb') as f:
            #     audio_bytes = f.read()
            audio_bytes = typing.cast(bytes, message["bytes"])
            print("bytes", len(audio_bytes))
            content = Content(role="user", parts=[Part.from_bytes(data=audio_bytes, mime_type="audio/webm")])
            live_request_queue.send_content(content=content)
        elif "text" in message:
            input_text = typing.cast(str, message["text"])
            if input_text != "<audio complete>":
                print(input_text)
                content = Content(role="user", parts=[Part.from_text(text=input_text)])
                live_request_queue.send_content(content=content)
        await asyncio.sleep(0)


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    # initialize the in memory store
    global SESSION_SERVICE
    SESSION_SERVICE = InMemorySessionService()
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index_audio.html"))


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Client websocket endpoint"""

    # Wait for client connection
    await websocket.accept()
    print(f"Client {session_id} connected")

    # Start agent session
    live_events, live_request_queue = start_agent_session(APP_NAME, session_id, SESSION_SERVICE)

    # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )
    await asyncio.gather(agent_to_client_task, client_to_agent_task)

    # Disconnected
    print(f"Client {session_id} disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
