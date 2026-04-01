import logging
import os
from langchain_chroma import Chroma
from config.settings import settings
from core.state import SourceDocument

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        from .embeddings import get_embedding_function
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        self.db = Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            embedding_function=get_embedding_function()
        )

    def search(self, hyde_query: str, k: int = 2) -> list:
        try:
            results = self.db.similarity_search_with_score(hyde_query, k=k)
            docs = []
            for doc, score in results:
                docs.append(
                    SourceDocument(
                        content=doc.page_content,
                        source=doc.metadata.get("source", "local_chroma_db"),
                        relevance_score=max(0.01, round(1.0 - score, 3))
                    )
                )
            return docs

        except Exception as e:
            logger.error(f"Chroma search failed: {e}")
            return []