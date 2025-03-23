import requests
import json
import sys
import argparse

def test_chat_endpoint(model_name=None):
    """Test the chat endpoint of our Agno Chat API."""
    # API endpoint
    url = "http://localhost:8000/api/v1/chat"
    
    # Request payload
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hello! Can you tell me about the Agno framework?"
            }
        ],
        "max_tokens": 500
    }
    
    # Add model_name if specified
    if model_name:
        payload["model_name"] = model_name
        print(f"Testing with model: {model_name}")
    else:
        print("Testing with default model")
    
    try:
        # Send POST request
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            print("Status: SUCCESS")
            print(f"Model used: {result.get('model', 'Not specified')}")
            
            # Handle different response formats
            if 'message' in result and 'content' in result['message']:
                print(f"Response content: {result['message']['content']}")
            else:
                print(f"Response: {result}")
        else:
            print(f"Status: ERROR (Code: {response.status_code})")
            print(f"Error details: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Test the Agno Chat API with different models.')
    parser.add_argument('--model', '-m', help='The model to use (e.g., gpt-4, gpt-3.5-turbo)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    test_chat_endpoint(args.model) 