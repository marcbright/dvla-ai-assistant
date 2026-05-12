"""Reusable Streamlit UI building blocks.

This module will hold shared UI components such as headers, cards,
input blocks, and response containers for the main application.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from knowledge.dvla_knowledge import DVLAKnowledgeBase


def render_header() -> None:
    """Render the branded app header section."""
    st.markdown(
        """
<div class="dvla-header">
  <div>
    <div class="dvla-header__brand">🇬🇭 DVLA Assist — Ghana Driver & Vehicle Authority AI</div>
    <div class="dvla-header__subtitle">
      Your 24/7 guide to licensing, registration, and road traffic services
    </div>
  </div>
</div>
<div class="dvla-divider"></div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(knowledge_base: DVLAKnowledgeBase) -> None:
    """Render sidebar sections for quick actions, info, and links."""
    st.session_state.setdefault("pending_question", None)

    with st.sidebar:
        st.markdown("### 🇬🇭 DVLA Assist")
        st.caption("Official-style support assistant for DVLA Ghana services")
        st.divider()

        st.markdown("### Quick Topics")
        quick_topics = knowledge_base.get_quick_topics()
        for category, questions in quick_topics.items():
            with st.expander(category, expanded=False):
                for idx, question in enumerate(questions):
                    if st.button(
                        question,
                        key=f"quick-topic-{category}-{idx}",
                        use_container_width=True,
                    ):
                        st.session_state["pending_question"] = question

        st.divider()
        st.markdown("### About DVLA Assist")
        st.markdown(
            (
                "DVLA Assist helps users navigate driver licensing, vehicle registration, "
                "roadworthiness, and traffic compliance processes in Ghana."
            )
        )
        st.caption(knowledge_base.get_disclaimer())

        st.divider()
        st.markdown("### Useful Links")
        st.markdown("- [DVLA Ghana Official Portal](https://www.dvlaghana.gov.gh)")
        st.markdown("- [DVLA Ghana Facebook](https://www.facebook.com/DVLAGhana)")
        st.markdown("- [Ghana Government Portal](https://www.ghana.gov.gh)")
        st.markdown("- [Motor Traffic and Transport Department (MTTD)](https://police.gov.gh)")

        st.divider()
        if st.button("Clear Chat", key="clear-chat", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["feedback"] = {}
            st.session_state["pending_question"] = None


def render_chat_message(role: str, content: str, timestamp: str) -> None:
    """Render one user or assistant message bubble with metadata."""
    role_normalized = role.strip().lower()
    is_assistant = role_normalized in {"assistant", "model"}
    bubble_class = "chat-assistant" if is_assistant else "chat-user"
    avatar = "🏛️" if is_assistant else "👤"
    label = "DVLA Assist" if is_assistant else "You"

    safe_timestamp = timestamp.strip() if timestamp.strip() else datetime.now().strftime("%H:%M")

    st.markdown(
        f"""
<div class="{bubble_class}">
  <div class="chat-meta">
    <span>{avatar}</span>
    <span>{label}</span>
    <span class="chat-timestamp">{safe_timestamp}</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    # Render markdown as requested, outside the HTML block for Streamlit safety.
    st.markdown(content)


def render_typing_indicator() -> None:
    """Render animated typing indicator while assistant response streams."""
    st.markdown(
        """
<div class="typing-indicator" aria-label="Assistant is typing">
  <span></span><span></span><span></span>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_feedback_buttons(message_index: int) -> None:
    """Render thumbs feedback controls for assistant responses."""
    st.session_state.setdefault("feedback", {})
    col_up, col_down, _ = st.columns([1, 1, 6])

    with col_up:
        if st.button("👍", key=f"feedback-up-{message_index}"):
            st.session_state["feedback"][message_index] = "up"

    with col_down:
        if st.button("👎", key=f"feedback-down-{message_index}"):
            st.session_state["feedback"][message_index] = "down"


def render_footer() -> None:
    """Render muted app footer and attribution."""
    st.markdown(
        """
<div class="dvla-footer">
  Powered by Bright Osei Kesse | DVLA Ghana AI Assistant | Not official DVLA output
</div>
        """,
        unsafe_allow_html=True,
    )
