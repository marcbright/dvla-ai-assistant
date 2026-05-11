"""Core package for AI orchestration and prompt construction.

This package will provide the abstraction layers needed to build prompts
and communicate with the configured large language model provider.
"""

from .ai_engine import AIEngine
from .prompt_builder import PromptBuilder

__all__ = ["AIEngine", "PromptBuilder"]
