import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest, ChatResponse, StreamingChunk
from app.core.openai_service import AgnoService
from app.core.config import MODEL_NAME
import json

# Get logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, req: Request):
    """
    Chat with an AI agent using Agno.
    
    This endpoint takes a chat request with previous messages and returns a response from the Agno agent.
    
    You can specify a different model by including the model_name parameter (e.g., "gpt-4", "gpt-3.5-turbo").
    If not provided, the default model from the server configuration will be used.
    
    Set stream=True to receive a streaming response.
    """
    # If streaming is requested, use the streaming endpoint
    if request.stream:
        return await stream_chat_with_agent(request, req)
    
    client_host = req.client.host if req.client else "unknown"
    request_id = req.headers.get("X-Request-ID", "unknown")
    
    # Get the model name from the request or use the default
    model_name = request.model_name or MODEL_NAME
    
    logger.info(
        f"Chat request received",
        extra={
            "client_ip": client_host, 
            "request_id": request_id,
            "model": model_name
        }
    )
    
    try:
        # Log the user's query (but be careful with PII)
        if request.messages and len(request.messages) > 0:
            last_message = request.messages[-1].content
            # Truncate long messages for logging
            truncated_message = last_message[:50] + ('...' if len(last_message) > 50 else '')
            logger.info(
                f"Processing query: {truncated_message}",
                extra={
                    "request_id": request_id, 
                    "message_length": len(last_message),
                    "model": model_name
                }
            )
        
        response = AgnoService.chat_completion(
            messages=request.messages,
            max_tokens=request.max_tokens,
            model_name=request.model_name,
            stream=False
        )
        
        # Log successful completion
        logger.info(
            f"Chat request completed successfully",
            extra={
                "request_id": request_id,
                "model": model_name
            }
        )
        
        return response
        
    except ValueError as ve:
        logger.error(
            f"Validation error",
            extra={
                "request_id": request_id, 
                "error": str(ve),
                "model": model_name
            }
        )
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(
            f"Error processing request",
            exc_info=True,
            extra={
                "request_id": request_id, 
                "error": str(e),
                "model": model_name
            }
        )
        raise HTTPException(status_code=500, detail=f"Error communicating with Agno agent: {str(e)}")


async def stream_chat_with_agent(request: ChatRequest, req: Request):
    """
    Stream chat response from the Agno agent.
    """
    client_host = req.client.host if req.client else "unknown"
    request_id = req.headers.get("X-Request-ID", "unknown")
    
    # Get the model name from the request or use the default
    model_name = request.model_name or MODEL_NAME
    
    logger.info(
        f"Streaming chat request received",
        extra={
            "client_ip": client_host, 
            "request_id": request_id,
            "model": model_name
        }
    )
    
    # Log the user's query (but be careful with PII)
    if request.messages and len(request.messages) > 0:
        last_message = request.messages[-1].content
        # Truncate long messages for logging
        truncated_message = last_message[:50] + ('...' if len(last_message) > 50 else '')
        logger.info(
            f"Processing streaming query: {truncated_message}",
            extra={
                "request_id": request_id, 
                "message_length": len(last_message),
                "model": model_name,
                "streaming": True
            }
        )
    
    async def event_generator():
        """Generate server-sent events."""
        try:
            async for chunk in AgnoService.chat_completion(
                messages=request.messages,
                max_tokens=request.max_tokens,
                model_name=request.model_name,
                stream=True
            ):
                # Convert the chunk to a dictionary for JSON serialization
                chunk_dict = chunk.dict()
                
                # Format as a server-sent event with proper JSON serialization
                yield f"data: {json.dumps(chunk_dict)}\n\n"
                
                # If this is the final chunk, log completion
                if chunk.done:
                    logger.info(
                        f"Streaming chat request completed successfully",
                        extra={
                            "request_id": request_id,
                            "model": model_name
                        }
                    )
        except Exception as e:
            logger.error(
                f"Error processing streaming request",
                exc_info=True,
                extra={
                    "request_id": request_id, 
                    "error": str(e),
                    "model": model_name
                }
            )
            # Send an error event
            error_chunk = StreamingChunk(
                content=f"\n\nError: {str(e)}",
                done=True,
                model=model_name
            )
            yield f"data: {json.dumps(error_chunk.dict())}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    ) 