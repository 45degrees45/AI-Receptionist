# File 2: handlers/inbound_handler.py
from twilio.twiml.voice_response import VoiceResponse, Gather
from .base_handler import BaseCallHandler

class InboundCallHandler(BaseCallHandler):
    def __init__(self):
        super().__init__()
        self.greeting = "Hello, thank you for calling Cindy Cleaning Services. How may I assist you today?"

    def handle_incoming_call(self):
        response = VoiceResponse()
        response.say(self.greeting)
        gather = Gather(input='speech', action='/handle-inbound-response', timeout=3)
        response.append(gather)
        return str(response)
