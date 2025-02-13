# handlers/voice_handler.py
from elevenlabs.client import ElevenLabs
import os
import base64

class VoiceHandler:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'JBFqnCBsd6RMkjVDRZzb')  # Default voice ID
        
    def generate_audio_response(self, text):
        try:
            print("Attempting to generate audio with text:", text)
            
            # Generate audio using ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            # Convert generator to bytes
            audio_content = b''.join(chunk for chunk in audio_generator)
            
            print(f"Successfully generated audio of size: {len(audio_content)} bytes")
            
            # For debugging, save the audio file locally
            with open("test_response.mp3", "wb") as f:
                f.write(audio_content)
            
            return audio_content
            
        except Exception as e:
            print(f"Error in generate_audio_response: {e}")
            return None
