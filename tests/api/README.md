# Agno API Basic Tests

This directory contains tests for the basic functionality of the Agno API.

## Available Tests

### Basic API Test

The `test_api.py` script tests the basic chat completion functionality of the Agno API. It sends a simple query to the API and displays the response.

## How to Run

Run the basic API test with the default model:

```bash
python tests/api/test_api.py
```

You can also specify a different model using the `--model` flag:

```bash
python tests/api/test_api.py --model "gpt-4"
```

## Expected Output

When the test runs successfully, you should see output similar to:

```
Testing with default model
Status: SUCCESS
Model used: gpt-4o-mini
Response content: Hello! I'd be happy to tell you about the Agno framework...
```

The actual response content will vary depending on the model used and the current state of the API. 