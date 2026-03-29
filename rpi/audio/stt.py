import asyncio
import structlog
import numpy as np
from typing import Optional

logger = structlog.get_logger()


class SpeechToText:
    def __init__(self, config: dict):
        self.config = config
        self.sample_rate = config['audio']['sample_rate']
        self.model = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        
        try:
            from vosk import Model, KaldiRecognizer
            model_path = "models/vosk-model-small-en-us-0.15"
            
            if not self._check_model_exists(model_path):
                logger.warning(f"Vosk model not found at {model_path}. Using mock STT.")
                self._initialized = True
                return
            
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            logger.info("Vosk STT model loaded")
            
        except ImportError:
            logger.warning("Vosk not installed. Using mock STT.")
        except Exception as e:
            logger.warning(f"Could not load Vosk model: {e}. Using mock STT.")
        
        self._initialized = True

    def _check_model_exists(self, path: str) -> bool:
        from pathlib import Path
        model_path = Path(path)
        return model_path.exists() and (model_path / "am").exists()

    async def transcribe(self, audio_data: bytes) -> Optional[str]:
        if not self._initialized:
            await self.initialize()
        
        if not self.model:
            return await self._mock_transcribe(audio_data)
        
        try:
            import wave
            
            self.recognizer.Reset()
            self.recognizer.AcceptWaveform(audio_data)
            
            result = self.recognizer.FinalResult()
            import json
            result_dict = json.loads(result)
            
            text = result_dict.get("text", "").strip()
            if text:
                logger.info(f"Transcribed: {text}")
            return text
            
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None

    async def _mock_transcribe(self, audio_data: bytes) -> Optional[str]:
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_array.astype(float)**2))
        
        if rms > 500:
            logger.debug("Mock STT: Audio detected but no model available")
            return "I heard you but cannot transcribe without a model"
        return None

    async def transcribe_file(self, file_path: str) -> Optional[str]:
        try:
            import wave
            
            with wave.open(file_path, "rb") as wf:
                audio_data = wf.readframes(wf.getnframes())
                return await self.transcribe(audio_data)
        except Exception as e:
            logger.error(f"Error transcribing file: {e}")
            return None
