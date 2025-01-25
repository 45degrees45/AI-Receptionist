# AI-Receptionist
An AI-powered virtual receptionist that uses real-time transcription, OpenAI's GPT for response generation, and ElevenLabs for voice synthesis. This project simulates a receptionist for any business, providing efficient and natural interactions.

# AI Receptionist

An AI-powered virtual receptionist that uses real-time transcription, OpenAI's GPT for response generation, and ElevenLabs for voice synthesis. This project simulates a receptionist for any business, providing efficient and natural interactions.

---

## Features

- **Real-Time Transcription**: Uses OpenAI's Whisper for speech-to-text transcription.
- **AI Response Generation**: Leverages OpenAI's GPT-3.5-turbo to generate context-aware responses.
- **Voice Synthesis**: Utilizes ElevenLabs to convert text responses into natural-sounding speech.
- **Local Whisper Option**: Supports local Whisper model for transcription to avoid API limits.

---

## Prerequisites

Before running the project, ensure you have the following installed:

1. **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
2. **FFmpeg**: Required for audio processing.
   - On macOS: `brew install ffmpeg`
   - On Linux: `sudo apt install ffmpeg`
   - On Windows: Download from [FFmpeg's official website](https://ffmpeg.org/download.html).
3. **API Keys**:
   - OpenAI API Key: [Get OpenAI API Key](https://platform.openai.com/account/api-keys)
   - ElevenLabs API Key: [Get ElevenLabs API Key](https://elevenlabs.io/)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-receptionist.git
   cd ai-receptionist
