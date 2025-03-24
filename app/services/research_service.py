import logging
from typing import AsyncIterator, Dict, Any
from agno import Agent, RunResponse
from app.core.config import settings
from app.core.exa_service import ExaService

logger = logging.getLogger(__name__)

class ResearchService:
    """Service for handling research queries using Agno and Exa tools."""
    
    def __init__(self):
        """Initialize the research service with Agno agent and Exa tools."""
        self.exa_service = ExaService()
        self.agent = Agent(
            model=settings.DEFAULT_MODEL,
            tools=[self.exa_service.search, self.exa_service.get_content],
            request_params={
                "temperature": 0.7,
                "max_tokens": 2000
            }
        )
        logger.info("Research service initialized with Exa tools")
    
    async def research(
        self,
        query: str,
        model_name: str = None,
        stream: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Perform research using Agno agent and Exa tools.
        
        Args:
            query: The research query
            model_name: Optional model name to use
            stream: Whether to stream the response
            
        Yields:
            Dict containing research results
        """
        try:
            # Update model if specified
            if model_name:
                self.agent.model = model_name
                logger.info(f"Using model: {model_name}")
            
            # Create research prompt
            prompt = f"""Research the following query and provide a comprehensive response:
            Query: {query}
            
            Use the available tools to:
            1. Search for relevant information
            2. Get detailed content from the most relevant sources
            3. Synthesize the information into a coherent response
            
            Focus on recent and authoritative sources.
            """
            
            # Get response from agent
            if stream:
                response = await self.agent.run(prompt, stream=True)
                async for chunk in response:
                    if chunk.content:
                        yield {
                            "content": chunk.content,
                            "done": False
                        }
                yield {"content": "", "done": True}
            else:
                response = await self.agent.run(prompt)
                if isinstance(response, RunResponse):
                    yield {
                        "content": response.content,
                        "done": True
                    }
                else:
                    yield {
                        "content": str(response),
                        "done": True
                    }
                    
        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            yield {
                "error": f"Error during research: {str(e)}",
                "done": True
            } 