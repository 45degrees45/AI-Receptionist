# handlers/base_handler.py
# Version: 1.1.0 - Switched to AWS Polly from ElevenLabs
# Changes:
# - Replaced VoiceHandler with AWSVoiceHandler
# - Added debug logging configuration
# - Improved error handling

# Version: 1.1.1 - Added improved logging

from openai import OpenAI
import requests
import os
import logging
from config.voice_config import voice_config

# Configure logging
logger = logging.getLogger(__name__)

class BaseCallHandler:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": "You are a professional cleaning service receptionist. Be friendly and efficient. Focus on scheduling cleaning appointments and providing information about our cleaning services. Keep responses concise and natural."}
        ]
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url="https://api.openai.com/v1"
        )
        self.voice_handler = voice_config.get_voice_handler()
        logger.info("BaseCallHandler initialized with voice handler: %s", 
                   self.voice_handler.__class__.__name__)

    def transcribe_audio(self, audio_url):
        try:
            logger.debug("Downloading audio from URL: %s", audio_url)
            audio_response = requests.get(audio_url)
            
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_response.content)
            
            logger.debug("Transcribing audio with Whisper")
            with open("temp_audio.wav", "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            os.remove("temp_audio.wav")
            logger.info("Audio transcription completed: %s", transcript.text)
            return transcript.text
        except Exception as e:
            logger.error("Error transcribing audio: %s", str(e), exc_info=True)
            return ""

    def handle_response(self, user_input):
        try:
            logger.info("Processing user input: %s", user_input)
            
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history
            )
            ai_response = response.choices[0].message.content
            logger.debug("AI generated response: %s", ai_response)
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Generate audio response
            audio_content = self.voice_handler.generate_audio_response(ai_response)
            
            if audio_content:
                logger.debug("Successfully generated audio response")
                return ai_response
            else:
                logger.error("Failed to generate audio response")
                return "I apologize, but I'm having trouble processing your request at the moment."
                
        except Exception as e:
            logger.error("Error in handle_response: %s", str(e), exc_info=True)
            return "I apologize, but I'm having trouble processing your request at the moment."
