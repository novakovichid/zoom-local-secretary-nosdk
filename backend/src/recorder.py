"""Audio recorder using WASAPI loopback via sounddevice."""
from __future__ import annotations

import queue
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
from rich.console import Console

console = Console()


class AudioRecorder:
    """Record system audio on Windows using WASAPI loopback."""

    def __init__(self, samplerate: int = 16_000, channels: int = 1, dtype: str = "int16") -> None:
        self.samplerate = samplerate
        self.channels = channels
        self.dtype = dtype
        self._q: "queue.Queue[np.ndarray]" = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._recording = False

    def _callback(self, indata, frames, time, status):
        if status:
            console.log(f"Stream status: {status}")
        self._q.put(indata.copy())

    def start(self) -> None:
        """Begin recording system audio."""
        if self._recording:
            raise RuntimeError("Recording already in progress")

        console.log("Starting audio capture via WASAPI loopback")
        wasapi = sd.WasapiSettings(loopback=True)
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._callback,
            extra_settings=wasapi,
        )
        self._stream.start()
        self._recording = True

    def stop(self, output_file: Path) -> Path:
        """Stop recording and save the WAV file to *output_file*."""
        if not self._recording:
            raise RuntimeError("Recording has not been started")

        console.log("Stopping audio capture")
        assert self._stream is not None
        self._stream.stop()
        self._stream.close()
        self._recording = False

        frames = []
        while not self._q.empty():
            frames.append(self._q.get())

        if not frames:
            raise RuntimeError("No audio captured")

        audio = np.concatenate(frames, axis=0)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        import wave

        with wave.open(str(output_file), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(np.dtype(self.dtype).itemsize)
            wf.setframerate(self.samplerate)
            wf.writeframes(audio.tobytes())

        console.log(f"Saved recording to {output_file}")
        return output_file
