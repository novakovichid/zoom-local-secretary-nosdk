"""Configuration loader for the Zoom Local Secretary."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    asr_model_size: str = os.getenv("ASR_MODEL_SIZE", "medium")
    asr_device: str = os.getenv("ASR_DEVICE", "cpu")
    asr_compute_type: str = os.getenv("ASR_COMPUTE_TYPE", "int8")
    asr_lang: str = os.getenv("ASR_LANG", "ru")

    recordings_dir: Path = Path("recordings")


config = Config()
