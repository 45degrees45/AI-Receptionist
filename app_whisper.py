'''
+-------------------+        +-----------------------+        +------------------+        +------------------------+
|   Step 1: Install |        |  Step 2: Real-Time    |        |  Step 3: Pass    |        |  Step 4: Live Audio    |
|   Python Libraries|        |  Transcription with   |        |  Real-Time       |        |  Stream from ElevenLabs|
+-------------------+        |       Whisper         |        |  Transcript to   |        |                        |
|                   |        +-----------------------+        |      OpenAI      |        +------------------------+
| - openai          |                    |                    +------------------+                    |
| - elevenlabs      |                    |                             |                              |
| - mpv             |                    v                             v                              v
| - portaudio       |        +-----------------------+        +------------------+        +------------------------+
| - pyaudio         |        |                       |        |                  |        |                        |
+-------------------+        |  Whisper performs     |-------->  OpenAI generates|-------->  ElevenLabs streams   |
                             |  real-time speech-to- |        |  response based  |        |  response as live      |
                             |  text transcription   |        |  on transcription|        |  audio to the user     |
                             |                       |        |                  |        |                        |
                             +-----------------------+        +------------------+        +------------------------+

###### Step 1: Install Python libraries ######

brew install portaudio
pip install pyaudio
pip install elevenlabs==0.3.0b0
brew install mpv
pip install --upgrade openai
'''
import os
from dotenv import load_dotenv
load_dotenv()

import pyaudio
import wave
import openai
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import play

class AI_Assistant:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.client = ElevenLabs(api_key=self.elevenlabs_api_key)
        self.audio = pyaudio.PyAudio()

        # Prompt
        self.full_transcript = [
            {"role":"system", "content":"You are a receptionist at a dental clinic. Be resourceful and efficient."},
        ]

###### Step 2: Real-Time Transcription with Whisper ######
        
    def start_transcription(self):
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=16000,
                                      input=True,
                                      frames_per_buffer=1024)
        print("Recording...")

        frames = []
        try:
            while True:
                data = self.stream.read(1024)
                frames.append(data)
        except KeyboardInterrupt:
            print("Recording stopped.")

        self.stream.stop_stream()
        self.stream.close()

        wf = wave.open("output.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()

        with open("output.wav", "rb") as audio_file:
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            self.generate_ai_response(transcript.text)

    def stop_transcription(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

###### Step 3: Pass real-time transcript to OpenAI ######
    
    def generate_ai_response(self, transcript):

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

        self.full_transcript.append({"role":"assistant", "content": text})
        print(f"\nAI Receptionist: {text}")
         
        audio = self.client.generate(
        text=text,
        voice="Rachel"
         )
    
        play(audio)

greeting = "Thank you for calling Vancouver dental clinic. My name is Sandy, how may I assist you?"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()