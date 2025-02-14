# handlers/base_voice_handler.py
from abc import ABC, abstractmethod

class BaseVoiceHandler(ABC):
    @abstractmethod
    def generate_audio_response(self, text):
        """Generate audio response from text.
        
        Args:
            text (str): The text to convert to speech
            
        Returns:
            str: TwiML response string
        """
        pass
