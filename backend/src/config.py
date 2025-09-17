"""Configuration loader for the Zoom Local Secretary."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def _int_from_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass
class Config:
    """Application configuration."""

    asr_model_size: str = os.getenv("ASR_MODEL_SIZE", "medium")
    asr_device: str = os.getenv("ASR_DEVICE", "cpu")
    asr_compute_type: str = os.getenv("ASR_COMPUTE_TYPE", "int8")
    asr_lang: str = os.getenv("ASR_LANG", "ru")

    recordings_dir: Path = Path("recordings")
    max_recordings: int = max(1, _int_from_env("MAX_RECORDINGS", 10))


config = Config()
