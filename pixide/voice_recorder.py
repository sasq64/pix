import sounddevice as sd
import soundfile as sf
import numpy as np
import os
from openai import OpenAI
import tempfile
import time
from typing import Any, cast
from concurrent.futures import Future, ThreadPoolExecutor

SoundArray = np.ndarray[Any, np.dtype[np.float32]]


class VoiceToText:
    def __init__(self, api_key: str | None = None):
        """Initialize VoiceToText with optional API key"""
        self.api_key: str = api_key or self._read_openai_key()
        self.client: OpenAI = OpenAI(api_key=self.api_key)
        self._current_recording: SoundArray | None = None
        self._sample_rate: float = 16000
        self._executor = ThreadPoolExecutor(max_workers=2)

    def _read_openai_key(self) -> str:
        """Read OpenAI API key from ~/.openai.key"""
        key_path = os.path.expanduser("~/.openai.key")
        try:
            with open(key_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"OpenAI API key file not found at {key_path}")
        except Exception as e:
            raise Exception(f"Error reading API key: {e}")

    def start_recording(self, sample_rate: float = 16000) -> None:
        """Start recording audio"""
        self._sample_rate = sample_rate
        print("Recording started...")
        self._current_recording = cast(
            SoundArray,
            sd.rec(
                frames=int(60 * sample_rate),  # Record for up to 60 seconds
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            ),
        )

    def stop_recording(self) -> SoundArray:
        """Stop recording and return the audio data"""
        if self._current_recording is None:
            raise RuntimeError("No recording in progress")

        sd.stop()
        current_frames = (
            sd.get_stream().write_available
            if hasattr(sd.get_stream(), "write_available")
            else len(self._current_recording)
        )

        # Get the actual recorded data (trim to actual length)
        actual_recording = (
            self._current_recording[:current_frames]
            if current_frames < len(self._current_recording)
            else self._current_recording
        )

        print("Recording complete!")
        self._current_recording = None
        return actual_recording

    def record_audio(
        self, duration: float = 5, sample_rate: float = 16000
    ) -> SoundArray:
        """Record audio for specified duration"""
        print(f"Recording for {duration} seconds...")
        recording: SoundArray = cast(
            SoundArray,
            sd.rec(
                frames=int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            ),
        )
        _ = sd.wait()  # Wait until recording is finished
        print("Recording complete!")
        return recording

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Send audio to OpenAI for transcription"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
            return transcript.text
        except Exception as e:
            raise Exception(f"Error during transcription: {e}")

    def start_transribe(self):
        self.start_recording(16000)

    def end_transcribe(self) -> Future[str]:
        audio_data = self.stop_recording()
        sample_rate = 16000

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            sf.write(file=temp_path, data=audio_data, samplerate=sample_rate)

        # Transcribe on worker thread
        print(f"Transcribing... {temp_path}")
        future = self._executor.submit(self._transcribe_and_cleanup, temp_path)
        return future

    def _transcribe_and_cleanup(self, temp_path: str) -> str:
        """Transcribe audio and clean up temporary file"""
        try:
            transcript = self.transcribe_audio(temp_path)
            return transcript
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def main():
    vtt = VoiceToText()
    vtt.start_transribe()
    time.sleep(5)  # Record for 5 seconds
    future = vtt.end_transcribe()
    transcript = future.result()  # Wait for future and get result
    print(f"\nTranscription: {transcript}")


if __name__ == "__main__":
    main()
