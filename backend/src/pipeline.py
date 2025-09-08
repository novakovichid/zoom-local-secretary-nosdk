"""Transcription and summarization pipeline."""
from __future__ import annotations

from pathlib import Path

import requests
from faster_whisper import WhisperModel
from rich.console import Console

from .config import Config

console = Console()


def transcribe_and_summarize(audio_path: Path, cfg: Config) -> tuple[Path, Path]:
    """Run ASR and summarization on *audio_path*.

    Returns paths to transcript and summary files.
    """
    transcript_path = cfg.recordings_dir / "transcript.txt"
    summary_path = cfg.recordings_dir / "summary.md"

    console.log("Loading ASR model")
    model = WhisperModel(
        cfg.asr_model_size,
        device=cfg.asr_device,
        compute_type=cfg.asr_compute_type,
    )

    segments, _ = model.transcribe(str(audio_path), language=cfg.asr_lang)
    transcript = " ".join(seg.text.strip() for seg in segments)
    transcript_path.write_text(transcript, encoding="utf-8")
    console.log(f"Transcript saved to {transcript_path}")

    prompt = "Сделай краткое резюме встречи:\n" + transcript
    payload = {
        "model": cfg.lm_model,
        "messages": [{"role": "user", "content": prompt}],
    }
    url = cfg.lm_base_url.rstrip("/") + "/chat/completions"

    console.log(f"Requesting summary from {url}")
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        summary = data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # pragma: no cover - network errors
        console.log(f"Summarization failed: {exc}")
        raise

    summary_path.write_text(summary, encoding="utf-8")
    console.log(f"Summary saved to {summary_path}")

    return transcript_path, summary_path
