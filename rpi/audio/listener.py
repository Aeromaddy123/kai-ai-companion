import asyncio
import numpy as np
import structlog
from typing import Optional

logger = structlog.get_logger()


class AudioListener:
    def __init__(self, config: dict):
        self.config = config['audio']
        self.sample_rate = self.config['sample_rate']
        self.channels = self.config['channels']
        self.chunk_size = self.config['chunk_size']
        self.silence_threshold = 500
        self.silence_timeout = self.config.get('silence_timeout', 2.0)
        self._audio_buffer = []
        self._is_listening = False
        
        try:
            import pyaudio
            self.pyaudio = pyaudio
            self.audio = pyaudio.PyAudio()
            self.stream = None
        except ImportError:
            logger.warning("PyAudio not installed. Using mock audio.")
            self.pyaudio = None
            self.audio = None

    async def initialize(self):
        if self.audio:
            self.stream = self.audio.open(
                format=self.pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            logger.info("Audio listener initialized")

    async def listen(self) -> bytes:
        if not self.stream:
            await self.initialize()
        
        frames = []
        silence_frames = 0
        max_silence_frames = int(self.silence_timeout * self.sample_rate / self.chunk_size)
        
        self._is_listening = True
        
        while self._is_listening:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                audio_data = np.frombuffer(data, dtype=np.int16)
                if self.is_silence(audio_data):
                    silence_frames += 1
                    if silence_frames > max_silence_frames // 2:
                        break
                else:
                    silence_frames = 0
                    
            except Exception as e:
                logger.error(f"Error reading audio: {e}")
                break
        
        return b''.join(frames)

    def is_silence(self, audio_data: np.ndarray) -> bool:
        rms = np.sqrt(np.mean(audio_data.astype(float)**2))
        return rms < self.silence_threshold

    async def listen_for_seconds(self, duration: float) -> bytes:
        if not self.stream:
            await self.initialize()
        
        frames = []
        num_chunks = int(duration * self.sample_rate / self.chunk_size)
        
        for _ in range(num_chunks):
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                logger.error(f"Error reading audio: {e}")
                break
        
        return b''.join(frames)

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        logger.info("Audio listener closed")
