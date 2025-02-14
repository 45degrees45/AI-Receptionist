# handlers/aws_voice_handler.py
import boto3
import os
import base64
from twilio.twiml.voice_response import VoiceResponse

class AWSVoiceHandler:
    def __init__(self):
        self.polly_client = boto3.client('polly',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.voice_id = os.getenv('AWS_POLLY_VOICE_ID', 'Ruth')  # Default to Ruth voice

    def generate_audio_response(self, text):
        try:
            # Generate speech using Amazon Polly
            response = self.polly_client.synthesize_speech(
                Engine='neural',
                OutputFormat='mp3',
                Text=text,
                VoiceId=self.voice_id,
                TextType='text'
            )
            
            # Get the audio stream
            if "AudioStream" in response:
                # Read the audio stream
                audio = response['AudioStream'].read()
                # Convert to base64 for Twilio
                audio_base64 = base64.b64encode(audio).decode('utf-8')
                
                # Create TwiML response with the audio
                response = VoiceResponse()
                response.play(f"data:audio/mp3;base64,{audio_base64}")
                
                return str(response)
            
        except Exception as e:
            print(f"Error generating voice response with AWS Polly: {e}")
            # Fallback to default Twilio TTS
            response = VoiceResponse()
            response.say(text)
            return str(response)
