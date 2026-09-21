import logging
from config.prompts import SUMMARIZER_REDUCE_SYSTEM, SUMMARIZER_REDUCE_USER
from core.llm import get_llm, call_llm
from core.state import PipelineState

logger = logging.getLogger(__name__)

class SummarizerAgent:
    def __init__(self):
        self.llm = get_llm()
        self.max_input_words = 6000 

    def run(self, state: PipelineState) -> PipelineState:
        logger.info("--- NODE: SUMMARIZER ---")
        raw_docs = state.get("raw_documents", [])
        if not raw_docs:
            logger.info("No raw documents found. Skipping summarization.")
            state["context_summary"] = "No context available."
            return state

        combined_text = "\n\n".join(
            [f"[{getattr(d, 'source', d.get('source', 'Unknown Source') if isinstance(d, dict) else 'Unknown Source')}]\n"
             f"{getattr(d, 'content', d.get('content', '') if isinstance(d, dict) else '')}" 
             for d in raw_docs]
        )
        
        
        words = combined_text.split()
        if len(words) > self.max_input_words:
            logger.warning(f"Combined text too long ({len(words)} words). Truncating to {self.max_input_words}.")
            combined_text = " ".join(words[:self.max_input_words]) + "...\n[TRUNCATED]"

        user_query = state.get("user_query", "")
        prompt = SUMMARIZER_REDUCE_USER.format(
            question=user_query, 
            summaries=combined_text
        )
        
       
        try:
            summary = call_llm(self.llm, system=SUMMARIZER_REDUCE_SYSTEM, user=prompt, max_tokens=1500)
            state["context_summary"] = summary
            logger.info("Summarization successful.")
            
        except Exception as e:
            logger.error(f"Summarizer failed: {e}")
            

            fallback_words = combined_text.split()
            state["context_summary"] = " ".join(fallback_words[:500]) + "...\n[FALLBACK DUE TO ERROR]"
            
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Summarizer error: {str(e)}")
            
        return state