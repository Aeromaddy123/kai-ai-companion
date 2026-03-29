import asyncio
import base64
import structlog
from typing import Optional

logger = structlog.get_logger()


class TTSPlayer:
    def __init__(self, config: dict):
        self.config = config
        self.server_host = config['server']['host']
        self.server_port = config['server']['port']
        self.base_url = f"http://{self.server_host}:{self.server_port}"

    async def speak(self, text: str) -> bool:
        if not text:
            return False
        
        logger.info(f"Speaking: {text}")
        
        try:
            audio_data = await self._get_tts_audio(text)
            if audio_data:
                await self._play_audio(audio_data)
                return True
            else:
                logger.warning("No audio data received from TTS")
                return False
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False

    async def _get_tts_audio(self, text: str) -> Optional[bytes]:
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tts",
                    json={"text": text},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"TTS request failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting TTS audio: {e}")
            return None

    async def _play_audio(self, audio_data: bytes):
        try:
            import pyaudio
            import wave
            import io
            
            audio = pyaudio.PyAudio()
            
            wav_file = io.BytesIO(audio_data)
            with wave.open(wav_file, 'rb') as wf:
                stream = audio.open(
                    format=audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                stream.stop_stream()
                stream.close()
            
            audio.terminate()
            
        except ImportError:
            logger.warning("PyAudio not available for playback")
        except Exception as e:
            logger.error(f"Audio playback error: {e}")

    async def speak_streaming(self, text: str):
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    'POST',
                    f"{self.base_url}/tts/stream",
                    json={"text": text},
                    timeout=60.0
                ) as response:
                    if response.status_code == 200:
                        import pyaudio
                        audio = pyaudio.PyAudio()
                        
                        stream = audio.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=22050,
                            output=True
                        )
                        
                        async for chunk in response.aiter_bytes(chunk_size=1024):
                            if chunk:
                                stream.write(chunk)
                        
                        stream.stop_stream()
                        stream.close()
                        audio.terminate()
                        
        except Exception as e:
            logger.error(f"Streaming TTS error: {e}")
