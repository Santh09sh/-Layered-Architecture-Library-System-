"""
AI Agent
The LibraryAI agent that processes user queries using reasoning and tools.
Implements the controlled reasoning architecture:
  User Query → Intent → Tool Selection → Execution → Response
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.ai.llm_provider import LLMProvider
from app.ai.gemini_provider import GeminiProvider, MockProvider
from app.ai.tool_registry import ToolRegistry
from app.config import settings


SYSTEM_PROMPT = """You are LibraryAI, an intelligent library assistant for a university library management system.

Your role:
- Help users find books, check availability, get recommendations
- Answer questions about borrowing, returns, fines, and reservations
- Provide library statistics and insights
- Use the entity graph to find relationships between books, authors, and categories

CRITICAL RULES:
1. NEVER invent books, authors, or availability information
2. ALWAYS use tools to get real data before answering factual questions
3. NEVER reveal other users' private information
4. NEVER directly modify database records - only read operations
5. Explain your reasoning when making recommendations
6. If you don't have enough information, ask the user to clarify
7. Be friendly, helpful, and professional

When you need data, use the available tools. Format your responses clearly with proper formatting.
If a tool returns an error, explain it to the user in a friendly way.
"""


class LibraryAgent:
    """The main AI agent that orchestrates reasoning and tool usage."""

    def __init__(self, db: Session, user_id: Optional[int] = None):
        self.db = db
        self.user_id = user_id
        self.tool_registry = ToolRegistry(db, user_id)
        self.provider = self._get_provider()

    def _get_provider(self) -> LLMProvider:
        if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            return GeminiProvider()
        return MockProvider()

    async def chat(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Process a user message through the reasoning pipeline:
        1. Understand the query
        2. Select appropriate tools
        3. Execute tools
        4. Generate response from tool results
        """
        messages = conversation_history or []
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append({"role": "user", "content": user_message})

        tool_definitions = self.tool_registry.get_tool_definitions()
        tool_results = []
        steps = []

        # Step 1: Get LLM's initial response (may include tool calls)
        response = await self.provider.generate(messages, tools=tool_definitions)

        # Step 2: Execute any tool calls
        if response.get("tool_calls"):
            for tool_call in response["tool_calls"]:
                tool_name = tool_call.get("name", "")
                arguments = tool_call.get("arguments", {})

                steps.append({
                    "type": "tool_call",
                    "tool": tool_name,
                    "arguments": arguments,
                })

                result = self.tool_registry.execute_tool(tool_name, arguments)
                tool_results.append({
                    "tool": tool_name,
                    "result": result,
                })

                steps.append({
                    "type": "tool_result",
                    "tool": tool_name,
                    "result": result,
                })

        # Step 3: Generate final response using tool results
        if tool_results:
            tool_context = json.dumps(tool_results, indent=2, default=str)
            messages.append({
                "role": "assistant",
                "content": f"I called the following tools and got these results:\n{tool_context}\n\nNow I'll answer based on this real data."
            })

            final_response = await self.provider.generate(messages)
            answer = final_response.get("content", "")
        else:
            answer = response.get("content", "I'm here to help with the library. Ask me about books, borrowing, or recommendations!")

        # For mock provider, generate a structured response from tool results
        if isinstance(self.provider, MockProvider) and tool_results:
            answer = self._format_mock_response(user_message, tool_results)

        return {
            "response": answer,
            "tool_calls": tool_results,
            "reasoning_steps": steps,
        }

    def _format_mock_response(self, query: str, tool_results: List[Dict]) -> str:
        """Generate a helpful response from tool results when using mock provider."""
        parts = []
        lower = query.lower()

        for tr in tool_results:
            tool = tr["tool"]
            result = tr["result"]

            if "error" in result:
                parts.append(f"⚠️ {result['error']}")
                continue

            if tool == "search_books" and "results" in result:
                books = result["results"]
                if books:
                    parts.append(f"📚 I found **{len(books)}** books matching your query:\n")
                    for b in books[:5]:
                        authors = ", ".join(b.get("authors", []))
                        avail = b.get("available_copies", 0)
                        status = "✅ Available" if avail > 0 else "❌ Unavailable"
                        parts.append(f"• **{b['title']}** by {authors} — {status} ({avail} copies)")
                else:
                    parts.append("I couldn't find any books matching your query.")

            elif tool == "recommend_books" and "recommendations" in result:
                recs = result["recommendations"]
                if recs:
                    parts.append("📖 Based on your reading history, I recommend:\n")
                    for r in recs:
                        parts.append(f"• **{r['title']}** — {r['reason']} (⭐ {r.get('rating', 'N/A')})")
                else:
                    parts.append("I don't have enough data to make personalized recommendations yet.")

            elif tool == "get_user_borrowing_history" and "records" in result:
                records = result["records"]
                parts.append(f"📋 Your borrowing history ({len(records)} records):\n")
                for r in records[:5]:
                    parts.append(f"• **{r['book_title']}** — {r['status']} (Due: {r['due_date'][:10]})")

            elif tool == "get_overdue_books" and "records" in result:
                count = result.get("overdue_count", 0)
                parts.append(f"⚠️ There are **{count}** overdue books.\n")
                for r in result["records"][:5]:
                    parts.append(f"• **{r['book_title']}** by {r['user_name']} — {r.get('days_overdue', 0)} days overdue")

            elif tool == "calculate_fine":
                total = result.get("total_unpaid", 0)
                if total > 0:
                    parts.append(f"💰 You have **${total:.2f}** in unpaid fines.")
                else:
                    parts.append("✅ You have no pending fines!")

            elif tool == "get_library_statistics":
                parts.append("📊 **Library Statistics:**\n")
                parts.append(f"• Total Books: {result.get('total_books', 0)}")
                parts.append(f"• Active Borrows: {result.get('books_borrowed', 0)}")
                parts.append(f"• Overdue: {result.get('overdue_books', 0)}")
                parts.append(f"• Active Members: {result.get('active_members', 0)}")

            elif tool == "check_borrowing_eligibility":
                if result.get("eligible"):
                    parts.append(f"✅ You're eligible to borrow! ({result.get('active_borrows', 0)}/{result.get('max_borrows', 5)} slots used)")
                else:
                    parts.append("❌ You're not currently eligible to borrow:")
                    for reason in result.get("reasons", []):
                        parts.append(f"  • {reason}")

        return "\n".join(parts) if parts else "I processed your request. Is there anything specific you'd like to know?"

    def get_available_tools(self) -> List[Dict]:
        """Return the list of tools available to this agent."""
        return self.tool_registry.get_tool_definitions()
