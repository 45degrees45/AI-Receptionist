# handlers/voice_handler.py
from elevenlabs.client import ElevenLabs
import os
import base64
from twilio.twiml.voice_response import VoiceResponse

class VoiceHandler:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')  # Default voice ID
        
    def generate_audio_response(self, text):
        try:
            # Generate audio using ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            # Convert generator to bytes
            audio_content = b''.join(chunk for chunk in audio_generator)
            
            # Convert audio to base64 for Twilio
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # Create TwiML response with the audio
            response = VoiceResponse()
            
            try:
                response.play(f"data:audio/mp3;base64,{audio_base64}")
            except Exception as e:
                print(f"Error playing audio: {e}")
                # Fallback to standard TTS if play fails
                response.say(text)
            
            # Add gather for next input
            gather = response.gather(
                input='speech',
                timeout=3
            )
            
            return str(response)
            
        except Exception as e:
            print(f"Error generating voice response: {e}")
            # Fallback to default Twilio TTS
            response = VoiceResponse()
            response.say(text)
            
            # Add gather for next input
            gather = response.gather(
                input='speech',
                timeout=3
            )
            
            return str(response)
