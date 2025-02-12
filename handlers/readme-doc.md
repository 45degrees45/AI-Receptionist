# AI-Powered Cleaning Service Call Handler

A Flask-based application that handles both inbound and outbound calls for Cindy Cleaning Services using Twilio, OpenAI's GPT-3.5, and Whisper API. The system acts as an intelligent receptionist capable of handling customer inquiries about cleaning services, scheduling appointments, and providing service information through voice interactions.

## Features

- Handles both inbound and outbound voice calls
- Speech-to-text conversion using OpenAI's Whisper API
- Natural language processing using GPT-3.5
- Professional cleaning service receptionist responses
- Automatic call routing and handling
- Health check endpoint for deployment monitoring

## Prerequisites

- Python 3.8+
- Twilio Account
- OpenAI API Access
- Valid domain/ngrok for Twilio webhook URLs

## Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd cleaning-service-call-handler
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
project_root/
├── app.py                 # Main Flask application
├── handlers/              # Handler modules directory
│   ├── __init__.py
│   ├── base_handler.py    # Base functionality for call handling
│   ├── inbound_handler.py # Inbound call handler
│   └── outbound_handler.py# Outbound call handler
├── requirements.txt       # Project dependencies
└── .env                  # Environment variables
```

## API Endpoints

### Voice Endpoints

- `POST /inbound-voice`: Handles incoming calls
- `POST /outbound-voice`: Handles outgoing calls
- `POST /handle-inbound-response`: Processes inbound call responses
- `POST /handle-outbound-response`: Processes outbound call responses

### Control Endpoints

- `POST /make-call`: Initiates an outbound call
  - Request body: `{"phone_number": "+1234567890"}`
- `GET /healthz`: Health check endpoint

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Make an outbound call:
```bash
curl -X POST http://localhost:5000/make-call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

## Development Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up ngrok for local development:
```bash
ngrok http 5000
```

3. Update your Twilio webhook URLs with the ngrok URL

## Error Handling

The application includes comprehensive error handling for:
- Failed API calls
- Audio transcription errors
- Invalid phone numbers
- Network issues
- Missing environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

## Support

For support, please [contact information or link to issues]