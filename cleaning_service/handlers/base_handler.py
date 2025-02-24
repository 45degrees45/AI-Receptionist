# handlers/base_handler.py
# Version: 1.1.0 - Switched to AWS Polly from ElevenLabs
# Changes:
# - Replaced VoiceHandler with AWSVoiceHandler
# - Added debug logging configuration
# - Improved error handling

from openai import OpenAI
import requests
import os
import logging
from .aws_voice_handler import AWSVoiceHandler

# Global debug flag
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        self.voice_handler = AWSVoiceHandler()
        logger.info("BaseCallHandler initialized with AWS Polly voice handler")

    def transcribe_audio(self, audio_url):
        try:
            logger.debug(f"Attempting to transcribe audio from URL: {audio_url}")
            
            # Download audio from Twilio URL
            audio_response = requests.get(audio_url)
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_response.content)
            
            # Transcribe with Whisper
            with open("temp_audio.wav", "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            os.remove("temp_audio.wav")
            
            logger.debug(f"Successfully transcribed audio: {transcript.text}")
            return transcript.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""

    def handle_response(self, user_input):
        try:
            logger.debug(f"Processing user input: {user_input}")
            
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history
            )
            ai_response = response.choices[0].message.content
            logger.debug(f"AI generated response: {ai_response}")
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Generate audio response using AWS Polly
            twiml_response = self.voice_handler.generate_audio_response(ai_response)
            
            if twiml_response:
                logger.debug("Successfully generated AWS Polly audio response")
                return ai_response
            else:
                logger.error("Failed to generate AWS Polly audio response")
                return "I apologize, but I'm having trouble processing your request at the moment."
                
        except Exception as e:
            logger.error(f"Error in handle_response: {e}")
            return "I apologize, but I'm having trouble processing your request at the moment."
