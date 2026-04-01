import logging
from config.prompts import GENERATOR_SYSTEM, GENERATOR_USER
from core.llm import get_planner_llm, call_llm
from core.state import PipelineState

logger = logging.getLogger(__name__)

class GeneratorAgent:
    def __init__(self):
        self.llm = get_planner_llm()

    def run(self, state: PipelineState) -> PipelineState:
        logger.info("--- NODE: GENERATOR ---")
        
        # 1. Guardrail against missing queries
        query = state.get("user_query", "No query provided.")
        context = state.get("context_summary", "")

        # 2. Prevent RAG hallucinations if context is missing
        if not context or context == "No context available.":
            logger.warning("No context available. Skipping generation to prevent hallucination.")
            no_context_msg = "I could not find enough relevant information to answer your question."
            state["draft_answer"] = no_context_msg
            state["final_answer"] = no_context_msg
            return state

        # 3. Safely format the prompt
        prompt = GENERATOR_USER.format(
            question=query,
            context=context
        )
        
        # 4. Execute LLM call with complete state fallback on failure
        try:
            draft = call_llm(self.llm, system=GENERATOR_SYSTEM, user=prompt, max_tokens=2000)
            state["draft_answer"] = draft
            # We set final_answer here as a baseline; the Refiner might overwrite it later
            state["final_answer"] = draft 
            logger.info("Generation successful.")
            
        except Exception as e:
            logger.error(f"Generator failed: {e}")
            error_msg = "Error generating answer from context."
            
            # Ensure BOTH outputs are populated so downstream systems don't break
            state["draft_answer"] = error_msg
            state["final_answer"] = error_msg
            
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Generator error: {str(e)}")
            
        return state