"""
Google Gemini LLM Provider
Concrete implementation of LLMProvider for Google Gemini.
"""

import json
from typing import List, Dict, Any, Optional
from app.ai.llm_provider import LLMProvider
from app.config import settings


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.LLM_MODEL
        self._client = None

    def _get_client(self):
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured. Set it in .env file.")
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
        return self._client

    async def generate(self, messages: List[Dict[str, str]],
                       tools: Optional[List[Dict]] = None,
                       temperature: float = 0.3) -> Dict[str, Any]:
        client = self._get_client()

        # Convert messages to Gemini format
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role}: {content}")

        prompt = "\n".join(prompt_parts)

        # If tools are provided, include them in the prompt
        if tools:
            tool_descriptions = json.dumps(tools, indent=2)
            prompt += f"\n\nAvailable tools:\n{tool_descriptions}"
            prompt += "\n\nIf you need to use a tool, respond with a JSON object: {\"tool_call\": {\"name\": \"tool_name\", \"arguments\": {...}}}"
            prompt += "\nIf you don't need a tool, just respond normally."

        try:
            response = client.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            text = response.text

            # Try to parse tool calls from response
            tool_calls = []
            if tools and '"tool_call"' in text:
                try:
                    # Extract JSON from response
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    if start >= 0 and end > start:
                        parsed = json.loads(text[start:end])
                        if "tool_call" in parsed:
                            tool_calls.append(parsed["tool_call"])
                except json.JSONDecodeError:
                    pass

            return {
                "content": text,
                "tool_calls": tool_calls,
            }
        except Exception as e:
            return {
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "tool_calls": [],
            }

    async def generate_simple(self, prompt: str) -> str:
        client = self._get_client()
        try:
            response = client.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"


class MockProvider(LLMProvider):
    """
    Mock LLM provider for demo/testing.
    Uses rule-based responses when no API key is available.
    """

    async def generate(self, messages: List[Dict[str, str]],
                       tools: Optional[List[Dict]] = None,
                       temperature: float = 0.3) -> Dict[str, Any]:
        last_message = messages[-1]["content"] if messages else ""
        lower = last_message.lower()

        # Simple keyword-based tool selection
        tool_calls = []
        if tools:
            if any(w in lower for w in ["borrow", "check out", "available", "can i"]):
                tool_calls.append({"name": "search_books", "arguments": {"query": last_message}})
            elif any(w in lower for w in ["overdue", "late", "due"]):
                tool_calls.append({"name": "get_overdue_books", "arguments": {}})
            elif any(w in lower for w in ["recommend", "suggest", "similar"]):
                tool_calls.append({"name": "recommend_books", "arguments": {}})
            elif any(w in lower for w in ["history", "borrowed", "reading"]):
                tool_calls.append({"name": "get_user_borrowing_history", "arguments": {}})
            elif any(w in lower for w in ["fine", "payment", "owe"]):
                tool_calls.append({"name": "calculate_fine", "arguments": {}})
            elif any(w in lower for w in ["statistic", "stats", "analytics"]):
                tool_calls.append({"name": "get_library_statistics", "arguments": {}})
            elif any(w in lower for w in ["search", "find", "look"]):
                tool_calls.append({"name": "search_books", "arguments": {"query": last_message}})

        return {
            "content": "",
            "tool_calls": tool_calls,
        }

    async def generate_simple(self, prompt: str) -> str:
        return "I'm a mock AI assistant. Configure a Gemini API key for full AI capabilities."
