# Agno API Tests

This directory contains various tests for the Agno API.

## Test Categories

### API Tests

Located in the `api` directory, these tests demonstrate and validate the basic functionality of the Agno API.

- `test_api.py`: Tests the basic chat completion endpoint with different models

To run the API tests, use the following command:

```bash
# Basic API test
python tests/api/test_api.py

# Test with a specific model
python tests/api/test_api.py --model "gpt-4"
```

### Streaming Tests

Located in the `streaming` directory, these tests demonstrate and validate the streaming functionality of the Agno API.

- `test_streaming.py`: Basic streaming test that connects to the API and displays streamed responses
- `stream_test_with_delay.py`: Visual streaming test that adds delays between characters to better visualize the streaming behavior
- `README_STREAMING.md`: Detailed documentation of the streaming implementation and testing procedures

To run the streaming tests, use the following commands:

```bash
# Basic streaming test
python tests/streaming/test_streaming.py

# Visual streaming test (with delay)
python tests/streaming/stream_test_with_delay.py
```

You can specify a different model using the `--model` flag:

```bash
python tests/streaming/test_streaming.py --model "gpt-4"
``` 