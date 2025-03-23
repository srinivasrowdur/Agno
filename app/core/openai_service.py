import logging
import time
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator, Union
from app.core.config import OPENAI_API_KEY, MODEL_NAME
from app.models.chat import ChatMessage, ChatResponse, StreamingChunk
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat

logger = logging.getLogger(__name__)

# Check for API key at module initialization
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables")

class AgnoService:
    """Service for interacting with the Agno agent."""
    
    # Dictionary to store agents for different models
    _agents = {}
    
    @classmethod
    def get_agent(cls, model_name: Optional[str] = None):
        """
        Get or create an Agno agent for the specified model.
        
        Args:
            model_name: The name of the model to use. If None, the default from config is used.
            
        Returns:
            An Agno agent instance.
        """
        # Use the default model from config if not specified
        model_to_use = model_name or MODEL_NAME
        
        # Create a new agent if one doesn't exist for this model
        if model_to_use not in cls._agents:
            logger.info(f"Initializing Agno agent with model: {model_to_use}")
            
            # Create a new Agno agent
            cls._agents[model_to_use] = Agent(
                model=OpenAIChat(
                    id=model_to_use,
                    api_key=OPENAI_API_KEY
                ),
                description="You are a helpful assistant that provides clear and concise answers.",
                markdown=True
            )
        
        return cls._agents[model_to_use]

    @classmethod
    def chat_completion(cls, messages: List[ChatMessage], max_tokens: int = 1000, model_name: Optional[str] = None, stream: bool = False) -> Union[ChatResponse, AsyncIterator[StreamingChunk]]:
        """
        Generate a chat completion using Agno agent.
        
        Args:
            messages: List of chat messages
            max_tokens: Maximum number of tokens to generate
            model_name: The name of the model to use. If None, the default from config is used.
            stream: Whether to stream the response or not
            
        Returns:
            ChatResponse object with the agent's response or an async iterator of StreamingChunk objects.
        """
        start_time = time.time()
        
        # Use the provided model or default
        model_to_use = model_name or MODEL_NAME
        
        # Log which model is being used
        logger.info(f"Using model: {model_to_use} with streaming={stream}")
        
        # Get the agent for this model
        agent = cls.get_agent(model_to_use)
        
        # Extract the last user message for Agno
        # Agno processes only the current message, not the full conversation
        if not messages:
            raise ValueError("No messages provided in request")
        
        last_message = messages[-1].content
        
        if not last_message or last_message.strip() == "":
            raise ValueError("Empty message content")
        
        # Handle streaming differently from non-streaming
        if stream:
            return cls._handle_streaming_response(agent, last_message, model_to_use)
        else:
            return cls._handle_normal_response(agent, last_message, model_to_use, start_time)

    @classmethod
    def _handle_normal_response(cls, agent, last_message, model_to_use, start_time):
        """Handle non-streaming response with retries."""
        # Implement retry logic for API calls
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Get response from the agent
                logger.debug(f"Sending request to Agno agent with model {model_to_use} (attempt {retry_count + 1}/{max_retries})")
                response = agent.run(last_message)
                
                # Format the response
                result = ChatResponse(
                    message=ChatMessage(
                        role="assistant", 
                        content=response.content if hasattr(response, 'content') else str(response)
                    ),
                    usage=None,  # Agno doesn't provide usage statistics
                    model=model_to_use  # Include the model used in the response
                )
                
                elapsed_time = time.time() - start_time
                logger.info(f"Processed request with model {model_to_use} in {elapsed_time:.2f} seconds")
                
                return result
                
            except Exception as e:
                retry_count += 1
                last_error = e
                
                if retry_count < max_retries:
                    backoff_time = 2 ** retry_count  # Exponential backoff
                    logger.warning(f"Error with Agno agent (model: {model_to_use}), retrying in {backoff_time}s: {str(e)}")
                    time.sleep(backoff_time)
                else:
                    logger.error(f"Failed to get response from model {model_to_use} after {max_retries} attempts: {str(e)}")
                    raise
        
        # This should not be reached due to the raise in the loop, but just in case
        raise last_error

    @classmethod
    async def _handle_streaming_response(cls, agent, last_message, model_to_use) -> AsyncIterator[StreamingChunk]:
        """Handle streaming response by yielding chunks."""
        logger.debug(f"Starting streaming response with model {model_to_use}")
        
        try:
            # Stream the response using the agent's run method with stream=True
            # This returns a regular generator, not an async generator
            full_content = ""
            
            # Get the generator
            chunk_generator = agent.run(last_message, stream=True)
            
            # Process each chunk from the generator
            for chunk_obj in chunk_generator:
                # Convert to string if not already a string
                if not isinstance(chunk_obj, str):
                    if hasattr(chunk_obj, 'delta'):
                        delta = chunk_obj.delta
                    elif hasattr(chunk_obj, 'content'):
                        delta = chunk_obj.content[len(full_content):] if hasattr(chunk_obj, 'content') else ""
                    else:
                        delta = str(chunk_obj)
                else:
                    delta = chunk_obj
                
                # Only yield non-empty chunks to reduce noise
                if delta:
                    # Track the full content for calculating deltas
                    full_content += delta
                    
                    # Log the delta content for debugging
                    logger.debug(f"Streaming chunk: {delta[:20]}..." if len(delta) > 20 else f"Streaming chunk: {delta}")
                    
                    # Create and yield the streaming chunk
                    yield StreamingChunk(
                        content=delta,
                        done=False,
                        model=model_to_use
                    )
            
            # Send a final chunk to indicate we're done
            yield StreamingChunk(
                content="",
                done=True,
                model=model_to_use
            )
            
            logger.info(f"Completed streaming response with model {model_to_use}")
            
        except Exception as e:
            logger.error(f"Error streaming response from model {model_to_use}: {str(e)}", exc_info=True)
            # Yield an error message as a final chunk
            yield StreamingChunk(
                content=f"\n\nError: {str(e)}",
                done=True,
                model=model_to_use
            )
            # Re-raise the exception to be handled by the caller
            raise 