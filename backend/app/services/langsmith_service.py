import os
from langsmith.wrappers import wrap_openai
from langsmith import traceable
import openai

# Lazy initialization of OpenAI client
_client = None


def get_client():
    """Get or create the LangSmith-wrapped OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _base_client = openai.OpenAI(api_key=api_key)
        _client = wrap_openai(_base_client)
    return _client


@traceable(name="create_completion")
def traced_completion(*args, **kwargs):
    """Wrapper to ensure completions are traced in LangSmith."""
    return get_client().chat.completions.create(*args, **kwargs)


__all__ = ["get_client", "traceable", "traced_completion"]
