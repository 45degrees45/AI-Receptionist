# File 3: handlers/outbound_handler.py
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from .base_handler import BaseCallHandler
import os

class OutboundCallHandler(BaseCallHandler):
    def __init__(self):
        super().__init__()
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'), 
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.greeting = "Hello, this is calling from Cindy Cleaning Services. How may I assist you today?"

    def make_call(self, to_number, host):
        try:
            call = self.twilio_client.calls.create(
                to=to_number,
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                url=f"https://{host}/outbound-voice"
            )
            return call.sid
        except Exception as e:
            print(f"Error making call: {e}")
            return None

    def handle_outbound_call(self):
        response = VoiceResponse()
        response.say(self.greeting)
        gather = Gather(input='speech', action='/handle-outbound-response', timeout=3)
        response.append(gather)
        return str(response)