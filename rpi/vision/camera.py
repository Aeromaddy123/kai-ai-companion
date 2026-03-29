import asyncio
import structlog
from pathlib import Path
from typing import Optional
import base64
import io

import numpy as np

logger = structlog.get_logger()


class Camera:
    def __init__(self, config: dict):
        self.config = config['vision']
        self.enabled = self.config['enabled']
        self.resolution = self.config.get('resolution', {'width': 640, 'height': 480})
        self.camera_index = self.config.get('camera_index', 0)
        self._camera = None
        self._is_streaming = False

    async def initialize(self) -> bool:
        if not self.enabled:
            logger.info("Camera is disabled in config")
            return False
        
        try:
            try:
                from picamera2 import Picamera2
                self._camera = Picamera2()
                self._camera.configure(self._camera.create_still_configuration(
                    size=(self.resolution['width'], self.resolution['height'])
                ))
                self._camera.start()
                logger.info("Picamera2 initialized")
                return True
                
            except ImportError:
                logger.info("Picamera2 not available, trying OpenCV")
                
                import cv2
                self._camera = cv2.VideoCapture(self.camera_index)
                
                if self._camera.isOpened():
                    self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution['width'])
                    self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution['height'])
                    logger.info(f"OpenCV camera initialized (index {self.camera_index})")
                    return True
                else:
                    logger.error("Could not open camera")
                    return False
                    
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False

    async def capture(self) -> Optional[str]:
        if not self._camera:
            if not await self.initialize():
                return None
        
        try:
            try:
                from picamera2 import Picamera2
                if isinstance(self._camera, Picamera2):
                    buffer = io.BytesIO()
                    self._camera.capture_file(buffer, format='jpeg')
                    buffer.seek(0)
                    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    return image_base64
                    
            except ImportError:
                import cv2
                if isinstance(self._camera, cv2.VideoCapture):
                    ret, frame = self._camera.read()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        image_base64 = base64.b64encode(buffer).decode('utf-8')
                        return image_base64
                        
        except Exception as e:
            logger.error(f"Capture error: {e}")
            return None
        
        return None

    async def capture_file(self, path: str) -> bool:
        try:
            image_base64 = await self.capture()
            if image_base64:
                import base64
                image_data = base64.b64decode(image_base64)
                with open(path, 'wb') as f:
                    f.write(image_data)
                logger.info(f"Image saved to {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False

    async def start_stream(self, fps: int = 5):
        self._is_streaming = True
        logger.info(f"Starting camera stream at {fps} FPS")
        
        while self._is_streaming:
            try:
                frame = await self.capture()
                if frame:
                    yield frame
                await asyncio.sleep(1 / fps)
            except Exception as e:
                logger.error(f"Stream error: {e}")
                break

    def stop_stream(self):
        self._is_streaming = False
        logger.info("Camera stream stopped")

    def close(self):
        self._is_streaming = False
        try:
            try:
                from picamera2 import Picamera2
                if isinstance(self._camera, Picamera2):
                    self._camera.close()
            except ImportError:
                import cv2
                if isinstance(self._camera, cv2.VideoCapture):
                    self._camera.release()
        except Exception as e:
            logger.error(f"Error closing camera: {e}")
        logger.info("Camera closed")
