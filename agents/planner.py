import logging
import re
from config.prompts import PLANNER_SYSTEM, PLANNER_USER
from core.llm import get_planner_llm, call_llm
from core.state import PipelineState

logger = logging.getLogger(__name__)

class PlannerAgent:
    def __init__(self):
        self.llm = get_planner_llm()

    def run(self, state: PipelineState) -> PipelineState:
        user_query = state.get("user_query", "")
        logger.info(f"PlannerAgent starting for query: {user_query}")
        
        try:
            prompt = PLANNER_USER.format(user_query=user_query)
            raw_response = call_llm(self.llm, system=PLANNER_SYSTEM, user=prompt)
            
            # Simple fallback parsing using split
            lines = [line.strip() for line in raw_response.split('\n') if line.strip()]
            questions = []
            
            for line in lines:
                # remove "1. " or "- "
                cleaned = re.sub(r"^(\d+[\.\)]|[-•])\s+", "", line)
                if cleaned:
                    questions.append(cleaned)

            if not questions:
                questions = [user_query]
            
            # Use bracket notation to update the state dictionary
            state["sub_questions"] = questions[:5] # cap at 5
            
        except Exception as e:
            logger.error(f"PlannerAgent failed: {e}")
            state["sub_questions"] = [user_query]
            
            # Safely append to the errors list in the dictionary
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Planner error: {str(e)}")
            
        return state