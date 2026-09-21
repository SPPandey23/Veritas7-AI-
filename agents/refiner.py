import logging
from config.prompts import REFINER_SYSTEM, REFINER_USER
from core.llm import get_llm, call_llm
from core.state import PipelineState

logger = logging.getLogger(__name__)

class RefinerAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, state: PipelineState) -> PipelineState:
        logger.info("--- NODE: REFINER ---")
        
        # 1. Early exit if the critic approved the draft or doesn't exist
        critic_result = state.get("critic_result", None)
        
        if not critic_result:
            logger.info("RefinerAgent skipping (no critic result)")
            return state

        # Handle both dict and CriticResult object
        if isinstance(critic_result, dict):
            verdict = critic_result.get("verdict", "good")
            issues_list = critic_result.get("issues", [])
            missing_list = critic_result.get("missing_topics", [])
            instruction = critic_result.get("improvement_instruction", "")
        else:
            verdict = getattr(critic_result, "verdict", "good")
            is_good = getattr(critic_result, "is_good", False)
            if is_good:
                logger.info("RefinerAgent skipping (critic approved draft)")
                return state
            issues_list = getattr(critic_result, "issues", [])
            missing_list = getattr(critic_result, "missing_topics", [])
            instruction = getattr(critic_result, "improvement_instruction", "")

        if verdict.lower() == "good":
            logger.info("RefinerAgent skipping (critic verdict is good)")
            return state

        logger.info("RefinerAgent improving draft")
        
        # 2. Guard against None types in the state
        query = state.get("user_query", "")
        context = state.get("context_summary", "")
        draft = state.get("draft_answer", "")
        
        # 3. Safely join lists, defaulting to empty lists if None
        safe_issues = ", ".join(issues_list or [])
        safe_missing_topics = ", ".join(missing_list or [])
        
        prompt = REFINER_USER.format(
            question=query,
            context=context,
            draft_answer=draft,
            issues=safe_issues,
            missing_topics=safe_missing_topics,
            improvement_instruction=instruction
        )
        
        try:
            refined = call_llm(self.llm, system=REFINER_SYSTEM, user=prompt, max_tokens=2000)
            state["draft_answer"] = refined
            state["final_answer"] = refined
            
            # Increment iteration count
            current_count = state.get("iteration_count", 0)
            state["iteration_count"] = current_count + 1
                
        except Exception as e:
            logger.error(f"Refiner failed: {e}")
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Refiner Agent Error: {str(e)}")
            # Note: We do NOT overwrite the draft_answer here, so if refinement fails, 
            # the user still gets the original draft rather than an error message.
            
        return state