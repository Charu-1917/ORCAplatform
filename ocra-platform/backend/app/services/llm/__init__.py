"""
Local LLM services (Ollama) for ORCA Marine Engine backend.
"""
from app.services.llm.ollama_client import ollama_client, OllamaUnavailable

__all__ = ["ollama_client", "OllamaUnavailable"]
