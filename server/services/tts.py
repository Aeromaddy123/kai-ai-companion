import asyncio
import io
import structlog
import subprocess
from pathlib import Path

logger = structlog.get_logger()


class TTSService:
    def __init__(self, config: dict):
        self.config = config
        self.voices_dir = Path("voices")
        self.default_voice = config.get('kai', {}).get('voice', 'default')
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        
        if self.voices_dir.exists():
            voices = list(self.voices_dir.glob("*.onnx"))
            logger.info(f"Found {len(voices)} voice models")
        else:
            logger.warning(f"Voices directory not found: {self.voices_dir}")
        
        self._initialized = True
        logger.info("TTS service initialized")

    async def speak(self, text: str, voice: str = None) -> bytes:
        voice = voice or self.default_voice
        
        try:
            audio_data = await self._generate_with_piper(text, voice)
            return audio_data
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return await self._fallback_tts(text)

    async def _generate_with_piper(self, text: str, voice: str) -> bytes:
        voice_model = self.voices_dir / f"{voice}.onnx"
        
        if not voice_model.exists():
            voice_model = self.voices_dir / "default.onnx"
        
        if not voice_model.exists():
            raise FileNotFoundError(f"Voice model not found: {voice}")
        
        process = await asyncio.create_subprocess_exec(
            'piper',
            '--model', str(voice_model),
            '--output_file', '-',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate(input=text.encode())
        
        if process.returncode != 0:
            raise RuntimeError(f"Piper failed: {stderr.decode()}")
        
        import wave
        
        raw_audio = stdout
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(22050)
            wf.writeframes(raw_audio)
        
        return wav_buffer.getvalue()

    async def _fallback_tts(self, text: str) -> bytes:
        logger.warning("Using fallback TTS (silent audio)")
        
        import wave
        import math
        
        duration = min(len(text) * 0.05, 5.0)
        sample_rate = 22050
        
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            
            num_samples = int(duration * sample_rate)
            silence = bytes(num_samples * 2)
            wf.writeframes(silence)
        
        return wav_buffer.getvalue()

    async def close(self):
        logger.info("TTS service closed")
