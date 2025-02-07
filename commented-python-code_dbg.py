# Line 1
# In C/C++, you would use #include for imports
# Python uses 'import' or 'from ... import' statements which are similar to #include
from flask import Flask, request              # Line 4
from twilio.rest import Client               # Line 5
from twilio.twiml.voice_response import VoiceResponse, Gather  # Line 6
from openai import OpenAI                    # Line 7
import os                                    # Line 8
from dotenv import load_dotenv               # Line 9
import logging  # Import logging for debug statements # Line 10
import inspect  # For getting line numbers in debug prints # Line 11

# Line 12 - Configure logging (similar to setting up debug output in C++)
def debug_print(message):
    # Get the caller's frame
    caller_frame = inspect.currentframe().f_back
    # Get line number
    line_no = caller_frame.f_lineno
    logger.debug(f"[Line {line_no}] {message}")

# Configure logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [Line %(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)  # Line 17

debug_print("Starting application initialization")  # Line 19

# Load environment variables from .env file
load_dotenv()  # Line 22
logger.debug("Environment variables loaded")  # Line 23

# Initialize Flask application
app = Flask(__name__)  # Line 26
logger.debug("Flask app initialized")  # Line 27

# Initialize API clients with authentication
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Line 30
twilio_client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))  # Line 31
logger.debug("API clients initialized")  # Line 32

class OutboundCallHandler:  # Line 34
    def __init__(self):  # Line 35
        logger.debug("Initializing OutboundCallHandler")  # Line 36
        self.conversation_history = [
            {"role": "system", "content": "You are a dental clinic receptionist. Be professional and efficient."}
        ]  # Line 39
        logger.debug(f"Conversation history initialized with system prompt")  # Line 40

    def make_call(self, to_number):  # Line 42
        logger.debug(f"Attempting to make call to: {to_number}")  # Line 43
        try:
            call = twilio_client.calls.create(
                to=to_number,
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                url="https://d502-116-68-102-4.ngrok-free.app/outbound-voice"
            )  # Line 49
            logger.debug(f"Call successfully initiated with SID: {call.sid}")  # Line 50
            return call.sid
        except Exception as e:
            logger.error(f"Error making call: {e}")  # Line 53
            return None

    def transcribe_audio(self, audio_url):  # Line 56
        logger.debug(f"Starting audio transcription from URL: {audio_url}")  # Line 57
        try:
            # Download audio file
            logger.debug("Downloading audio file")  # Line 60
            audio_response = requests.get(audio_url)  # Line 61
            
            with open("temp_audio.wav", "wb") as f:  # Line 63
                f.write(audio_response.content)
            logger.debug("Audio file saved temporarily")  # Line 65
            
            # Transcribe audio
            logger.debug("Starting Whisper transcription")  # Line 68
            with open("temp_audio.wav", "rb") as audio_file:  # Line 69
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )  # Line 73
            
            logger.debug("Audio transcription completed")  # Line 75
            os.remove("temp_audio.wav")  # Line 76
            logger.debug("Temporary audio file removed")  # Line 77
            
            return transcript.text
        except Exception as e:
            logger.error(f"Error in transcription: {e}")  # Line 81
            return ""

    def handle_response(self, user_input):  # Line 84
        logger.debug(f"Handling user input: {user_input}")  # Line 85
        
        # Log conversation state before adding new input
        logger.debug(f"Current conversation history length: {len(self.conversation_history)}")  # Line 88
        
        self.conversation_history.append({"role": "user", "content": user_input})  # Line 90
        logger.debug("User input added to conversation history")  # Line 91
        
        logger.debug("Requesting response from OpenAI")  # Line 93
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.conversation_history
        )  # Line 97
        
        ai_response = response.choices[0].message.content  # Line 99
        logger.debug(f"Received AI response: {ai_response}")  # Line 100
        
        self.conversation_history.append({"role": "assistant", "content": ai_response})  # Line 102
        logger.debug("AI response added to conversation history")  # Line 103
        
        return ai_response

logger.debug("Creating global CallHandler instance")  # Line 107
call_handler = OutboundCallHandler()  # Line 108

@app.route("/outbound-voice", methods=['POST'])  # Line 110
def outbound_voice():
    logger.debug("Handling outbound voice request")  # Line 112
    logger.debug(f"Request data: {request.values}")  # Line 113
    
    response = VoiceResponse()  # Line 115
    response.say("Hello, this is Sandy from Vancouver Dental Clinic. How may I assist you today?")  # Line 116
    logger.debug("Initial greeting added to response")  # Line 117
    
    gather = Gather(input='speech', action='/handle-response', timeout=3)  # Line 119
    response.append(gather)  # Line 120
    logger.debug("Speech gathering configured")  # Line 121
    
    return str(response)

@app.route("/handle-response", methods=['POST'])  # Line 125
def handle_response():
    logger.debug("Handling response endpoint called")  # Line 127
    logger.debug(f"Request values: {request.values}")  # Line 128
    
    response = VoiceResponse()  # Line 130
    
    if 'RecordingUrl' in request.values:  # Line 132
        logger.debug("Recording URL found in request")  # Line 133
        user_speech = call_handler.transcribe_audio(request.values['RecordingUrl'])  # Line 134
        logger.debug(f"Transcribed speech: {user_speech}")  # Line 135
    else:
        logger.debug("Using direct speech result")  # Line 137
        user_speech = request.values.get('SpeechResult', '')  # Line 138
        logger.debug(f"Speech result: {user_speech}")  # Line 139
    
    if user_speech:  # Line 141
        logger.debug("Processing valid speech input")  # Line 142
        ai_response = call_handler.handle_response(user_speech)  # Line 143
        logger.debug(f"AI response generated: {ai_response}")  # Line 144
        
        response.say(ai_response)  # Line 146
        gather = Gather(input='speech', action='/handle-response', timeout=3)  # Line 147
        response.append(gather)  # Line 148
    else:
        logger.debug("No speech detected, requesting repeat")  # Line 150
        response.say("I didn't catch that. Could you please repeat?")  # Line 151
        gather = Gather(input='speech', action='/handle-response', timeout=3)  # Line 152
        response.append(gather)  # Line 153
    
    logger.debug("Returning voice response")  # Line 155
    return str(response)

@app.route("/make-call", methods=['POST'])  # Line 158
def initiate_call():
    logger.debug("Call initiation endpoint called")  # Line 160
    logger.debug(f"Request JSON: {request.json}")  # Line 161
    
    phone_number = request.json.get('phone_number')  # Line 163
    if not phone_number:
        logger.error("No phone number provided in request")  # Line 165
        return {"error": "Phone number required"}, 400
    
    logger.debug(f"Initiating call to: {phone_number}")  # Line 168
    call_sid = call_handler.make_call(phone_number)  # Line 169
    
    if call_sid:  # Line 171
        logger.debug(f"Call successfully initiated with SID: {call_sid}")  # Line 172
        return {"status": "success", "call_sid": call_sid}
    
    logger.error("Call initiation failed")  # Line 175
    return {"error": "Failed to make call"}, 500

if __name__ == "__main__":  # Line 178
    logger.debug("Starting Flask application")  # Line 179
    app.run(debug=True)  # Start the server  # Line 180
    logger.debug("Flask application shutdown")  # Line 181