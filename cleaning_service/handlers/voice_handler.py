# handlers/voice_handler.py
from elevenlabs import generate, set_api_key
import os
import base64
from twilio.twiml.voice_response import VoiceResponse

class VoiceHandler:
    def __init__(self):
        # Set the API key for ElevenLabs
        set_api_key(os.getenv('ELEVENLABS_API_KEY'))
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'Rachel')
        
    def generate_audio_response(self, text):
        try:
            # Generate audio using ElevenLabs
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_monolingual_v1"
            )
            
            # Convert audio to base64 for Twilio
            audio_base64 = base64.b64encode(audio).decode('utf-8')
            
            # Create TwiML response with the audio
            response = VoiceResponse()
            response.play(f"data:audio/mp3;base64,{audio_base64}")
            
            return str(response)
            
        except Exception as e:
            print(f"Error generating voice response: {e}")
            # Fallback to default Twilio TTS
            response = VoiceResponse()
            response.say(text)
            return str(response)
