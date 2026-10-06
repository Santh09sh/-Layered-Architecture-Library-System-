"""
AI Agent Chat Page
Chat interface for LibraryAI with tool call visualization.
"""

import streamlit as st
import json


def render(api):
    """Render the AI agent chat page."""

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px;">
        <div style="width: 48px; height: 48px; border-radius: 14px; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 14px rgba(99,102,241,0.3);">
            🤖
        </div>
        <div>
            <h2 style="margin: 0 !important; font-size: 24px !important;">
                LibraryAI <span style="font-size: 16px; color: #fbbf24;">✨</span>
            </h2>
            <p style="margin: 0 !important; color: #64748b; font-size: 13px !important;">
                Intelligent library assistant powered by AI
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Initialize Chat History ───────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm **LibraryAI**, your intelligent library assistant. I can help you:\n\n"
                           "• 📚 Search and find books\n"
                           "• ✅ Check book availability\n"
                           "• 📖 Get personalized recommendations\n"
                           "• 📊 View library statistics\n"
                           "• 💰 Check your fines\n"
                           "• 🔍 Explore the entity graph\n\n"
                           "Ask me anything about the library!",
                "tool_calls": None,
            }
        ]

    # ── Suggestions (only shown when chat is fresh) ───────────────────────
    if len(st.session_state.chat_messages) <= 1:
        st.markdown('<p style="color: #64748b; font-size: 12px !important; margin-bottom: 8px;">💡 Suggestions</p>', unsafe_allow_html=True)
        suggestions = [
            "Which books about AI are available?",
            "Recommend books for me",
            "Show my borrowing history",
            "What are the library statistics?",
            "Check my fines",
            "Who are the most borrowed authors?",
        ]
        suggestion_cols = st.columns(3)
        for idx, suggestion in enumerate(suggestions):
            with suggestion_cols[idx % 3]:
                if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                    st.session_state.pending_message = suggestion
                    st.rerun()

        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    # ── Chat History Display ──────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for idx, msg in enumerate(st.session_state.chat_messages):
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 12px 0;">
                    <div class="chat-user" style="max-width: 75%;">
                        {_format_message(msg["content"])}
                    </div>
                    <div style="width: 32px; height: 32px; border-radius: 10px; background: linear-gradient(135deg, #10b981, #14b8a6); display: flex; align-items: center; justify-content: center; margin-left: 10px; flex-shrink: 0; font-size: 14px;">
                        👤
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 12px 0;">
                    <div style="width: 32px; height: 32px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; margin-right: 10px; flex-shrink: 0; font-size: 14px;">
                        🤖
                    </div>
                    <div class="chat-bot" style="max-width: 75%;">
                        {_format_message(msg["content"])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Tool calls
                if msg.get("tool_calls"):
                    with st.expander(f"🔧 {len(msg['tool_calls'])} tool{'s' if len(msg['tool_calls']) > 1 else ''} used"):
                        for tc in msg["tool_calls"]:
                            tool_name = tc.get("tool", "unknown")
                            result = tc.get("result", {})
                            st.markdown(f"""
                            <div class="glass-card" style="padding: 10px 14px; margin-bottom: 8px;">
                                <code style="color: #818cf8; font-size: 13px !important;">{tool_name}</code>
                            </div>
                            """, unsafe_allow_html=True)
                            if result and not result.get("error"):
                                result_str = json.dumps(result, indent=2)
                                if len(result_str) > 500:
                                    result_str = result_str[:500] + "..."
                                st.code(result_str, language="json")

    # ── Input ─────────────────────────────────────────────────────────────
    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    # Handle pending message from suggestion
    pending = st.session_state.pop("pending_message", None)
    if pending:
        _send_message(api, pending)
        st.rerun()

    # Chat input
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Message",
            placeholder="Ask LibraryAI anything...",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_send:
        send_clicked = st.button("📤 Send", use_container_width=True, key="chat_send")

    if send_clicked and user_input.strip():
        _send_message(api, user_input.strip())
        st.rerun()

    # Clear chat button
    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
    if len(st.session_state.chat_messages) > 1:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()


def _send_message(api, message: str):
    """Send a message to the AI agent and store the response."""
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": message,
        "tool_calls": None,
    })

    # Call API
    try:
        result = api.agent_chat(message)
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": result.get("response", "I couldn't process that request."),
            "tool_calls": result.get("tool_calls"),
        })
    except Exception as e:
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
            "tool_calls": None,
        })


def _format_message(content: str) -> str:
    """Format message content with basic markdown-like rendering."""
    import html
    content = html.escape(content)
    # Bold
    import re
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #f1f5f9;">\1</strong>', content)
    # Newlines
    content = content.replace("\n", "<br>")
    return f'<div style="font-size: 14px !important; line-height: 1.7 !important;">{content}</div>'
