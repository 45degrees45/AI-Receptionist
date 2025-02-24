# handlers/aws_health_check.py
# Version: 1.0.0 - Initial AWS Health Check Implementation
# Author: Claude
# Date: 2025-02-24

import boto3
import os
import logging
from botocore.exceptions import (
    ClientError, 
    CredentialRetrievalError, 
    InvalidRegionError,
    TokenRetrievalError,
    EndpointConnectionError
)

logger = logging.getLogger(__name__)

class AWSHealthCheck:
    def __init__(self):
        self.required_vars = {
            'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
            'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1')
        }
        self.voice_id = os.getenv('AWS_POLLY_VOICE_ID', 'Ruth')
        self.test_text = "This is a health check test."

    def check_credentials(self):
        """Validate AWS credentials and permissions"""
        missing_vars = [key for key, value in self.required_vars.items() if not value]
        
        if missing_vars:
            return {
                'status': 'error',
                'message': f'Missing required environment variables: {", ".join(missing_vars)}',
                'details': {var: 'missing' for var in missing_vars}
            }

        try:
            # Test credential validity
            sts = boto3.client(
                'sts',
                aws_access_key_id=self.required_vars['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=self.required_vars['AWS_SECRET_ACCESS_KEY'],
                region_name=self.required_vars['AWS_REGION']
            )
            sts.get_caller_identity()
            return {
                'status': 'success',
                'message': 'AWS credentials are valid',
                'details': {
                    'region': self.required_vars['AWS_REGION'],
                    'voice_id': self.voice_id
                }
            }
        except Exception as e:
            logger.error(f"Credential validation error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Invalid AWS credentials: {str(e)}',
                'details': {'error_type': e.__class__.__name__}
            }

    def check_polly_service(self):
        """Test AWS Polly service availability and permissions"""
        try:
            polly = boto3.client(
                'polly',
                aws_access_key_id=self.required_vars['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=self.required_vars['AWS_SECRET_ACCESS_KEY'],
                region_name=self.required_vars['AWS_REGION']
            )
            
            # Test voice synthesis
            response = polly.synthesize_speech(
                Engine='neural',
                OutputFormat='mp3',
                Text=self.test_text,
                VoiceId=self.voice_id
            )
            
            if 'AudioStream' in response:
                return {
                    'status': 'success',
                    'message': 'AWS Polly service is working correctly',
                    'details': {
                        'voice_id': self.voice_id,
                        'engine': 'neural',
                        'response_code': response['ResponseMetadata']['HTTPStatusCode']
                    }
                }
            else:
                return {
                    'status': 'error',
                    'message': 'AWS Polly response missing AudioStream',
                    'details': response['ResponseMetadata']
                }
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            return {
                'status': 'error',
                'message': f'AWS Polly service error: {error_code}',
                'details': {
                    'error_code': error_code,
                    'error_message': error_message
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Unexpected error checking Polly service: {str(e)}',
                'details': {'error_type': e.__class__.__name__}
            }

    def run_all_checks(self):
        """Run all AWS health checks"""
        results = {
            'credentials': self.check_credentials(),
            'polly_service': self.check_polly_service()
        }
        
        # Overall status
        overall_status = 'success' if all(r['status'] == 'success' for r in results.values()) else 'error'
        
        return {
            'status': overall_status,
            'checks': results,
            'timestamp': logging.Formatter().converter()
        }
