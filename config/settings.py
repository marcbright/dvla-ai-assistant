"""Environment-driven application settings for DVLA Assist.

Loads variables from a local ``.env`` file via python-dotenv and exposes a
single module-level ``settings`` instance for use across the codebase.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _merge_streamlit_secrets_into_environ() -> None:
    """Fill missing os.environ entries from Streamlit Community Cloud secrets.

    Local development keeps using ``.env`` via ``load_dotenv()`` above. On Streamlit Cloud,
    secrets are configured in the app dashboard and exposed as ``st.secrets``; we mirror
    supported keys into the environment so the rest of the app stays unchanged.
    """
    try:
        import streamlit as st
    except ImportError:
        return
    try:
        secrets = st.secrets
    except Exception:
        return
    if not secrets:
        return

    keys = (
        "GEMINI_API_KEY",
        "MODEL_NAME",
        "DEBUG",
        "LOG_LEVEL",
        "APP_NAME",
        "APP_VERSION",
        "MAX_TOKENS",
        "TEMPERATURE",
        "MAX_HISTORY_TURNS",
    )

    def push_from_mapping(mapping: object) -> None:
        if not isinstance(mapping, dict):
            return
        for key in keys:
            if key not in mapping:
                continue
            val = mapping.get(key)
            if val is None:
                continue
            text = str(val).strip()
            if not text:
                continue
            if not os.getenv(key):
                os.environ[key] = text

    try:
        mapping = {k: secrets[k] for k in keys if k in secrets}
        push_from_mapping(mapping)
    except Exception:
        pass

    try:
        nested = secrets["dvla"]
    except Exception:
        nested = None
    push_from_mapping(nested if isinstance(nested, dict) else None)


_merge_streamlit_secrets_into_environ()


def _parse_bool(raw: str | None, default: bool) -> bool:
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(raw: str | None, default: int) -> int:
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _parse_float(raw: str | None, default: float) -> float:
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


@dataclass
class Settings:
    """Central configuration loaded from environment variables."""

    APP_NAME: str = "DVLA Assist"
    APP_VERSION: str = "1.0.0"
    GEMINI_API_KEY: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip())
    MODEL_NAME: str = "gemini-2.5-flash"
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.3
    MAX_HISTORY_TURNS: int = 5
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    def __post_init__(self) -> None:
        """Apply env overrides and validate required fields."""
        object.__setattr__(self, "APP_NAME", os.getenv("APP_NAME", self.APP_NAME))
        object.__setattr__(self, "APP_VERSION", os.getenv("APP_VERSION", self.APP_VERSION))

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. For local development, copy `.env.example` to "
                "`.env` and set GEMINI_API_KEY. For Streamlit Community Cloud, add it under "
                "App settings → Secrets (see README)."
            )
        object.__setattr__(self, "GEMINI_API_KEY", api_key)

        object.__setattr__(self, "MODEL_NAME", os.getenv("MODEL_NAME", self.MODEL_NAME))
        object.__setattr__(
            self,
            "MAX_TOKENS",
            _parse_int(os.getenv("MAX_TOKENS"), self.MAX_TOKENS),
        )
        object.__setattr__(
            self,
            "TEMPERATURE",
            _parse_float(os.getenv("TEMPERATURE"), self.TEMPERATURE),
        )
        object.__setattr__(
            self,
            "MAX_HISTORY_TURNS",
            _parse_int(os.getenv("MAX_HISTORY_TURNS"), self.MAX_HISTORY_TURNS),
        )
        object.__setattr__(self, "LOG_LEVEL", os.getenv("LOG_LEVEL", self.LOG_LEVEL).upper())
        object.__setattr__(
            self,
            "DEBUG",
            _parse_bool(os.getenv("DEBUG"), self.DEBUG),
        )


settings = Settings()
