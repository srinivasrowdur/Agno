# Streaming Support in Agno API

## Overview

The Agno API includes robust streaming support, allowing clients to receive responses progressively as they are generated instead of waiting for the entire response to complete. This provides a better user experience for chat applications and other interfaces where immediate feedback is valuable.

## How to Use Streaming

To use streaming with the Agno API, simply include `"stream": true` in your request payload:

```json
{
  "messages": [
    {"role": "user", "content": "Tell me a story about a robot named Max"}
  ],
  "model": "gpt-3.5-turbo",
  "stream": true
}
```

The API will respond with a stream of Server-Sent Events (SSE), each containing a chunk of the response.

## Client Implementation

### Using JavaScript

```javascript
const eventSource = new EventSource('/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Tell me a story about a robot named Max' }
    ],
    model: 'gpt-3.5-turbo',
    stream: true
  })
});

let responseText = '';

eventSource.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  responseText += chunk.content;
  
  // Update UI with the accumulated response
  document.getElementById('response').textContent = responseText;
  
  // Close the connection when done
  if (chunk.done) {
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

### Using Python

```python
import requests
import sseclient
import json

url = "http://localhost:8000/api/v1/chat"
headers = {"Content-Type": "application/json"}
payload = {
    "messages": [
        {"role": "user", "content": "Tell me a story about a robot named Max"}
    ],
    "model": "gpt-3.5-turbo",
    "stream": True
}

response = requests.post(url, headers=headers, json=payload, stream=True)
client = sseclient.SSEClient(response)

full_response = ""
for event in client.events():
    chunk = json.loads(event.data)
    full_response += chunk["content"]
    print(chunk["content"], end="", flush=True)
    
    if chunk["done"]:
        break

print("\nFull response:", full_response)
```

## Stream Response Format

Each stream event contains a JSON object with the following structure:

```json
{
  "content": "chunk of text",
  "done": false,
  "model": "gpt-3.5-turbo"
}
```

The final chunk will have `"done": true`.

## Technical Details

- The API uses FastAPI's `StreamingResponse` to implement Server-Sent Events
- Events are formatted as JSON strings preceded by `data: `
- Character chunking is determined by the underlying model implementation
- Each chunk may contain a single character, word, or phrase

## Testing

For detailed information on testing the streaming functionality, see:
- [Streaming Implementation Tests](/tests/streaming/README_STREAMING.md)

## Troubleshooting

If you encounter issues with streaming:

1. Ensure your client properly handles SSE format
2. Check your network connection allows for persistent connections
3. Verify that your request includes `"stream": true`
4. For large responses, ensure your client can handle timeouts appropriately 