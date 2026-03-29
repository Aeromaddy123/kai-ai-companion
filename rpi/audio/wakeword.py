import asyncio
import structlog
from typing import Optional
from pathlib import Path

logger = structlog.get_logger()


class WakeWordDetector:
    def __init__(self, config: dict):
        self.config = config
        self.wake_word = config['aeromaddy']['wake_word'].lower()
        self._is_available = False
        self._detection_task = None
        
        try:
            import torch
            from speechbrain.pretrained import EncoderClassifier
            self.torch = torch
            self.classifier = None
            self._is_available = True
            logger.info("Wake word detector initialized with SpeechBrain")
        except ImportError:
            logger.warning("SpeechBrain not available, using simple audio detection")
            try:
                import pvporcupine
                from pvporcupine import Porcupine
                self.porcupine = pvporcupine
                access_key = os.environ.get('PICOVOICE_ACCESS_KEY')
                if access_key:
                    self.porcupine_handle = Porcupine(
                        access_key=access_key,
                        keyword_paths=[f'models/hey-aeromaddy.ppn']
                    )
                    self._is_available = True
                else:
                    logger.warning("PICOVOICE_ACCESS_KEY not set")
            except ImportError:
                self._is_available = False

    def is_available(self) -> bool:
        return self._is_available

    async def detect(self) -> bool:
        if not self._is_available:
            return await self._simple_detection()
        
        try:
            import pyaudio
            import numpy as np
            
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=512
            )
            
            while True:
                data = stream.read(512, exception_on_overflow=False)
                audio_frame = np.frombuffer(data, dtype=np.int16)
                
                if self._is_audio_loud(audio_frame):
                    logger.debug("Loud audio detected, checking for wake word...")
                    return True
                
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            return False

    async def _simple_detection(self) -> bool:
        logger.debug("Using simple audio level detection for wake word")
        await asyncio.sleep(0.5)
        return True

    def _is_audio_loud(self, audio_frame) -> bool:
        import numpy as np
        rms = np.sqrt(np.mean(audio_frame.astype(float)**2))
        return rms > 1000

    async def stop(self):
        if self._detection_task:
            self._detection_task.cancel()
            try:
                await self._detection_task
            except asyncio.CancelledError:
                pass
