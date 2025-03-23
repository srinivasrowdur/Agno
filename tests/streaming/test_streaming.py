import requests
import json
import argparse
import sseclient
import sys

def test_streaming_chat(model_name=None):
    """Test the streaming chat endpoint of our Agno Chat API."""
    # API endpoint
    url = "http://localhost:8000/api/v1/chat"
    
    # Request payload
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Count from 1 to 10."
            }
        ],
        "max_tokens": 100,
        "stream": True
    }
    
    # Add model_name if specified
    if model_name:
        payload["model_name"] = model_name
        print(f"Testing streaming with model: {model_name}")
    else:
        print("Testing streaming with default model")
    
    try:
        # Send a streaming request
        response = requests.post(url, json=payload, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Streaming started successfully. Receiving chunks...\n")
            
            # Parse the server-sent events
            client = sseclient.SSEClient(response)
            
            # Track full content
            full_content = ""
            
            # Process each chunk
            for event in client.events():
                try:
                    # The event.data is already a string, not a JSON string
                    # We need to parse it as JSON
                    chunk = json.loads(event.data)
                    
                    # Print the chunk content
                    if "content" in chunk and chunk["content"]:
                        sys.stdout.write(chunk["content"])
                        sys.stdout.flush()
                        full_content += chunk["content"]
                    
                    # Check if this is the final chunk
                    if "done" in chunk and chunk["done"]:
                        print("\n\nStreaming completed.")
                        print(f"Model used: {chunk.get('model', 'Not specified')}")
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    print(f"Raw data: {event.data}")
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    print(f"Raw data: {event.data}")
                    
            print("\n\nFull response content:")
            print(full_content)
            
        else:
            print(f"Status: ERROR (Code: {response.status_code})")
            print(f"Error details: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        print("Make sure the API server is running at http://localhost:8000")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Test the Agno Chat API streaming with different models.')
    parser.add_argument('--model', '-m', help='The model to use (e.g., gpt-4, gpt-3.5-turbo)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    test_streaming_chat(args.model) 