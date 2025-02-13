# File 4: app.py

from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from handlers.inbound_handler import InboundCallHandler
from handlers.outbound_handler import OutboundCallHandler
from dotenv import load_dotenv
import traceback

load_dotenv()

app = Flask(__name__)

inbound_handler = InboundCallHandler()
outbound_handler = OutboundCallHandler()

@app.route("/inbound-voice", methods=['POST'])
def inbound_voice():
    return inbound_handler.handle_incoming_call()

@app.route("/outbound-voice", methods=['POST'])
def outbound_voice():
    return outbound_handler.handle_outbound_call()

@app.route("/handle-inbound-response", methods=['POST'])
def handle_inbound_response():
    return handle_response(inbound_handler)

@app.route("/handle-outbound-response", methods=['POST'])
def handle_outbound_response():
    return handle_response(outbound_handler)

def handle_response(handler):
    response = VoiceResponse()
    try:
        print("Starting response handling")
        print("Request values:", request.values)
        
        if 'RecordingUrl' in request.values:
            print(f"Processing recording from URL: {request.values['RecordingUrl']}")
            user_speech = handler.transcribe_audio(request.values['RecordingUrl'])
        else:
            user_speech = request.values.get('SpeechResult', '')
            print(f"Direct speech result: {user_speech}")
        
        if user_speech:
            print("Processing user speech")
            ai_response = handler.handle_response(user_speech)
            print(f"AI response: {ai_response}")
            response.say(ai_response)
            action = '/handle-inbound-response' if isinstance(handler, InboundCallHandler) else '/handle-outbound-response'
            gather = Gather(input='speech', action=action, timeout=10)
            response.append(gather)
        else:
            print("No speech detected")
            response.say("I didn't catch that. Could you please repeat?")
            action = '/handle-inbound-response' if isinstance(handler, InboundCallHandler) else '/handle-outbound-response'
            gather = Gather(input='speech', action=action, timeout=10)
            response.append(gather)
    except Exception as e:
        print(f"Error in handle_response: {e}")
        print("Full traceback:", traceback.format_exc())
        response.say("I apologize, but I'm having trouble processing your request at the moment.")
        response.hangup()
    
    return str(response)

@app.route("/make-call", methods=['POST'])
def initiate_call():
    phone_number = request.json.get('phone_number')
    if not phone_number:
        return {"error": "Phone number required"}, 400
    
    host = request.headers.get('Host', '')
    call_sid = outbound_handler.make_call(phone_number, host)
    if call_sid:
        return {"status": "success", "call_sid": call_sid}
    return {"error": "Failed to make call"}, 500

@app.route("/healthz", methods=['GET'])
def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    app.run(debug=True)
