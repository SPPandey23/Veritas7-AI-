import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import dotenv
dotenv.load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any

from core import build_research_graph

# ── FastAPI App ──────────────────────────────────────────────
app = FastAPI(
    title="Veritas7 AI API",
    description="7-stage autonomous multi-agent research pipeline",
    version="1.0.0"
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response Models ────────────────────────────────
class ResearchRequest(BaseModel):
    query: str

class DocumentResponse(BaseModel):
    content: str
    source: str
    relevance_score: float

class CriticResponse(BaseModel):
    verdict: str
    overall_score: float
    issues: List[str]
    missing_topics: List[str]
    improvement_instruction: str

class ResearchResponse(BaseModel):
    final_answer: str
    confidence_score: float
    iteration_count: int
    sub_questions: List[str]
    rewritten_queries: List[str]
    raw_documents: List[DocumentResponse]
    context_summary: str
    draft_answer: str
    critic_result: Optional[CriticResponse]
    errors: List[str]
    success: bool

# ── Helper: serialize pipeline state ────────────────────────
def serialize_state(state: dict) -> dict:
    """Convert LangGraph state (with Pydantic objects) to JSON-safe dict."""
    
    # Serialize raw_documents
    raw_docs = state.get("raw_documents", [])
    docs_serialized = []
    for doc in raw_docs:
        if isinstance(doc, dict):
            docs_serialized.append(doc)
        else:
            docs_serialized.append({
                "content": getattr(doc, "content", ""),
                "source": getattr(doc, "source", "unknown"),
                "relevance_score": getattr(doc, "relevance_score", 0.0)
            })
    
    # Serialize critic_result
    critic = state.get("critic_result", None)
    critic_serialized = None
    if critic:
        if isinstance(critic, dict):
            critic_serialized = critic
        else:
            critic_serialized = {
                "verdict": getattr(critic, "verdict", "unknown"),
                "overall_score": getattr(critic, "overall_score", 0.0),
                "issues": getattr(critic, "issues", []),
                "missing_topics": getattr(critic, "missing_topics", []),
                "improvement_instruction": getattr(critic, "improvement_instruction", "")
            }
    
    return {
        "final_answer": state.get("final_answer") or state.get("draft_answer", "No final answer generated."),
        "confidence_score": state.get("confidence_score", 0.0),
        "iteration_count": state.get("iteration_count", 0),
        "sub_questions": state.get("sub_questions", []),
        "rewritten_queries": state.get("rewritten_queries", []),
        "raw_documents": docs_serialized,
        "context_summary": state.get("context_summary", ""),
        "draft_answer": state.get("draft_answer", ""),
        "critic_result": critic_serialized,
        "errors": state.get("errors", []),
        "success": len(state.get("errors", [])) == 0
    }

# ── Routes ───────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    groq_key = os.environ.get("GROQ_API_KEY", "")
    tavily_key = os.environ.get("TAVILY_API_KEY", "")
    return {
        "status": "ok",
        "groq_configured": bool(groq_key),
        "tavily_configured": bool(tavily_key)
    }


@app.post("/api/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured on the server.")
    
    try:
        graph = build_research_graph()
        initial_state = {"user_query": query}
        final_state = graph.invoke(initial_state)
        return serialize_state(final_state)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


# ── Run directly ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
