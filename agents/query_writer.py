import logging
from config.prompts import REWRITER_SYSTEM, REWRITER_USER, HYDE_SYSTEM, HYDE_USER
from core.llm import get_rewriter_llm, call_llm
from core.state import PipelineState

logger = logging.getLogger(__name__)

class QueryRewriterAgent:
    def __init__(self):
        self.llm = get_rewriter_llm()

    def run(self, state: PipelineState) -> PipelineState:
        # Safely get the sub_questions list from the dictionary
        sub_questions = state.get("sub_questions", [])
        logger.info(f"QueryRewriterAgent starting for {len(sub_questions)} questions")
        
        keywords = []
        hyde_passages = []

        # Synchronous execution is robust and simple
        for q in sub_questions:
            try:
                # Web search keyword query
                kw_prompt = REWRITER_USER.format(sub_question=q)
                kw_raw = call_llm(self.llm, system=REWRITER_SYSTEM, user=kw_prompt, max_tokens=100)
                kw_clean = kw_raw.strip('"\'').replace("Query:", "").strip()
                keywords.append(kw_clean if kw_clean else q)

                # HyDE passage 
                hyde_prompt = HYDE_USER.format(sub_question=q)
                hyde_raw = call_llm(self.llm, system=HYDE_SYSTEM, user=hyde_prompt, max_tokens=200)
                hyde_passages.append(hyde_raw.strip() if hyde_raw.strip() else q)
                
            except Exception as e:
                logger.error(f"QueryRewriter fail for {q}: {e}")
                keywords.append(q)
                hyde_passages.append(q)
                
                # Safely log the error to the state dictionary
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(f"Rewriter error for '{q}': {str(e)}")

        # Update the state using bracket notation
        state["rewritten_queries"] = keywords
        state["hyde_passages"] = hyde_passages
        
        return state