import logging
from typing import List
from tavily import TavilyClient
from config.settings import settings
from core.state import SourceDocument

logger = logging.getLogger(__name__)

class WebSearchTool:
    def __init__(self):
        """
        Initializes the Tavily client using the API key from settings.
        """
        if not settings.TAVILY_API_KEY:
            logger.warning("TAVILY_API_KEY is missing. Web search will fail.")
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(self, query: str, n: int = 5) -> List[SourceDocument]:
        """
        Performs a web search and converts raw results into SourceDocument objects.
        This prevents the 'dict' object error in the ResearchAgent.
        """
        if not query:
            return []

        try:
            logger.info(f"Tavily searching: {query}")
            # Execute the search
            response = self.client.search(
                query=query, 
                max_results=n,
                search_depth="advanced" # Use 'advanced' for better quality AI research
            )
            
            raw_results = response.get("results", [])
            formatted_docs = []

            for res in raw_results:
                # We map the Tavily keys to our SourceDocument fields
                doc = SourceDocument(
                    content=res.get("content", ""),
                    source=res.get("url", "unknown_source"),
                    relevance_score=res.get("score", 0.0)
                )
                formatted_docs.append(doc)

            return formatted_docs

        except Exception as e:
            logger.error(f"Tavily search failed for '{query}': {e}")
            # Return an empty list so the pipeline can attempt to continue
            return []

    def rewrite_and_search(self, query: str):
        """
        Optional: Some users prefer a combined 'search and summarize' 
        but for your 7-stage pipeline, we keep it simple.
        """
        return self.search(query)