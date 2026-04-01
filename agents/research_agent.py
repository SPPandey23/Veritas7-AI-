import logging
from typing import List

from core.state import PipelineState, SourceDocument
from retrieval.web_search import WebSearchTool  
from config.settings import settings

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self):
        self.web_search = WebSearchTool()

    def run(self, state: PipelineState) -> PipelineState:
        logger.info("--- NODE: RESEARCH AGENT ---")

        queries = state.get("rewritten_queries", [])
        if not queries:
            queries = [state.get("user_query", "")]
            logger.warning("No rewritten queries found. Falling back to original query.")
        
        all_results: List[SourceDocument] = []

        for q in queries:
            if not q: continue
            try:
        
                web_docs = self.web_search.search(q, n=settings.TOP_K_RESULTS)
                all_results.extend(web_docs)
            except Exception as e:
                logger.error(f"Search failed for query '{q}': {e}")
              
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(f"Search Error: {str(e)}")

        seen_content = set()
        unique_docs = []
        
        for doc in all_results:
           
            if doc.content not in seen_content:
                seen_content.add(doc.content)
                unique_docs.append(doc)

      
        unique_docs.sort(key=lambda x: x.relevance_score, reverse=True)

        
        state["raw_documents"] = unique_docs[:15]
        
        logger.info(f"Research complete. Gathered {len(state['raw_documents'])} documents.")
        
        return state