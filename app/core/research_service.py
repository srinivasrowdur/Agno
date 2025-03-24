import logging
import os
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, AsyncIterator, Any

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.run.response import RunResponse
from fastapi import HTTPException

from app.core.config import MODEL_NAME, OPENAI_API_KEY
from app.models.research import ResearchRequest, ResearchResponse, StreamingChunk

logger = logging.getLogger(__name__)

class ResearchService:
    """Service for handling research queries using Agno and Exa tools."""
    
    def __init__(self, model_name: str):
        """
        Initialize the research service with Exa tools.
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.agent = Agent(
                model=OpenAIChat(
                    id=model_name,
                    api_key=OPENAI_API_KEY
                ),
                tools=[ExaTools(start_published_date=today, type="keyword")],
                description="""You are a distinguished research analyst specializing in synthesizing 
                information from multiple sources. Your expertise lies in creating clear, factual 
                reports that combine academic rigor with engaging narrative.""",
                instructions="""
                1. Begin by running targeted searches to gather comprehensive information
                2. Analyze and cross-reference sources for accuracy and relevance
                3. Structure your findings in a clear, logical format
                4. Include only verifiable facts with proper citations
                5. Create an engaging narrative that guides through complex topics
                """,
                expected_output="""
                A professional research report in markdown format:

                # {Topic Title}

                ## Key Findings
                {Major discoveries or developments with citations}

                ## Analysis
                {Detailed analysis of the findings}

                ## Sources
                {Numbered list of sources with relevant quotes}
                """,
                markdown=True,
                show_tool_calls=True
            )
            logger.info("Research service initialized with Exa tools")
        except Exception as e:
            logger.error(f"Error initializing research service: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def research(self, query: str, stream: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Perform research using the agent and Exa tools.
        """
        try:
            logger.info(f"Starting research for query: query='{query}' model_name='{self.agent.model.id}' stream={stream}")
            
            if not stream:
                response = self.agent.run(query)
                if isinstance(response, dict):
                    yield {"content": response.get("content", str(response)), "done": True}
                elif isinstance(response, RunResponse):
                    yield {"content": response.content, "done": True}
                else:
                    yield {"content": str(response), "done": True}
                return

            is_first_chunk = True
            for chunk in self.agent.run(query, stream=True):
                if isinstance(chunk, dict):
                    yield {"content": chunk.get("content", str(chunk)), "done": False}
                elif isinstance(chunk, RunResponse):
                    yield {"content": chunk.content, "done": False}
                else:
                    yield {"content": str(chunk), "done": False}
                is_first_chunk = False
            
            yield {"content": "", "done": True}
        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 