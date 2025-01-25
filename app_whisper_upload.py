'''
+-------------------+        +-----------------------+        +------------------+        +------------------------+
|   Step 1: Install |        |  Step 2: Upload Audio |        |  Step 3: Pass    |        |  Step 4: Live Audio    |
|   Python Libraries|        |  File for Transcription|        |  Transcript to   |        |  Stream from ElevenLabs|
+-------------------+        |       Whisper         |        |      OpenAI      |        |                        |
|                   |        +-----------------------+        +------------------+        +------------------------+
| - openai          |                    |                             |                              |
| - elevenlabs      |                    |                             |                              |
| - mpv             |                    v                             v                              v
|                   |        +-----------------------+        +------------------+        +------------------------+
|                   |        |                       |        |                  |        |                        |
+-------------------+        |  Whisper performs     |-------->  OpenAI generates|-------->  ElevenLabs streams   |
                             |  speech-to-text       |        |  response based  |        |  response as live      |
                             |  transcription        |        |  on transcription|        |  audio to the user     |
                             |                       |        |                  |        |                        |
                             +-----------------------+        +------------------+        +------------------------+

###### Step 1: Install Python libraries ######

pip install elevenlabs==0.3.0b0
brew install mpv
pip install --upgrade openai
'''
import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import play

class AI_Assistant:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.client = ElevenLabs(api_key=self.elevenlabs_api_key)

        # Prompt
        self.full_transcript = [
            {"role":"system", "content":"You are a receptionist at a homeopathy clinic. Be resourceful and efficient."},
        ]

###### Step 2: Upload Audio File for Transcription with Whisper ######
        
    def transcribe_audio_file(self, audio_file_path):
        """
        Transcribe an uploaded audio file using OpenAI's Whisper.
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                print(f"Transcription: {transcript.text}")
                self.generate_ai_response(transcript.text)
        except Exception as e:
            print(f"Error transcribing audio file: {e}")

###### Step 3: Pass transcript to OpenAI ######
    
    def generate_ai_response(self, transcript):
        """
        Generate an AI response based on the transcribed text.
        """
        self.full_transcript.append({"role":"user", "content": transcript})
        print(f"\nPatient: {transcript}", end="\r\n")

        response = self.openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = self.full_transcript
        )

        ai_response = response.choices[0].message.content
        self.generate_audio(ai_response)

        print(f"\nReal-time transcription: ", end="\r\n")

###### Step 4: Generate audio with ElevenLabs ######
        
    def generate_audio(self, text):
        """
        Generate and play audio from the AI response using ElevenLabs.
        """
        self.full_transcript.append({"role":"assistant", "content": text})
        print(f"\nAI Receptionist: {text}")
         
        audio = self.client.generate(
            text=text,
            voice="Rachel"
        )
    
        play(audio)

# Example usage
greeting = "Thank you for calling Dr.Lalu resident consultation, chingavanam. My name is Sandy, how may I assist you?"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)

# Replace 'your_audio_file.ogg' with the path to your uploaded WhatsApp .ogg file
audio_file_path = "WhatsApp Ptt 2025-01-23 at 10.19.51 PM.ogg"
ai_assistant.transcribe_audio_file(audio_file_path)