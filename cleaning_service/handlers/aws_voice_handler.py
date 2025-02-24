# handlers/aws_voice_handler.py
# Version: 1.2.0 - Enhanced error handling and validation
# Changes:
# - Added detailed error messages for common AWS issues
# - Improved credential validation
# - Added health check integration

import boto3
import os
import base64
import logging
from botocore.exceptions import (
    BotoCoreError, 
    ClientError,
    CredentialRetrievalError,
    InvalidRegionError
)
from twilio.twiml.voice_response import VoiceResponse
from .base_voice_handler import BaseVoiceHandler
from .aws_health_check import AWSHealthCheck

logger = logging.getLogger(__name__)

class AWSPollyError(Exception):
    """Custom exception for AWS Polly errors"""
    pass

class AWSVoiceHandler(BaseVoiceHandler):
    def __init__(self):
        # Run initial health check
        health_checker = AWSHealthCheck()
        health_status = health_checker.check_credentials()
        
        if health_status['status'] == 'error':
            logger.error(f"AWS initialization error: {health_status['message']}")
            raise AWSPollyError(health_status['message'])

        try:
            self.polly_client = boto3.client('polly',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            logger.info("AWS Polly client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Polly client: {e}")
            raise AWSPollyError(f"Failed to initialize AWS Polly client: {str(e)}")

        # Configure voice settings
        self.voice_id = os.getenv('AWS_POLLY_VOICE_ID', 'Ruth')
        self.engine = os.getenv('AWS_POLLY_ENGINE', 'neural')
        self.output_format = 'mp3'
        
        logger.info(f"Voice handler configured with voice_id: {self.voice_id}, engine: {self.engine}")

    def _handle_aws_error(self, error):
        """Handle specific AWS errors with detailed messages"""
        error_messages = {
            'AccessDeniedException': 'AWS access denied. Please check IAM permissions for Polly service.',
            'InvalidRegionException': 'Invalid AWS region specified.',
            'InvalidSampleRateException': 'Invalid sample rate for audio output.',
            'InvalidSsmlException': 'Invalid SSML in input text.',
            'LanguageNotSupportedException': 'Specified language is not supported.',
            'LexiconNotFoundException': 'Specified lexicon does not exist.',
            'ServiceFailureException': 'AWS Polly service is currently unavailable.',
            'TextLengthExceededException': 'Input text is too long.',
            'ThrottlingException': 'AWS Polly request rate exceeded.',
            'CredentialRetrievalError': 'Failed to retrieve AWS credentials.',
            'EndpointConnectionError': 'Could not connect to AWS Polly endpoint.'
        }
        
        error_code = getattr(error, 'response', {}).get('Error', {}).get('Code', error.__class__.__name__)
        error_message = error_messages.get(error_code, f'Unexpected AWS error: {str(error)}')
        
        logger.error(f"AWS Polly error: {error_code} - {error_message}")
        return error_message

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
                return self._fallback_response(text, "No audio stream received from AWS Polly")
            
        except (BotoCoreError, ClientError) as aws_error:
            error_message = self._handle_aws_error(aws_error)
            return self._fallback_response(text, error_message)
        except Exception as e:
            logger.error(f"Unexpected error in generate_audio_response: {e}")
            return self._fallback_response(text, f"Unexpected error: {str(e)}")

    def _fallback_response(self, text, error_message=""):
        """
        Generate fallback TwiML response using Twilio's text-to-speech
        
        Args:
            text (str): Text to convert to speech
            error_message (str): Error message for logging
            
        Returns:
            str: TwiML response string
        """
        logger.warning(f"Using fallback TTS response. Reason: {error_message}")
        response = VoiceResponse()
        response.say(text)
        return str(response)

    def check_health(self):
        """Run health check for AWS Polly service"""
        health_checker = AWSHealthCheck()
        return health_checker.run_all_checks()
