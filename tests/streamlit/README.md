# Agno API Streamlit Test App

This directory contains a Streamlit application for testing the Agno API's chat functionality.

## Features

- Interactive chat interface
- Support for both streaming and non-streaming responses
- Model selection (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
- Adjustable max token parameter
- Connection testing
- Response time tracking

## Requirements

- Python 3.11+
- Streamlit
- Requests
- sseclient-py

## How to Run

Make sure the Agno API is running locally (typically on port 8000) before starting the Streamlit app.

1. Navigate to the project root directory
2. Activate your virtual environment (if using one)
3. Run the Streamlit app:

```bash
streamlit run tests/streamlit/test_chat_app.py
```

The app will be available at http://localhost:8501 by default.

## Usage Instructions

1. Use the sidebar to configure:
   - Which model to use
   - Whether to enable streaming
   - Maximum number of tokens to generate

2. You can test the API connection using the "Test Connection" button

3. Type messages in the chat input and see responses from the Agno API

4. The app displays the model used and response time for each interaction

## Troubleshooting

If you encounter connection issues:
- Make sure the Agno API is running
- Check that the API URL is correct (http://localhost:8000/api/v1)
- Verify Docker containers are running properly

If streaming isn't working:
- Check that the `sseclient-py` package is installed
- Verify that the API is correctly implementing server-sent events 