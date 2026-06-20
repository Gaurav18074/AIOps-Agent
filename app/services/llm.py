from app.config import settings


def get_llm():
    """Return a configured LangChain LLM client."""
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )
    elif settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
            temperature=0.2,
        )
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
