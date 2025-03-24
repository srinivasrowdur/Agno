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
                
                # Handle generator objects by consuming the generator
                if hasattr(response, '__iter__') and hasattr(response, '__next__') and not hasattr(response, 'content'):
                    # It's a generator - consume it to get the full content
                    content = ""
                    try:
                        for chunk in response:
                            if isinstance(chunk, str):
                                content += chunk
                            elif hasattr(chunk, 'content'):
                                content += chunk.content
                            elif hasattr(chunk, 'delta'):
                                content += chunk.delta
                            else:
                                content += str(chunk)
                    except Exception as e:
                        logger.warning(f"Error consuming generator: {str(e)}")
                        # If we've collected some content, use it; otherwise re-raise
                        if not content:
                            raise
                else:
                    # Not a generator - use content attribute if available or convert to string
                    content = response.content if hasattr(response, 'content') else str(response)
                
                # Format the response
                result = ChatResponse(
                    message=ChatMessage(
                        role="assistant", 
                        content=content
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
            # Use Agno's native streaming functionality
            # This returns an iterator of RunResponse objects
            run_response_iterator = agent.run(last_message, stream=True)
            
            # Process each chunk as it comes
            for chunk in run_response_iterator:
                # Skip empty chunks
                if not chunk or not hasattr(chunk, 'content') or not chunk.content:
                    continue
                
                # Log the chunk content
                logger.debug(f"Streaming chunk: {chunk.content[:30]}..." if len(chunk.content) > 30 else f"Streaming chunk: {chunk.content}")
                
                # Yield a streaming chunk with the content
                yield StreamingChunk(
                    content=chunk.content,
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