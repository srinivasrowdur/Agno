import os
import logging
from typing import List, Dict, Any
from exa_py import Exa

logger = logging.getLogger(__name__)

class ExaService:
    """Service for interacting with the Exa API."""
    
    def __init__(self):
        """Initialize the Exa service with API key."""
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            raise ValueError("EXA_API_KEY environment variable is not set")
        
        self.client = Exa(api_key)
        logger.info("Exa service initialized")
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for content using Exa API.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        try:
            results = await self.client.search(
                query,
                num_results=max_results,
                use_autoprompt=True
            )
            return results
        except Exception as e:
            logger.error(f"Error during Exa search: {str(e)}")
            raise
    
    async def get_content(self, url: str) -> str:
        """
        Get content from a URL using Exa API.
        
        Args:
            url: The URL to get content from
            
        Returns:
            The content as a string
        """
        try:
            content = await self.client.get_content(url)
            return content
        except Exception as e:
            logger.error(f"Error getting content from {url}: {str(e)}")
            raise 