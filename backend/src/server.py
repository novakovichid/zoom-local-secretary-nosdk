"""FastAPI server for Zoom Local Secretary."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rich.console import Console

from .config import config
from .recorder import AudioRecorder
from .pipeline import transcribe_and_summarize

console = Console()
app = FastAPI(title="Zoom Local Secretary")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/recordings", StaticFiles(directory=config.recordings_dir), name="recordings")

recorder = AudioRecorder()
AUDIO_PATH = config.recordings_dir / "meeting.wav"


@app.post("/start_recording")
async def start_recording() -> dict:
    """Begin capturing system audio."""
    try:
        recorder.start()
        return {"status": "recording"}
    except Exception as exc:
        console.log(f"Failed to start recording: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/stop_recording")
async def stop_recording() -> dict:
    """Stop capturing and save the WAV file."""
    try:
        path = recorder.stop(AUDIO_PATH)
        return {"status": "stopped", "audio_path": str(path)}
    except Exception as exc:
        console.log(f"Failed to stop recording: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/transcribe_and_summarize")
async def run_pipeline() -> dict:
    """Transcribe the recording and summarize it."""
    try:
        t_path, s_path = transcribe_and_summarize(AUDIO_PATH, config)
        return {
            "transcript_path": str(t_path),
            "summary_path": str(s_path),
        }
    except Exception as exc:
        console.log(f"Pipeline failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
