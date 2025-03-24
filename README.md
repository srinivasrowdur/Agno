# Agno API

A powerful API service for accessing AI models based on the Agno framework.

## Features

- Chat completion API
- [Streaming support](README_STREAMING.md) for real-time responses
- Multi-model support
- Docker support

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agno-api.git
   cd agno-api
   ```

2. Set your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Start the service:
   ```bash
   docker compose up -d
   ```

4. The API will be available at `http://localhost:8000`

## API Endpoints

### Chat Completion

```
POST /api/v1/chat
```

Request Body:
```json
{
  "messages": [
    {"role": "user", "content": "Hello, who are you?"}
  ],
  "model": "gpt-3.5-turbo",
  "max_tokens": 1000,
  "stream": false
}
```

For streaming implementation details, see the [Streaming Documentation](README_STREAMING.md).

## Testing

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
