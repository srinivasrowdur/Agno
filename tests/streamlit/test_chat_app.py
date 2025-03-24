import streamlit as st
import requests
import json
import time
import re

# Set page config
st.set_page_config(
    page_title="Agno API Chat Test",
    page_icon="💬",
    layout="centered"
)

# API endpoint configuration
API_BASE_URL = "http://localhost:8000/api/v1"
MODELS = ["o3-mini", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

# App title and description
st.title("Agno API Chat Test")
st.markdown("This is a simple test app for the Agno API chat functionality.")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    selected_model = st.selectbox("Select Model", MODELS)
    enable_streaming = st.checkbox("Enable Streaming", value=True)
    max_tokens = st.slider("Max Tokens", min_value=100, max_value=4000, value=1000, step=100)
    show_raw_content = st.checkbox("Show Raw Content", value=False)
    
    st.header("API Information")
    st.write(f"API URL: {API_BASE_URL}")
    
    # Test connection button
    if st.button("Test Connection"):
        try:
            response = requests.get(f"{API_BASE_URL.split('/api/v1')[0]}")
            if response.status_code == 200:
                st.success("Connection successful!")
            else:
                st.error(f"Connection failed: Status {response.status_code}")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

# When user submits a message
if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Create request payload
    payload = {
        "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        "model_name": selected_model,
        "max_tokens": max_tokens,
        "stream": enable_streaming
    }
    
    # Process with streaming or non-streaming mode
    with st.chat_message("assistant"):
        if enable_streaming:
            # Streaming mode
            message_placeholder = st.empty()
            full_response = ""
            debug_container = st.empty()
            
            try:
                headers = {
                    "Content-Type": "application/json", 
                    "Accept": "text/event-stream"
                }
                
                # Make the API request for streaming
                with requests.post(
                    f"{API_BASE_URL}/chat", 
                    json=payload, 
                    headers=headers,
                    stream=True
                ) as response:
                    
                    if response.status_code != 200:
                        st.error(f"Error: {response.status_code} - {response.text}")
                    else:
                        # Create a container for raw content if enabled
                        if show_raw_content:
                            raw_container = st.container()
                            with raw_container:
                                st.write("### Raw Response Data")
                                raw_output = st.empty()
                        
                        # Process the streaming response
                        buffer = ""
                        raw_data = []
                        
                        for chunk in response.iter_content(chunk_size=1024):
                            if not chunk:
                                continue
                                
                            # Convert bytes to string if needed
                            if isinstance(chunk, bytes):
                                chunk_str = chunk.decode('utf-8')
                            else:
                                chunk_str = chunk
                            
                            # Add to debug data if showing raw content
                            if show_raw_content:
                                raw_data.append(chunk_str)
                                raw_output.code("".join(raw_data[-10:]), language="text")
                            
                            # Add to buffer and process
                            buffer += chunk_str
                            
                            # Find and process all complete SSE messages
                            # SSE format is "data: {...}\n\n"
                            pattern = r'data: ({.*?})\s*\n\n'
                            matches = re.findall(pattern, buffer)
                            
                            if matches:
                                # Process all matches
                                for data_str in matches:
                                    try:
                                        data = json.loads(data_str)
                                        
                                        # Update debug info
                                        if show_raw_content:
                                            debug_container.json(data)
                                        
                                        # Extract content and update the display
                                        if "content" in data and data["content"]:
                                            full_response += data["content"]
                                            message_placeholder.markdown(full_response + "▌")
                                        
                                        # Check if this is the final chunk
                                        if data.get("done", False):
                                            message_placeholder.markdown(full_response)
                                            break
                                            
                                    except json.JSONDecodeError as e:
                                        st.warning(f"Failed to parse JSON: {data_str[:100]}... (Error: {str(e)})")
                                
                                # Remove processed messages from buffer
                                for match in matches:
                                    buffer = buffer.replace(f"data: {match}\n\n", "", 1)
                        
                        # Final update without cursor
                        message_placeholder.markdown(full_response)
            
            except Exception as e:
                st.error(f"Error during streaming: {str(e)}")
                full_response = f"Error: {str(e)}"
            
            # Add assistant response to chat history if we got something
            if full_response and not full_response.startswith("Error:"):
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        else:
            # Non-streaming mode - simple API call
            try:
                with st.spinner("Thinking..."):
                    start_time = time.time()
                    response = requests.post(f"{API_BASE_URL}/chat", json=payload)
                    elapsed_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        assistant_message = response_data.get("message", {}).get("content", "")
                        model_used = response_data.get("model", "Unknown")
                        
                        st.markdown(assistant_message)
                        st.caption(f"Model: {model_used} | Time: {elapsed_time:.2f}s")
                        
                        # Add to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": assistant_message
                        })
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Add debug expander
with st.expander("Debug Information"):
    st.write("### API Configuration")
    st.json({
        "api_url": API_BASE_URL,
        "model": selected_model,
        "streaming": enable_streaming,
        "max_tokens": max_tokens
    })
    
    st.write("### Test API Response Format")
    if st.button("Test Streaming Format"):
        try:
            test_response = requests.post(
                f"{API_BASE_URL}/chat", 
                json={"messages": [{"role": "user", "content": "Hello, test response format"}], "stream": True},
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            st.write(f"Status Code: {test_response.status_code}")
            st.write(f"Headers: {dict(test_response.headers)}")
            
            # Get the first few chunks to analyze the format
            chunks = []
            for i, chunk in enumerate(test_response.iter_content(chunk_size=1024)):
                if chunk:
                    chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                    chunks.append(chunk_str)
                    
                    # Only get a few chunks
                    if i >= 2:
                        break
            
            st.write("### Raw Response Format")
            st.code("".join(chunks), language="text")
            
            st.write("### Response Analysis")
            joined = "".join(chunks)
            if "data:" in joined:
                st.success("✅ Contains 'data:' prefix (SSE format)")
            else:
                st.error("❌ Missing 'data:' prefix (not SSE format)")
                
            if "\n\n" in joined:
                st.success("✅ Contains '\\n\\n' separator (SSE format)")
            else:
                st.error("❌ Missing '\\n\\n' separator (not SSE format)")
                
            # Try to extract and parse a message 
            pattern = r'data: ({.*?})\s*\n\n'
            matches = re.findall(pattern, joined)
            if matches:
                st.success(f"✅ Found {len(matches)} SSE messages")
                for i, match in enumerate(matches):
                    try:
                        parsed = json.loads(match)
                        st.json(parsed)
                    except:
                        st.code(match, language="json")
            else:
                st.error("❌ No SSE messages found")
                
        except Exception as e:
            st.error(f"Debug request failed: {str(e)}")

# Display additional info and stats at the bottom
st.divider()
st.caption("Agno API Chat Test App | Created for testing")

# Clear all button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun() 