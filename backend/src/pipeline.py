"""Transcription pipeline."""
from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel
from rich.console import Console

from .config import Config

console = Console()


def _format_ts(seconds: float) -> str:
    """Format seconds as ``HH:MM:SS``."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def transcribe(
    audio_path: Path, cfg: Config, *, transcript_path: Path | None = None
) -> Path:
    """Transcribe *audio_path* and save the result to a text file.

    Each line of the transcript contains the segment index, start and end
    timestamps, and the recognized text.
    """
    if transcript_path is None:
        transcript_path = cfg.recordings_dir / "transcript.txt"

    console.log("Loading ASR model")
    model = WhisperModel(
        cfg.asr_model_size,
        device=cfg.asr_device,
        compute_type=cfg.asr_compute_type,
    )

    segments, _ = model.transcribe(str(audio_path), language=cfg.asr_lang)
    lines: list[str] = []
    for i, seg in enumerate(segments, 1):
        start = _format_ts(seg.start)
        end = _format_ts(seg.end)
        text = seg.text.strip()
        lines.append(f"[{i} {start}-{end}] {text}")

    transcript_path.write_text("\n".join(lines), encoding="utf-8")
    console.log(f"Transcript saved to {transcript_path}")
    return transcript_path
