"""This module handles creation of llm object from type.
"""
import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOllama 

temperature = float(os.environ.get("TEMPERATURE", 0.01))
llm_provider = os.environ.get("LLM_PROVIDER", "ollama").lower()

def build_llm(llm_type: str) -> BaseChatModel:
    """Builds an llm object based on the configured provider (openai or ollama).

    Args:
        llm_type: A string indicating the model name (e.g., "gpt-3.5-turbo", "llama3").

    Returns:
        A chat model instance.
    """
    if llm_provider == "ollama":
        print("Building Ollama LLM...")
        # To connect to Ollama running on the host from inside a Docker container,
        # we use 'host.docker.internal'. The OLLAMA_BASE_URL env var can override this.
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        llm = ChatOllama(
            base_url=ollama_base_url,
            model=llm_type,
            temperature=temperature,
        )
    elif llm_provider == "openai":
        print("Building OpenAI LLM...")
        llm = ChatOpenAI(model_name=llm_type, temperature=temperature)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {llm_provider}. Please choose 'openai' or 'ollama'.")

    return llm
