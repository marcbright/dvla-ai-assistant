"""Custom CSS injector utilities for Streamlit pages.

This module will define style helpers used to apply branding and
consistent visual themes throughout the application UI.
"""

from __future__ import annotations

import streamlit as st


def inject_custom_css() -> None:
    """Inject a professional DVLA Ghana-themed CSS stylesheet into Streamlit."""
    st.markdown(
        """
<style>
/* --------------------------------------------------------
   Fonts
   -------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* --------------------------------------------------------
   Theme variables: DVLA Ghana inspired palette
   -------------------------------------------------------- */
:root {
    --dvla-navy: #0A1628;
    --dvla-gold: #FCD116;
    --dvla-green: #006B3F;
    --dvla-red: #CE1126;
    --dvla-white: #FFFFFF;
    --dvla-surface: #F8F9FA;
    --dvla-text: #1F2937;
    --dvla-muted: #6B7280;
    --dvla-border: #E5E7EB;
    --dvla-shadow: 0 10px 30px rgba(10, 22, 40, 0.08);
    --dvla-radius-sm: 10px;
    --dvla-radius-md: 14px;
    --dvla-radius-lg: 18px;
}

/* --------------------------------------------------------
   App shell
   -------------------------------------------------------- */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.stApp {
    background: var(--dvla-white);
    color: var(--dvla-text);
}

/* Main content subtle surface */
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(180deg, var(--dvla-white) 0%, var(--dvla-surface) 100%);
}

/* --------------------------------------------------------
   Header bar
   -------------------------------------------------------- */
.dvla-header {
    width: 100%;
    background: var(--dvla-navy);
    color: var(--dvla-white);
    border-bottom: 4px solid var(--dvla-gold);
    padding: 0.9rem 1.2rem;
    border-radius: 0 0 var(--dvla-radius-md) var(--dvla-radius-md);
    box-shadow: var(--dvla-shadow);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.dvla-header__brand {
    font-weight: 700;
    letter-spacing: 0.2px;
}

.dvla-header__subtitle {
    color: rgba(255, 255, 255, 0.82);
    font-size: 0.92rem;
}

.dvla-divider {
    height: 6px;
    background: linear-gradient(90deg, var(--dvla-green) 0%, var(--dvla-gold) 100%);
    margin: 0.55rem 0 1rem 0;
    border-radius: 999px;
}

/* --------------------------------------------------------
   Sidebar
   -------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: var(--dvla-navy);
    border-right: 1px solid rgba(252, 209, 22, 0.2);
}

[data-testid="stSidebar"] * {
    color: var(--dvla-white);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown p {
    color: var(--dvla-white);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(252, 209, 22, 0.35);
}

[data-testid="stSidebar"] a {
    color: var(--dvla-gold);
}

/* --------------------------------------------------------
   Chat bubbles
   Use `.chat-user` and `.chat-assistant` wrappers in components.
   -------------------------------------------------------- */
.chat-user {
    margin-left: auto;
    max-width: min(78%, 760px);
    background: var(--dvla-gold);
    color: #1A1A1A;
    padding: 0.8rem 1rem;
    border-radius: var(--dvla-radius-lg) var(--dvla-radius-lg) 4px var(--dvla-radius-lg);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(0, 0, 0, 0.04);
}

.chat-assistant {
    margin-right: auto;
    max-width: min(78%, 760px);
    background: var(--dvla-white);
    color: var(--dvla-text);
    padding: 0.85rem 1rem;
    border-radius: var(--dvla-radius-lg) var(--dvla-radius-lg) var(--dvla-radius-lg) 4px;
    border: 1px solid var(--dvla-border);
    border-left: 5px solid var(--dvla-green);
    box-shadow: var(--dvla-shadow);
}

.chat-meta {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin-bottom: 0.4rem;
    font-weight: 600;
}

.chat-timestamp {
    margin-left: auto;
    font-size: 0.78rem;
    opacity: 0.75;
}

/* --------------------------------------------------------
   Input and forms
   -------------------------------------------------------- */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 12px;
    border: 1px solid var(--dvla-border);
    background: var(--dvla-white);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: var(--dvla-green);
    box-shadow: 0 0 0 3px rgba(0, 107, 63, 0.2);
}

/* --------------------------------------------------------
   Buttons
   -------------------------------------------------------- */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid transparent;
    transition: transform 0.18s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: var(--dvla-green);
    color: var(--dvla-white);
}

.stButton > button[kind="primary"]:hover {
    background: #005734;
    box-shadow: 0 6px 18px rgba(0, 107, 63, 0.28);
    transform: translateY(-1px);
}

/* Secondary/regular button */
.stButton > button:not([kind="primary"]) {
    background: var(--dvla-gold);
    color: #1A1A1A;
    border-color: rgba(0, 0, 0, 0.08);
}

.stButton > button:not([kind="primary"]):hover {
    background: #e6be14;
    box-shadow: 0 6px 18px rgba(252, 209, 22, 0.35);
    transform: translateY(-1px);
}

/* --------------------------------------------------------
   Typing indicator
   -------------------------------------------------------- */
.typing-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: var(--dvla-white);
    border: 1px solid var(--dvla-border);
    border-left: 4px solid var(--dvla-green);
    border-radius: 999px;
    padding: 0.45rem 0.75rem;
    box-shadow: 0 4px 12px rgba(10, 22, 40, 0.08);
}

.typing-indicator span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--dvla-green);
    animation: dvla-typing-bounce 1.2s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.18s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.36s;
}

@keyframes dvla-typing-bounce {
    0%, 80%, 100% {
        transform: translateY(0);
        opacity: 0.45;
    }
    40% {
        transform: translateY(-4px);
        opacity: 1;
    }
}

/* --------------------------------------------------------
   Scrollbars
   -------------------------------------------------------- */
* {
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 107, 63, 0.55) rgba(10, 22, 40, 0.08);
}

*::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

*::-webkit-scrollbar-track {
    background: rgba(10, 22, 40, 0.08);
    border-radius: 10px;
}

*::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--dvla-green), var(--dvla-navy));
    border-radius: 10px;
}

*::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #005734, #081121);
}

/* --------------------------------------------------------
   Footer badge
   -------------------------------------------------------- */
.dvla-footer {
    margin-top: 1.5rem;
    text-align: center;
    color: var(--dvla-muted);
    font-size: 0.82rem;
}

.dvla-footer .claude-badge {
    display: inline-block;
    margin-top: 0.3rem;
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
    background: rgba(10, 22, 40, 0.06);
    border: 1px solid rgba(10, 22, 40, 0.12);
    color: #4B5563;
}

/* --------------------------------------------------------
   Responsive tuning (desktop + tablet)
   -------------------------------------------------------- */
@media (max-width: 1024px) {
    .chat-user,
    .chat-assistant {
        max-width: 88%;
        font-size: 0.97rem;
    }

    .dvla-header {
        padding: 0.8rem 1rem;
    }
}

@media (max-width: 768px) {
    .chat-user,
    .chat-assistant {
        max-width: 94%;
        padding: 0.75rem 0.85rem;
    }

    .dvla-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )
