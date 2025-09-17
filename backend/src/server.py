"""FastAPI server for Zoom Local Secretary."""
from __future__ import annotations

import json
from pathlib import Path


import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rich.console import Console

from .config import config
from .recorder import AudioRecorder
from .pipeline import transcribe

console = Console()
app = FastAPI(title="Zoom Local Secretary")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recorder = AudioRecorder()


class RecordingManager:
    """Manage cyclic storage of recorded audio and transcripts."""

    def __init__(self, directory: Path, limit: int, prefix: str = "meeting") -> None:
        self.directory = directory
        self.limit = max(1, limit)
        self.prefix = prefix
        self.state_file = self.directory / ".state.json"
        self.directory.mkdir(parents=True, exist_ok=True)
        self._next_index = 0
        self._latest_index: int | None = None
        self._load_state()

    def _load_state(self) -> None:
        if not self.state_file.exists():
            return
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return

        next_index = data.get("next_index")
        if isinstance(next_index, int):
            self._next_index = next_index % self.limit

        latest_index = data.get("latest_index")
        if isinstance(latest_index, int):
            self._latest_index = latest_index % self.limit

    def _save_state(self) -> None:
        data = {"next_index": self._next_index}
        if self._latest_index is not None:
            data["latest_index"] = self._latest_index
        self.state_file.write_text(json.dumps(data), encoding="utf-8")

    def _path_for_index(self, index: int, suffix: str) -> Path:
        return self.directory / f"{self.prefix}_{index + 1:02d}.{suffix}"

    def prepare_audio_path(self) -> Path:
        """Return the path for the next recording without updating state."""

        return self._path_for_index(self._next_index, "wav")

    def commit_recording(self) -> Path:
        """Finalize the latest recording and advance the cyclic index."""

        idx = self._next_index
        transcript_path = self._path_for_index(idx, "txt")
        if transcript_path.exists():
            transcript_path.unlink()

        self._latest_index = idx
        self._next_index = (idx + 1) % self.limit
        self._save_state()
        return self._path_for_index(idx, "wav")

    def latest_audio_path(self) -> Path:
        """Return the most recently finalized recording."""

        if self._latest_index is None:
            raise RuntimeError("No recordings available")

        path = self._path_for_index(self._latest_index, "wav")
        if not path.exists():
            raise RuntimeError("Latest recording file is missing")
        return path

    def transcript_path_for(self, audio_path: Path) -> Path:
        """Return the transcript path corresponding to *audio_path*."""

        return audio_path.with_suffix(".txt")


recording_manager = RecordingManager(
    config.recordings_dir, config.max_recordings
)


@app.post("/api/start_recording")
async def start_recording() -> dict:
    """Begin capturing system audio."""
    try:
        recorder.start()
        return {"status": "recording"}
    except Exception as exc:
        console.log(f"Failed to start recording: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/stop_recording")
async def stop_recording() -> dict:
    """Stop capturing and save the WAV file."""
    try:
        audio_path = recording_manager.prepare_audio_path()
        path = recorder.stop(audio_path)
        recording_manager.commit_recording()
        return {"status": "stopped", "audio_path": str(path)}
    except Exception as exc:
        console.log(f"Failed to stop recording: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/transcribe")
async def run_pipeline() -> dict:
    """Transcribe the recording."""
    try:
        audio_path = recording_manager.latest_audio_path()
        transcript_path = recording_manager.transcript_path_for(audio_path)
        t_path = transcribe(audio_path, config, transcript_path=transcript_path)
        return {"transcript_path": str(t_path)}
    except Exception as exc:
        console.log(f"Pipeline failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# Upload and transcribe arbitrary audio files
@app.post("/api/transcribe_file")
async def transcribe_file(file: UploadFile = File(...)) -> dict:
    """Upload an audio file and transcribe it."""
    try:
        upload_path = config.recordings_dir / file.filename
        with upload_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        transcript_path = recording_manager.transcript_path_for(upload_path)
        t_path = transcribe(upload_path, config, transcript_path=transcript_path)
        return {"transcript_path": str(t_path)}
    except Exception as exc:
        console.log(f"File transcription failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# Serve recordings and frontend assets
app.mount("/recordings", StaticFiles(directory=config.recordings_dir), name="recordings")
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

