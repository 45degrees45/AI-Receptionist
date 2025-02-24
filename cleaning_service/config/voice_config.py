# config/voice_config.py
# Version: 1.0.0 - Initial version with voice service configuration
# Version: 1.0.1 - Added debug mode configuration

import os
import logging
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceService(Enum):
    AWS_POLLY = "aws_polly"
    ELEVENLABS = "elevenlabs"

class VoiceConfig:
    def __init__(self):
        # Get voice service from environment variable, default to AWS Polly
        self.voice_service = VoiceService(
            os.getenv('VOICE_SERVICE', VoiceService.AWS_POLLY.value)
        )
        
        # Debug mode configuration
        self.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        
        if self.debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
            
        logger.info(f"Initialized voice config with service: {self.voice_service}")
        
    def get_voice_handler(self):
        """Factory method to get appropriate voice handler"""
        if self.voice_service == VoiceService.AWS_POLLY:
            from handlers.aws_voice_handler import AWSVoiceHandler
            return AWSVoiceHandler()
        elif self.voice_service == VoiceService.ELEVENLABS:
            from handlers.voice_handler import VoiceHandler
            return VoiceHandler()
        else:
            raise ValueError(f"Unsupported voice service: {self.voice_service}")

# Global instance
voice_config = VoiceConfig()
