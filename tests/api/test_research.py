import os
import pytest
import requests
import sseclient
import json
from typing import Generator

API_URL = "http://localhost:8000/api/v1"

def test_research_endpoint():
    """Test the basic research endpoint functionality."""
    response = requests.post(
        f"{API_URL}/research",
        json={
            "query": "What are the latest developments in quantum computing?",
            "model_name": "o3-mini",
            "stream": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "content" in data["message"]
    assert data["model"] == "o3-mini"

def test_research_streaming():
    """Test the streaming research functionality."""
    response = requests.post(
        f"{API_URL}/research",
        json={
            "query": "What are the latest developments in AI safety?",
            "model_name": "o3-mini",
            "stream": True
        },
        stream=True
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
    
    client = sseclient.SSEClient(response)
    chunks = []
    
    for event in client.events():
        chunk = json.loads(event.data)
        chunks.append(chunk)
        
        # Verify chunk structure
        assert "content" in chunk
        assert "done" in chunk
        assert "model" in chunk
        
        if chunk["done"]:
            break
    
    assert len(chunks) > 0
    assert chunks[-1]["done"] == True

if __name__ == "__main__":
    # Run tests
    test_research_endpoint()
    print("Basic research test passed!")
    
    test_research_streaming()
    print("Streaming research test passed!") 