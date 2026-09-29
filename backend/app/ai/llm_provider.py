"""
LLM Provider Abstraction
Defines the interface for LLM providers so they can be swapped.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]],
                       tools: Optional[List[Dict]] = None,
                       temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            messages: Conversation history
            tools: Available tool definitions
            temperature: Creativity parameter

        Returns:
            Dict with 'content' (text response) and optionally 'tool_calls'
        """
        pass

    @abstractmethod
    async def generate_simple(self, prompt: str) -> str:
        """Generate a simple text response."""
        pass
