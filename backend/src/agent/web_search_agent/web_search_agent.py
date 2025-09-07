import logging
import asyncio
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import current_time
from strands_tools.tavily import tavily_search, tavily_extract
from ...config.settings import settings
from .web_search_system_prompt import WEB_SEARCH_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class WebSearchAgent:
    """Web Search Agent for retrieving real-time information when knowledge base is insufficient."""
    
    def __init__(self):
        model = BedrockModel(
            model_id=settings.BEDROCK_MODEL_ID,
            boto_session=settings.SESSION,
        )
        
        # Import tavily tools with better error handling
        self.tavily_search = None
        self.tavily_extract = None
        
        try:
            self.tavily_search = tavily_search
            self.tavily_extract = tavily_extract
            logger.info("Successfully imported essential Tavily tools")
        except ImportError as e:
            logger.error(f"Failed to import Tavily tools: {e}")
            logger.warning("Web search functionality will be limited")
        
        # Create simplified web search tool
        @tool
        async def search_web_for_current_info(
            query: str, 
            search_type: str = "general",
            max_results: int = 3
        ) -> str:
            """
            Search the web for real-time information when knowledge base doesn't have current data.
            
            Args:
                query: Search query for current information
                search_type: Type of search - "general" for general info, "news" for recent news
                max_results: Maximum number of results to return (1-10)
            
            Returns:
                Formatted search results with current information
            """
            try:
                if not self.tavily_search:
                    return "❌ Web search functionality is not available. Please check Tavily API configuration."
                
                # Configure search parameters
                topic = "news" if search_type == "news" else "general"
                
                result = await self.tavily_search(
                    query=query,
                    search_depth="advanced",
                    topic=topic,
                    max_results=max_results,
                    include_raw_content=True,
                    include_answer=True
                )
                
                if result.get("status") == "success":
                    content_text = result.get("content", [{}])[0].get("text", "")
                    
                    # Simple JSON parsing with fallback
                    try:
                        import json
                        data = json.loads(content_text)
                    except (json.JSONDecodeError, ValueError):
                        return f"**Search Results for:** {query}\n\n{content_text}"
                    
                    # Format results
                    formatted = [f"**Search Results for:** {query}"]
                    
                    if data.get("answer"):
                        formatted.append(f"\n**Summary:** {data['answer']}")
                    
                    if data.get("results"):
                        formatted.append("\n**Sources:**")
                        for i, item in enumerate(data["results"][:max_results], 1):
                            title = item.get("title", "No title")
                            url = item.get("url", "")
                            content = item.get("content", "")
                            
                            formatted.append(f"\n{i}. **{title}**")
                            if content:
                                preview = content[:150] + "..." if len(content) > 150 else content
                                formatted.append(f"   {preview}")
                            if url:
                                formatted.append(f"   🔗 {url}")
                    
                    return "\n".join(formatted)
                        
                else:
                    error_msg = result.get("content", [{}])[0].get("text", "Unknown error")
                    return f"❌ Web search failed: {error_msg}"
                    
            except Exception as e:
                logger.error(f"Error in web search: {e}")
                return f"❌ Error performing web search: {str(e)}"

        @tool
        async def extract_content_from_urls(urls: str) -> str:
            """
            Extract clean content from specific URLs for detailed information.
            
            Args:
                urls: Comma-separated URLs to extract content from
            
            Returns:
                Extracted and formatted content
            """
            try:
                if not self.tavily_extract:
                    return "❌ Content extraction functionality is not available."
                
                # Parse URLs
                url_list = [url.strip() for url in urls.split(",")]
                
                result = await self.tavily_extract(
                    urls=url_list,
                    extract_depth="advanced",
                    format="markdown"
                )
                
                if result.get("status") == "success":
                    content_text = result.get("content", [{}])[0].get("text", "")
                    
                    try:
                        import json
                        data = json.loads(content_text)
                    except (json.JSONDecodeError, ValueError):
                        return f"**Extracted Content:**\n\n{content_text}"
                    
                    formatted = ["**Extracted Content:**"]
                    
                    if data.get("results"):
                        for i, item in enumerate(data["results"], 1):
                            url = item.get("url", "Unknown URL")
                            content = item.get("raw_content", "")
                            
                            formatted.append(f"\n**{i}. Content from {url}:**")
                            if content:
                                # Limit content length for readability
                                preview = content[:800] + "..." if len(content) > 800 else content
                                formatted.append(preview)
                    
                    return "\n".join(formatted)
                        
                else:
                    error_msg = result.get("content", [{}])[0].get("text", "Unknown error")
                    return f"❌ Content extraction failed: {error_msg}"
                    
            except Exception as e:
                logger.error(f"Error in content extraction: {e}")
                return f"❌ Error extracting content: {str(e)}"

        # Initialize the agent with simplified tools
        self.agent = Agent(
            model=model,
            system_prompt=WEB_SEARCH_SYSTEM_PROMPT,
            tools=[
                current_time,
                search_web_for_current_info,
                extract_content_from_urls
            ]
        )
    
    async def search_and_analyze(self, query: str, context: str = "") -> str:
        """
        Perform web search and analysis for queries that require current information.
        
        Args:
            query: The search query or question
            context: Additional context from memory or knowledge base
        
        Returns:
            Comprehensive answer with current web information
        """
        try:
            # Enhanced query with context
            enhanced_query = f"""
SEARCH REQUEST: {query}

CONTEXT: {context if context else "No additional context provided"}

INSTRUCTIONS:
1. Determine if this requires real-time/current information
2. If yes, use search_web_for_current_info to get current data
3. If URLs are provided in results, use extract_content_from_urls for detailed info
4. Provide a comprehensive, accurate answer
5. Cite sources when possible
6. Be clear if information might be outdated or uncertain
"""
            
            result = await self.agent.invoke_async(enhanced_query)
            response = str(result)
            logger.info(f"Web search completed for query: {query[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error in web search analysis: {e}")
            return f"I encountered an error while searching for current information: {str(e)}"


# Create global instance
web_search_agent = WebSearchAgent()


@tool
async def web_search_assistant(query: str, context: str = "") -> str:
    """
    Get current, real-time information from the web when knowledge base is insufficient.
    
    Use this tool when:
    - User asks about recent events, news, or current information
    - Knowledge base doesn't have up-to-date information
    - User requests current market data, weather, or time-sensitive info
    - Specific websites or URLs need to be analyzed
    
    Args:
        query: The search query or question requiring current information
        context: Additional context from memory or knowledge base to help with search
    
    Returns:
        Current information from web search with sources cited
    """
    try:
        # Use the web search agent to get current information
        result = await web_search_agent.search_and_analyze(query, context)
        return result
        
    except Exception as e:
        logger.error(f"Error in web search assistant: {e}")
        return f"I encountered an error while searching for current information: {str(e)}. Please try rephrasing your question or ask me to create a support ticket for technical assistance."
