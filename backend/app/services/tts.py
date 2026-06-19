import asyncio
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.config import settings


@dataclass(frozen=True)
class TTSRequest:
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"
    speed: int = 100


@dataclass(frozen=True)
class TTSResult:
    audio_path: str
    duration_ms: int | None = None


class TTSProvider:
    model_name = "placeholder"
    model_version = "0"

    def generate(self, request: TTSRequest) -> TTSResult:
        raise NotImplementedError


class PlaceholderTTSProvider(TTSProvider):
    """Placeholder for the first API shape; real providers come next."""

    def generate(self, request: TTSRequest) -> TTSResult:
        raise RuntimeError("No TTS provider is configured yet")


class WindowsSapiTTSProvider(TTSProvider):
    model_name = "windows-sapi"
    model_version = "1"

    def generate(self, request: TTSRequest) -> TTSResult:
        settings.audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = settings.audio_dir / f"{uuid4()}.wav"
        rate = max(-10, min(10, round((request.speed - 100) / 10)))

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            suffix=".txt",
            delete=False,
        ) as text_file:
            text_file.write(request.text)
            text_path = Path(text_file.name)

        script = "\n".join(
            [
                "Add-Type -AssemblyName System.Speech",
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer",
                f"$synth.Rate = {rate}",
                (
                    f"$text = [System.IO.File]::ReadAllText("
                    f"'{text_path}', [System.Text.Encoding]::UTF8)"
                ),
                f"$synth.SetOutputToWaveFile('{audio_path}')",
                "$synth.Speak($text)",
                "$synth.SetOutputToNull()",
                "$synth.Dispose()",
            ]
        )

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            suffix=".ps1",
            delete=False,
        ) as script_file:
            script_file.write(script)
            script_path = Path(script_file.name)

        try:
            subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script_path),
                ],
                check=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
        finally:
            text_path.unlink(missing_ok=True)
            script_path.unlink(missing_ok=True)

        if not audio_path.exists() or audio_path.stat().st_size == 0:
            raise RuntimeError("TTS provider created an empty audio file")

        return TTSResult(audio_path=str(audio_path))


class EdgeTTSProvider(TTSProvider):
    model_name = "edge-tts"
    model_version = "12"

    CLOSING_PUNCTUATION = "\"'\u201d\u2019\uff09)]\u300b\u3011\u300d\u300f"
    QUESTION_ENDINGS = ("?", "\uff1f")
    QUESTION_PARTICLES = (
        "\u5417",
        "\u4e48",
        "\u5462",
        "\u561b",
        "\u662f\u4e0d\u662f",
        "\u6709\u6ca1\u6709",
        "\u5bf9\u4e0d\u5bf9",
        "\u597d\u4e0d\u597d",
        "\u884c\u4e0d\u884c",
    )

    def is_question(self, text: str) -> bool:
        stripped = text.strip().rstrip(self.CLOSING_PUNCTUATION)
        if stripped.endswith(self.QUESTION_ENDINGS):
            return True

        stripped_without_terminal = stripped.rstrip("\u3002.!\uff01\u2026")
        return stripped_without_terminal.endswith(self.QUESTION_PARTICLES)

    def infer_prosody(self, text: str, speed: int) -> tuple[str, str]:
        rate_delta = max(-50, min(100, speed - 100))
        pitch = "+0Hz"
        stripped = text.strip().rstrip(self.CLOSING_PUNCTUATION)

        if stripped.endswith(("!", "\uff01")):
            rate_delta += 4
            pitch = "+8Hz"
        elif stripped.endswith(("...", "\u2026")):
            rate_delta -= 6
            pitch = "-4Hz"

        rate_delta = max(-50, min(100, rate_delta))
        return f"{rate_delta:+d}%", pitch

    def generate(self, request: TTSRequest) -> TTSResult:
        import edge_tts

        settings.audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = settings.audio_dir / f"{uuid4()}.mp3"
        rate, pitch = self.infer_prosody(request.text, request.speed)

        async def save_audio() -> None:
            communicate = edge_tts.Communicate(
                request.text,
                request.voice,
                rate=rate,
                pitch=pitch,
            )
            await communicate.save(str(audio_path))

        asyncio.run(save_audio())

        if not audio_path.exists() or audio_path.stat().st_size == 0:
            raise RuntimeError("TTS provider created an empty audio file")

        return TTSResult(audio_path=str(audio_path))


default_tts_provider = EdgeTTSProvider()
