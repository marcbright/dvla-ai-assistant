"""Google Gemini API wrapper for model interactions.

This module will encapsulate model initialization, request formatting,
response handling, and error management for Gemini API calls.
"""

from __future__ import annotations

import re
from typing import Generator

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

from config import settings
from knowledge.dvla_knowledge import DVLAKnowledgeBase
from utils.logger import log_audit, logger

from .prompt_builder import PromptBuilder

_MAX_INPUT_CHARS = 500
_INPUT_BLOCKLIST = (
    "recipe",
    "weather",
    "sports",
    "politics",
    "stock",
    "cryptocurrency",
    "bitcoin",
    "investment advice",
    "diagnosis",
    "prescription",
)
_FEE_OR_LEGAL_HINT = re.compile(
    r"\b("
    r"GHS|ghs|cedis?|gh¢|¢|"
    r"fee|fees|cost|charge|charges|penalt|penalties|fine|fines|"
    r"required documents?|documents required|must provide|shall provide|"
    r"legal requirement|under the law|pursuant to|Act\s*683|road traffic act"
    r")\b",
    re.IGNORECASE,
)
_CODE_FENCE = re.compile(r"```[\s\S]*?```", re.MULTILINE)


class AIEngine:
    """Gemini-backed AI engine for DVLA Ghana conversations."""

    def __init__(self) -> None:
        """Configure Gemini client and initialize model with system prompt."""
        self.prompt_builder = PromptBuilder()
        self.knowledge_base = DVLAKnowledgeBase()
        self.system_prompt = self.prompt_builder.build_system_prompt(
            self.knowledge_base.get_system_context()
        )

        genai.configure(api_key=settings.GEMINI_API_KEY)
        generation_config = genai.GenerationConfig(
            max_output_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
        )
        self.model = genai.GenerativeModel(
            model_name=settings.MODEL_NAME,
            system_instruction=self.system_prompt,
            generation_config=generation_config,
        )

    def pre_check_input(self, user_input: str) -> tuple[bool, str]:
        """Validate user input before calling the model API.

        Returns (True, "") when the message may proceed, or (False, reason)
        when it should be blocked with a user-facing explanation.
        """
        if len(user_input) > _MAX_INPUT_CHARS:
            log_audit(
                f"pre_check_input blocked: length_exceeded len={len(user_input)} "
                f"max={_MAX_INPUT_CHARS}"
            )
            return (
                False,
                f"Your message is too long. Please keep questions to {_MAX_INPUT_CHARS} "
                "characters or fewer, then try again.",
            )

        lowered = user_input.lower()
        for keyword in _INPUT_BLOCKLIST:
            if re.search(rf"\b{re.escape(keyword)}\b", lowered):
                log_audit(f"pre_check_input blocked: keyword='{keyword}'")
                return (
                    False,
                    "DVLA Assist only answers questions about DVLA Ghana services "
                    "(licensing, registration, roadworthiness, and related traffic "
                    "information). For other topics, please use an appropriate service "
                    "or visit https://www.dvlaghana.gov.gh for official DVLA contact options.",
                )

        log_audit("pre_check_input passed")
        return (True, "")

    def post_process_response(self, response: str) -> str:
        """Normalize model output: disclaimers, sentence closure, markdown cleanup."""
        original = response
        text = response.strip()

        # 1) Strip accidental fenced code / stray backticks first
        text = _CODE_FENCE.sub("", text)
        text = text.replace("```", "")
        text = text.strip()
        if text != original.strip():
            log_audit("post_process_response: stripped_code_fences_or_artifacts")

        # 2) Append official disclaimer when discussing fees or legal-style requirements
        disclaimer = self.knowledge_base.get_disclaimer().strip()
        needs_disclaimer = bool(_FEE_OR_LEGAL_HINT.search(text)) and bool(disclaimer)
        if needs_disclaimer and disclaimer not in text:
            text = f"{text.rstrip()}\n\n{disclaimer}"
            log_audit("post_process_response: appended_disclaimer_fee_or_legal_content")

        # 3) Avoid an abrupt non-terminal ending on substantive replies
        stripped = text.rstrip()
        if stripped and stripped[-1] not in ".!?…":
            text = f"{stripped}."
            log_audit("post_process_response: ensured_terminal_punctuation")

        return text.strip()

    def stream_response(
        self, user_message: str, chat_history: list
    ) -> Generator[str, None, None]:
        """Send a streaming Gemini request and yield text chunks."""
        ok, reason = self.pre_check_input(user_message)
        if not ok:
            yield reason
            return

        converted_history = self.prompt_builder.build_conversation_history(chat_history)
        collected_chunks: list[str] = []

        try:
            chat = self.model.start_chat(history=converted_history)
            response = chat.send_message(user_message, stream=True)

            for chunk in response:
                text = (chunk.text or "").strip()
                if not text:
                    continue
                collected_chunks.append(text)

            if not collected_chunks:
                logger.error("Gemini returned an empty streaming response.")
                raise ValueError("Empty response received from Gemini.")

            raw_full = "".join(collected_chunks)
            processed = self.post_process_response(raw_full)
            if processed != raw_full:
                log_audit("stream_response: post_process adjusted streamed reply")

            logger.info(
                "Stream request='{}' | response='{}'",
                user_message,
                processed,
            )

            chunk_size = 72
            for start in range(0, len(processed), chunk_size):
                yield processed[start : start + chunk_size]
        except GoogleAPIError as exc:
            self._handle_google_api_error(exc)
        except ValueError:
            raise
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            logger.exception("Unexpected streaming error: {}", str(exc))
            raise RuntimeError("Unexpected error while streaming Gemini response.") from exc

    def get_response(self, user_message: str, chat_history: list) -> str:
        """Send a non-streaming Gemini request and return full text."""
        ok, reason = self.pre_check_input(user_message)
        if not ok:
            return reason

        converted_history = self.prompt_builder.build_conversation_history(chat_history)

        try:
            chat = self.model.start_chat(history=converted_history)
            response = chat.send_message(user_message)
            text = (response.text or "").strip()

            if not text:
                logger.error("Gemini returned an empty non-streaming response.")
                raise ValueError("Empty response received from Gemini.")

            processed = self.post_process_response(text)
            logger.info("Request='{}' | response='{}'", user_message, processed)
            return processed
        except GoogleAPIError as exc:
            self._handle_google_api_error(exc)
        except ValueError:
            raise
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            logger.exception("Unexpected non-streaming error: {}", str(exc))
            raise RuntimeError("Unexpected error while getting Gemini response.") from exc

    def _handle_google_api_error(self, error: GoogleAPIError) -> None:
        """Normalize common Google API error cases into clear exceptions."""
        message = str(error).lower()
        logger.exception("Google API error: {}", str(error))

        if "quota" in message or "resource exhausted" in message:
            raise RuntimeError(
                "Gemini quota exceeded. Please try again later or use another API key."
            ) from error

        if "api key" in message or "permission denied" in message or "unauthenticated" in message:
            raise RuntimeError(
                "Invalid Gemini API key or insufficient permission. "
                "Please verify GEMINI_API_KEY."
            ) from error

        if (
            "not found" in message
            or "is not found for api version" in message
            or "404" in message
            or type(error).__name__ == "NotFound"
        ):
            raise RuntimeError(
                f"The configured Gemini model ({settings.MODEL_NAME!r}) is not available "
                "for your API key or API version. Set MODEL_NAME in `.env` to a supported "
                "model (for example `gemini-2.5-flash` or `gemini-2.0-flash`) and restart."
            ) from error

        raise RuntimeError("Gemini API request failed. Please try again shortly.") from error
