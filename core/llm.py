from config.settings import settings
from langchain_groq import ChatGroq

client = None

if getattr(settings, "GROQ_API_KEY", None):
    client = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=getattr(settings, "LLM_MODEL", "openai/gpt-oss-120b"),
        temperature=0.3
    )


def get_planner_llm():
    return client

def get_rewriter_llm():
    return client


def call_llm(llm_client, system: str, user: str, json_mode: bool = False, max_tokens: int = 1000) -> str:
   
    if not llm_client:
        return "Simulated LLM Response: Please configure your GROQ_API_KEY in .env."

    try:
        messages = [
            ("system", system),
            ("human", user)
        ]

        response = llm_client.invoke(messages)
        content = response.content if response else ""

        return content.strip() if content else ""

    except Exception as e:
        print(f"LLM Call Failed: {e}")
        return "{}" if json_mode else ""
