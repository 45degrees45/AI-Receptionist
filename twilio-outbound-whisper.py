from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client with base configuration
openai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.openai.com/v1"
)

twilio_client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

class OutboundCallHandler:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": "You are a dental clinic receptionist. Be professional and efficient."}
        ]

    def make_call(self, to_number):
        try:
            call = twilio_client.calls.create(
                to=to_number,
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                url=f"https://{request.headers.get('Host', '')}/outbound-voice"
            )
            return call.sid
        except Exception as e:
            print(f"Error making call: {e}")
            return None

    def transcribe_audio(self, audio_url):
        try:
            # Download audio from Twilio URL
            audio_response = requests.get(audio_url)
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_response.content)
            
            # Transcribe with Whisper
            with open("temp_audio.wav", "rb") as audio_file:
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            os.remove("temp_audio.wav")
            return transcript.text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""

    def handle_response(self, user_input):
        try:
            self.conversation_history.append({"role": "user", "content": user_input})
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history
            )
            ai_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            return ai_response
        except Exception as e:
            print(f"Error handling response: {e}")
            return "I apologize, but I'm having trouble processing your request at the moment."

call_handler = OutboundCallHandler()

@app.route("/outbound-voice", methods=['POST'])
def outbound_voice():
    response = VoiceResponse()
    response.say("Hello, this is Sandy from Vancouver Dental Clinic. How may I assist you today?")
    gather = Gather(input='speech', action='/handle-response', timeout=3)
    response.append(gather)
    return str(response)

@app.route("/handle-response", methods=['POST'])
def handle_response():
    response = VoiceResponse()
    
    try:
        if 'RecordingUrl' in request.values:
            user_speech = call_handler.transcribe_audio(request.values['RecordingUrl'])
        else:
            user_speech = request.values.get('SpeechResult', '')
        
        if user_speech:
            ai_response = call_handler.handle_response(user_speech)
            response.say(ai_response)
            gather = Gather(input='speech', action='/handle-response', timeout=3)
            response.append(gather)
        else:
            response.say("I didn't catch that. Could you please repeat?")
            gather = Gather(input='speech', action='/handle-response', timeout=3)
            response.append(gather)
    except Exception as e:
        print(f"Error in handle_response: {e}")
        response.say("I apologize, but I'm having trouble processing your request at the moment.")
    
    return str(response)

@app.route("/make-call", methods=['POST'])
def initiate_call():
    phone_number = request.json.get('phone_number')
    if not phone_number:
        return {"error": "Phone number required"}, 400
    
    call_sid = call_handler.make_call(phone_number)
    if call_sid:
        return {"status": "success", "call_sid": call_sid}
    return {"error": "Failed to make call"}, 500

if __name__ == "__main__":
    app.run(debug=True)
