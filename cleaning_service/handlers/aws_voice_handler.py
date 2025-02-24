# handlers/aws_voice_handler.py
# Version: 1.1.0 - Enhanced AWS Polly implementation
# Changes:
# - Added comprehensive error handling
# - Improved logging
# - Added voice configuration options

import boto3
import os
import base64
import logging
from botocore.exceptions import BotoCoreError, ClientError
from twilio.twiml.voice_response import VoiceResponse
from .base_voice_handler import BaseVoiceHandler

# Configure logging
logger = logging.getLogger(__name__)

class AWSVoiceHandler(BaseVoiceHandler):
    def __init__(self):
        # Validate AWS credentials
        required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required AWS environment variables: {', '.join(missing_vars)}")
            raise ValueError(f"Missing required AWS environment variables: {', '.join(missing_vars)}")

        try:
            self.polly_client = boto3.client('polly',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            logger.info("AWS Polly client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Polly client: {e}")
            raise

        # Configure voice settings
        self.voice_id = os.getenv('AWS_POLLY_VOICE_ID', 'Ruth')
        self.engine = os.getenv('AWS_POLLY_ENGINE', 'neural')
        self.output_format = 'mp3'
        
        logger.info(f"Voice handler configured with voice_id: {self.voice_id}, engine: {self.engine}")

    def generate_audio_response(self, text):
        """
        Generate audio response using AWS Polly
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            str: TwiML response string
        """
        try:
            logger.debug(f"Generating speech for text: {text[:50]}...")
            
            # Generate speech using Amazon Polly
            response = self.polly_client.synthesize_speech(
                Engine=self.engine,
                OutputFormat=self.output_format,
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
                twiml_response = VoiceResponse()
                twiml_response.play(f"data:audio/mp3;base64,{audio_base64}")
                
                logger.debug("Successfully generated audio response")
                return str(twiml_response)
            else:
                logger.error("No AudioStream in Polly response")
                return self._fallback_response(text)
            
        except (BotoCoreError, ClientError) as aws_error:
            logger.error(f"AWS Polly error: {aws_error}")
            return self._fallback_response(text)
        except Exception as e:
            logger.error(f"Unexpected error in generate_audio_response: {e}")
            return self._fallback_response(text)

    def _fallback_response(self, text):
        """
        Generate fallback TwiML response using Twilio's text-to-speech
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            str: TwiML response string
        """
        logger.info("Using fallback TTS response")
        response = VoiceResponse()
        response.say(text)
        return str(response)
