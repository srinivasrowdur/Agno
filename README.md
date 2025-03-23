# Agno API

A powerful API service that provides access to AI models using the Agno framework.

## Features

- **Chat Completion**: Generate responses from AI models
- **Streaming Support**: Receive model responses in real-time as they're generated
- **Multi-Model Support**: Configure and use different AI models without changing server code
- **Docker Support**: Easy deployment using Docker

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- OpenAI API key or compatible API

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd agno
   ```

2. Set your API key:
   Create a `.env` file with your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Start the service using Docker:
   ```bash
   docker compose up -d
   ```

4. The API will be available at:
   ```
   http://localhost:8000
   ```

## API Endpoints

### Chat Completion

```
POST /api/v1/chat
```

Request body:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello! How are you?"
    }
  ],
  "max_tokens": 500,
  "model_name": "gpt-4",  // Optional
  "stream": false  // Set to true for streaming responses
}
```

## Testing

This project includes various tests to ensure functionality:

### API Tests

Test the basic API endpoints:
```bash
python tests/api/test_api.py
```

### Streaming Tests

Test the streaming functionality:
```bash
python tests/streaming/test_streaming.py
```

For a visual demonstration of streaming:
```bash
python tests/streaming/stream_test_with_delay.py
```

## Development

For local development without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## License

[Your License]

## Acknowledgements

- Built with [Agno Framework](https://github.com/agno/agno)
- Powered by OpenAI GPT models 