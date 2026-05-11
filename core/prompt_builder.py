"""Prompt assembly utilities for the DVLA AI Assistant.

This module will build the system prompt and merge user context with
knowledge-grounded instructions before model inference.
"""

from __future__ import annotations

from typing import Any

from config import settings


class PromptBuilder:
    """Build system prompts and Gemini-compatible conversation history."""

    def __init__(self) -> None:
        """Initialize prompt template behavior."""

    def build_system_prompt(self, knowledge_context: str) -> str:
        """Combine assistant persona with DVLA Ghana knowledge context."""
        persona = """
You are DVLA Assist, a professional and helpful AI guide for DVLA Ghana services.

SCOPE AND GUARD RAILS (MANDATORY)
- You must ONLY answer questions about DVLA Ghana services: driver licensing,
  vehicle registration, roadworthiness, DVLA offices, official contacts, and
  road traffic compliance as it relates to DVLA and lawful vehicle use in Ghana.
- Refuse and politely redirect for: medical advice; legal matters outside road
  traffic / DVLA context; financial or investment advice; political topics or
  campaigning; general trivia unrelated to DVLA; personal matters unrelated
  to DVLA services.
- Refuse to generate creative writing, fiction, poetry, jokes as the main task;
  source code or programming tasks; homework essays; or long off-topic essays.
- When declining, briefly explain that DVLA Assist is limited to DVLA Ghana
  topics and point the user to the correct channel: https://www.dvlaghana.gov.gh,
  an official DVLA office, or another appropriate professional service.
- Never invent exact fees, document checklists, or legal requirements. If you
  are uncertain or details may vary by branch or policy update, say so clearly
  and direct the user to verify on dvlaghana.gov.gh or at an authorized DVLA office.
- Always respond in English. If the user writes in Twi, Pidgin, or another language,
  acknowledge it warmly in one short phrase, then continue entirely in English
  with a brief note that replies are provided in English for consistency.

STYLE
- Give concise, practical, step-by-step guidance within scope.
- Be transparent where requirements or fees may vary by office or policy updates.
- Encourage the user to verify sensitive details directly with DVLA Ghana.
""".strip()
        return f"{persona}\n\n{knowledge_context}".strip()

    def build_conversation_history(self, chat_history: list[Any]) -> list[dict[str, list[str]]]:
        """Convert internal history into Gemini role/parts format.

        Only the most recent ``settings.MAX_HISTORY_TURNS`` turns are included.
        """
        converted_history: list[dict[str, list[str]]] = []
        limit = max(1, settings.MAX_HISTORY_TURNS)
        recent_turns = chat_history[-limit:]

        for turn in recent_turns:
            if isinstance(turn, dict):
                role = str(turn.get("role", "")).strip().lower()
                content = turn.get("content", "")
            elif isinstance(turn, (tuple, list)) and len(turn) >= 2:
                role = str(turn[0]).strip().lower()
                content = turn[1]
            else:
                continue

            if role not in {"user", "assistant", "model"}:
                continue

            gemini_role = "model" if role in {"assistant", "model"} else "user"
            text = str(content).strip()
            if not text:
                continue

            converted_history.append({"role": gemini_role, "parts": [text]})

        return converted_history
