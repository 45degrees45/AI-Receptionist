# File 1: handlers/base_handler.py
# handlers/base_handler.py
from openai import OpenAI
import requests
import os
from .voice_handler import VoiceHandler

class BaseCallHandler:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": "You are a professional cleaning service receptionist. Be friendly and efficient. Focus on scheduling cleaning appointments and providing information about our cleaning services."}
        ]
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url="https://api.openai.com/v1"
        )
        self.voice_handler = VoiceHandler()

    def transcribe_audio(self, audio_url):
        try:
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
            return transcript.text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""

    def handle_response(self, user_input):
        try:
            self.conversation_history.append({"role": "user", "content": user_input})
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history
            )
            ai_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Generate voice response using ElevenLabs
            return self.voice_handler.generate_audio_response(ai_response)
        except Exception as e:
            print(f"Error handling response: {e}")
            return "I apologize, but I'm having trouble processing your request at the moment."
