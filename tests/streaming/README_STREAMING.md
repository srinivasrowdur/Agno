# Agno API Streaming Support

This document provides an overview of the streaming support implemented for the Agno API.

## Overview

Streaming allows clients to receive responses from the API as they are generated, rather than waiting for the entire response to be completed. This provides a better user experience for applications that display AI-generated content to users.

## Implementation Details

The streaming support has been implemented in the following components:

1. **API Endpoints (`app/api/endpoints.py`)**:
   - Handles streaming requests via Server-Sent Events (SSE)
   - Provides proper JSON serialization for streaming chunks
   - Returns a `StreamingResponse` with appropriate content type headers

2. **OpenAI Service (`app/core/openai_service.py`)**:
   - Uses Agno's native streaming capability with `agent.run(message, stream=True)`
   - Processes the `RunResponse` objects returned by Agno's streaming generator
   - Maps each chunk to a `StreamingChunk` model for consistent API responses

3. **Models (`app/models/chat.py`)**:
   - `StreamingChunk` model represents individual stream chunks with:
     - `content`: The text content of the chunk
     - `done`: Boolean indicating if this is the final chunk
     - `model`: The model used to generate the response

## How Streaming Works

1. The client sends a request to `/api/v1/chat` with `"stream": true` in the JSON payload
2. The API identifies this as a streaming request and calls `stream_chat_with_agent`
3. The Agno agent processes the request with `stream=True`
4. Each chunk from the Agno agent is converted to a `StreamingChunk` object
5. Chunks are sent to the client as Server-Sent Events in the format:
   ```
   data: {"content": "chunk text", "done": false, "model": "model-name"}
   ```
6. The final chunk has `"done": true` to signal the end of the stream

## How to Test

We provide several ways to test the streaming functionality:

### Basic Streaming Test

Run the following command to test basic streaming functionality:

```bash
python tests/streaming/test_streaming.py
```

You can also specify a different model using the `--model` flag:

```bash
python tests/streaming/test_streaming.py --model "gpt-4"
```

### Visual Streaming Test

For a more visual demonstration of streaming (with added delay between characters), use:

```bash
python tests/streaming/stream_test_with_delay.py
```

This script adds a small delay between displaying characters, which helps visualize the streaming behavior.

### Streamlit Test App

We've also created a Streamlit application that provides a visual interface for testing the API:

```bash
streamlit run tests/streamlit/test_chat_app.py
```

This app provides:
- A chat interface to interact with the API
- Support for both streaming and non-streaming modes
- Configuration options for different models
- Debugging tools to analyze the API responses

## Client Implementation Tips

When implementing a client to consume the streaming API:

1. Use a library that supports Server-Sent Events (SSE)
2. Parse each event as JSON to extract the chunk content
3. Accumulate chunks to build the complete response
4. Check the `done` flag to know when the stream is complete
5. Handle potentially small chunk sizes (sometimes single characters)

## Troubleshooting

Common issues and solutions:

1. **Issue**: Chunks with very small content (single letters/punctuation)  
   **Solution**: This is normal behavior - accumulate chunks for display

2. **Issue**: Non-natural word breaks in chunks  
   **Solution**: The client should buffer and display at word boundaries

3. **Issue**: Stream ending prematurely  
   **Solution**: Check for network issues or timeouts in your client

## Future Improvements

Potential improvements for the streaming implementation include:

1. Client-side improvements for smoother text rendering
2. Additional metadata in streaming chunks (token counts, etc.)
3. Improved error recovery for interrupted streams 