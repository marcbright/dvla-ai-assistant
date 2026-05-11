"""Streamlit entry point for the DVLA AI Assistant application.

This module will initialize the app layout, orchestrate UI interactions,
and connect user inputs to the AI and domain-knowledge layers.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from core.ai_engine import AIEngine
from knowledge.dvla_knowledge import DVLAKnowledgeBase
from ui.components import (
    render_chat_message,
    render_feedback_buttons,
    render_footer,
    render_header,
    render_sidebar,
    render_typing_indicator,
)
from ui.styles import inject_custom_css


def _timestamp_now() -> str:
    """Return a compact local timestamp string for chat messages."""
    return datetime.now().strftime("%H:%M")


def _initialize_session_state() -> None:
    """Initialize persistent app session state once."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    if "retry_last_message" not in st.session_state:
        st.session_state.retry_last_message = None


def _render_chat_history() -> None:
    """Render full chat transcript from session state."""
    for idx, message in enumerate(st.session_state.messages):
        role = message.get("role", "")
        content = message.get("content", "")
        timestamp = message.get("timestamp", "")
        render_chat_message(role=role, content=content, timestamp=timestamp)

        if role in {"assistant", "model"}:
            render_feedback_buttons(idx)


def _resolve_user_input() -> str | None:
    """Resolve input from chat box or pending sidebar quick-topic click."""
    typed_prompt = st.chat_input("Ask me anything about DVLA Ghana...")
    pending = st.session_state.pending_question
    if pending:
        st.session_state.pending_question = None
        return str(pending).strip() or None
    if typed_prompt:
        return typed_prompt.strip() or None
    return None


def _stream_assistant_reply(ai_engine: AIEngine, user_message: str, chat_history: list[dict]) -> str:
    """Stream assistant reply into placeholder and return final text."""
    reply_box = st.empty()
    typing_box = st.empty()
    typing_box.markdown(
        """
<div class="typing-indicator" aria-label="Assistant is typing">
  <span></span><span></span><span></span>
</div>
        """,
        unsafe_allow_html=True,
    )
    full_response = ""

    try:
        for chunk in ai_engine.stream_response(
            user_message=user_message,
            chat_history=chat_history,
        ):
            full_response += chunk
            preview = full_response + "▌"
            reply_box.markdown(
                f'<div class="chat-assistant"><div class="chat-meta"><span>🏛️</span>'
                f'<span>DVLA Assist</span><span class="chat-timestamp">{_timestamp_now()}</span>'
                f"</div>{preview}</div>",
                unsafe_allow_html=True,
            )
    finally:
        typing_box.empty()

    return full_response.strip()


def main() -> None:
    """Run the DVLA Assist Streamlit application."""
    st.set_page_config(
        page_title="DVLA Assist | Ghana",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _initialize_session_state()

    inject_custom_css()
    render_header()

    knowledge_base = DVLAKnowledgeBase()
    render_sidebar(knowledge_base=knowledge_base)

    _render_chat_history()

    user_prompt = _resolve_user_input()
    if not user_prompt and st.session_state.retry_last_message:
        user_prompt = st.session_state.retry_last_message
        st.session_state.retry_last_message = None

    if user_prompt:
        user_message = {
            "role": "user",
            "content": user_prompt,
            "timestamp": _timestamp_now(),
        }
        st.session_state.messages.append(user_message)
        render_chat_message(
            role=user_message["role"],
            content=user_message["content"],
            timestamp=user_message["timestamp"],
        )

        try:
            ai_engine = AIEngine()
            history_before_current_turn = st.session_state.messages[:-1]
            assistant_text = _stream_assistant_reply(
                ai_engine=ai_engine,
                user_message=user_prompt,
                chat_history=history_before_current_turn,
            )
            if not assistant_text:
                raise ValueError("Assistant returned an empty response.")

            assistant_message = {
                "role": "assistant",
                "content": assistant_text,
                "timestamp": _timestamp_now(),
            }
            st.session_state.messages.append(assistant_message)
            render_feedback_buttons(len(st.session_state.messages) - 1)
            st.rerun()
        except Exception as error:
            st.warning(f"Unable to complete your request right now: {error}")
            st.session_state.retry_last_message = user_prompt
            if st.button("Retry last message", key="retry-last-message"):
                st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
