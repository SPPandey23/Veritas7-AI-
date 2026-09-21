import logging
import json
from config.prompts import CRITIC_SYSTEM, CRITIC_USER
from core.llm import get_llm, call_llm
from core.state import PipelineState, CriticResult

logger = logging.getLogger(__name__)

class CriticAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, state: PipelineState) -> PipelineState:
        logger.info("--- NODE: CRITIC ---")
        
        # 1. Guard against missing inputs (bracket notation for TypedDict)
        query = state.get("user_query", "")
        context = state.get("context_summary", "")
        answer = state.get("draft_answer", "")
        
        prompt = CRITIC_USER.format(
            question=query,
            context=context,
            answer=answer
        )
        
        try:
            raw_eval = call_llm(self.llm, system=CRITIC_SYSTEM, user=prompt, json_mode=True, max_tokens=1000)
            
            # 2. Strip Markdown backticks before parsing JSON
            clean_eval = raw_eval.strip()
            if clean_eval.startswith("```"):
                # Remove the first line (e.g., ```json) and the last line (```)
                lines = clean_eval.split("\n")
                if len(lines) >= 2:
                    clean_eval = "\n".join(lines[1:-1]).strip()
            
            data = json.loads(clean_eval)
            
            # 3. Enforce data types for lists to prevent .join() bugs in Refiner
            issues = data.get("issues", [])
            if not isinstance(issues, list):
                issues = [str(issues)]
                
            missing_topics = data.get("missing_topics", [])
            if not isinstance(missing_topics, list):
                missing_topics = [str(missing_topics)]
            
            result = CriticResult(
                verdict=data.get("verdict", "needs_improvement"),
                overall_score=float(data.get("overall_score", 5.0)),
                issues=issues,
                missing_topics=missing_topics,
                improvement_instruction=data.get("improvement_instruction", "")
            )
            
            state["critic_result"] = result
            state["confidence_score"] = result.overall_score / 10.0
            logger.info(f"Critic Verdict: {result.verdict} (Score: {result.overall_score})")

        except Exception as e:
            logger.error(f"Critic failed to parse evaluation: {e}")
            # 4. Safer fallback: Pass the draft to prevent infinite loops, 
            # but flag it with a 0.0 confidence score so it isn't trusted blindly.
            state["critic_result"] = CriticResult(
                verdict="good",  # 'good' prevents the Refiner from looping infinitely
                overall_score=0.0, 
                issues=["Critic evaluation failed."],
                missing_topics=[],
                improvement_instruction=""
            )
            state["confidence_score"] = 0.0
            
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Critic Agent Error: {str(e)}")
            
        return state