import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",           # Looks for this file in the root
        env_file_encoding="utf-8",
        extra="ignore"             # Ignores extra variables in .env
    )

    # --- API Keys ---
    GROQ_API_KEY: str = Field(default="")
    TAVILY_API_KEY: str = Field(default="")

    # --- Search Settings ---
    SEARCH_PROVIDER: str = "tavily"
    TOP_K_RESULTS: int = 5

    # --- LLM Settings ---
    LLM_MODEL: str = "openai/gpt-oss-120b"
    MAX_ITERATIONS: int = 3

    # --- Path Helpers ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CHROMA_DB_PATH: str = "./data/chroma_db"

    @property
    def active_search_key(self) -> str:
        """Returns the Tavily key for the WebSearchTool."""
        return self.TAVILY_API_KEY

    @property
    def has_groq(self) -> bool:
        return bool(self.GROQ_API_KEY)


# Initialize the settings instance
settings = Settings()
