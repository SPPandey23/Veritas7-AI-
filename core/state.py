import operator
from typing import List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    content: str
    source: str = "unknown"
    relevance_score: float = 0.0


class CriticResult(BaseModel):
   
    verdict: str = Field(default="needs_improvement", description="Must be 'good' or 'needs_improvement'")
    overall_score: float = Field(default=5.0, description="Score from 1-10")
    issues: List[str] = Field(default_factory=list)
    missing_topics: List[str] = Field(default_factory=list)
    improvement_instruction: str = Field(default="")

    @property
    def is_good(self) -> bool:
    
        return self.verdict == "good" or self.overall_score >= 7.0


class PipelineState(TypedDict):
    user_query: str
    sub_questions: List[str]
    rewritten_queries: List[str]
    hyde_passages: List[str]

    raw_documents: Annotated[List[SourceDocument], operator.add]

    context_summary: str
    draft_answer: str
    final_answer: str

    # Loop Control
    iteration_count: int
    critic_result: Optional[CriticResult]
    confidence_score: float

    # Error accumulation
    errors: Annotated[List[str], operator.add]