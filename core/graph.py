import logging
from langgraph.graph import StateGraph, START, END

from core.state import PipelineState
from agents.planner import PlannerAgent
from agents.query_writer import QueryRewriterAgent
from agents.research_agent import ResearchAgent
from agents.summarizer import SummarizerAgent
from agents.generator import GeneratorAgent
from agents.critic_agent import CriticAgent
from agents.refiner import RefinerAgent

logger = logging.getLogger(__name__)

planner = PlannerAgent()
rewriter = QueryRewriterAgent()
researcher = ResearchAgent()
summarizer = SummarizerAgent()
generator = GeneratorAgent()
critic = CriticAgent()
refiner = RefinerAgent()

def should_refine(state: PipelineState) -> str:
    max_iterations = 3
    current_iterations = state.get("iteration_count", 0)
    
    if current_iterations >= max_iterations:
        logger.warning(f"Max iterations ({max_iterations}) reached. Forcing exit.")
        return "end"

    critic_result = state.get("critic_result", None)
    if not critic_result:
        logger.info("No critic result found. Routing to END.")
        return "end"

    
    if isinstance(critic_result, dict):
        verdict = critic_result.get("verdict", "good")
    else:
        verdict = getattr(critic_result, "verdict", "good")

    if verdict.lower() == "good":
        logger.info("Critic approved the draft. Routing to END.")
        return "end"

    logger.info("Critic requested improvements. Routing to Refiner.")
    return "refine"

def build_research_graph():
   
    workflow = StateGraph(PipelineState)
    workflow.add_node("planner", planner.run)
    workflow.add_node("rewriter", rewriter.run)
    workflow.add_node("researcher", researcher.run)
    workflow.add_node("summarizer", summarizer.run)
    workflow.add_node("generator", generator.run)
    workflow.add_node("critic", critic.run)
    workflow.add_node("refiner", refiner.run)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "rewriter")
    workflow.add_edge("rewriter", "researcher")
    workflow.add_edge("researcher", "summarizer")
    workflow.add_edge("summarizer", "generator")
    workflow.add_edge("generator", "critic")

    workflow.add_conditional_edges(
        "critic",          
        should_refine,     
        {
            "refine": "refiner", 
            "end": END           
        }
    )

    workflow.add_edge("refiner", "critic")
    app = workflow.compile()
    return app