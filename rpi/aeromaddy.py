#!/usr/bin/env python3
"""
AEROMADDY - Main Client Entry Point
Runs on Raspberry Pi, connects to local LLM server
"""

import asyncio
import signal
import sys
from pathlib import Path

import yaml
import structlog

from rpi.audio.listener import AudioListener
from rpi.audio.wakeword import WakeWordDetector
from rpi.audio.stt import SpeechToText
from rpi.audio.tts_player import TTSPlayer
from rpi.vision.camera import Camera
from rpi.api.client import APIClient
from rpi.utils.logger import setup_logging


class AEROMADDYClient:
    def __init__(self, config_path: str = "config/aeromaddy.yaml"):
        self.config = self._load_config(config_path)
        self.logger = setup_logging(self.config)
        self.api_client = None
        self.audio_listener = None
        self.wakeword_detector = None
        self.stt = None
        self.tts_player = None
        self.camera = None
        self.is_running = False
        self.conversation_mode = False

    def _load_config(self, config_path: str) -> dict:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    async def initialize(self):
        self.logger.info("Initializing AEROMADDY client...")

        server_config = self.config["server"]
        base_url = f"{server_config['protocol']}://{server_config['host']}:{server_config['port']}"
        self.api_client = APIClient(base_url)

        if not await self.api_client.health_check():
            self.logger.error("Server is not responding. Please check connection.")
            return False

        self.logger.info("Server connection established")

        self.audio_listener = AudioListener(self.config)
        self.stt = SpeechToText(self.config)
        self.wakeword_detector = WakeWordDetector(self.config)
        self.tts_player = TTSPlayer(self.config)

        if self.config["vision"]["enabled"]:
            self.camera = Camera(self.config)
            await self.camera.initialize()

        self.is_running = True
        self.logger.info("AEROMADDY client initialized successfully")
        return True

    async def handle_wakeword(self):
        self.logger.info("Wake word detected!")
        self.conversation_mode = True
        await self.tts_player.speak("Yes?")

        while self.conversation_mode and self.is_running:
            audio_data = await self.audio_listener.listen()

            if audio_listener.is_silence(audio_data):
                self.conversation_mode = False
                self.logger.debug("Silence detected, exiting conversation mode")
                break

            text = await self.stt.transcribe(audio_data)

            if text:
                self.logger.info(f"User said: {text}")
                await self.process_command(text)

    async def process_command(self, text: str):
        if "what do you see" in text.lower() or "describe" in text.lower():
            await self.handle_vision_query(text)
        elif "remember" in text.lower():
            await self.handle_memory_command(text)
        elif "stop" in text.lower() or "goodbye" in text.lower():
            await self.tts_player.speak("Goodbye! Have a great day!")
            self.conversation_mode = False
        else:
            await self.handle_chat(text)

    async def handle_chat(self, text: str):
        response = await self.api_client.chat(text)
        if response:
            self.logger.info(f"AEROMADDY response: {response}")
            await self.tts_player.speak(response)

    async def handle_vision_query(self, text: str):
        if not self.camera:
            await self.tts_player.speak("Camera is not available.")
            return

        image = await self.camera.capture()
        if image:
            response = await self.api_client.vision_chat(image, text)
            if response:
                await self.tts_player.speak(response)
        else:
            await self.tts_player.speak("I couldn't capture an image.")

    async def handle_memory_command(self, text: str):
        response = await self.api_client.chat(text)
        if response:
            memory_text = self._extract_memory_content(text, response)
            if memory_text:
                await self.api_client.add_memory(memory_text)
                await self.tts_player.speak("I've remembered that.")
            else:
                await self.tts_player.speak(response)

    def _extract_memory_content(self, user_input: str, response: str) -> str:
        if "remember" in user_input.lower():
            important_keywords = ["keys", "where", "put", "left", "stored", "location"]
            if any(kw in user_input.lower() for kw in important_keywords):
                return f"User said: {user_input}"
        return None

    async def run(self):
        if not await self.initialize():
            self.logger.error("Failed to initialize AEROMADDY client")
            return

        self.logger.info("AEROMADDY is ready! Say 'Hey AEROMADDY' to activate...")
        await self.tts_player.speak(
            "AEROMADDY is online. Say Hey AEROMADDY to activate."
        )

        while self.is_running:
            try:
                if self.wakeword_detector.is_available():
                    detected = await self.wakeword_detector.detect()
                    if detected:
                        await self.handle_wakeword()
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)

    def shutdown(self):
        self.logger.info("Shutting down AEROMADDY...")
        self.is_running = False
        if self.audio_listener:
            self.audio_listener.close()
        if self.camera:
            self.camera.close()
        self.logger.info("AEROMADDY shutdown complete")


async def main():
    client = AEROMADDYClient()

    def signal_handler(sig, frame):
        client.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
