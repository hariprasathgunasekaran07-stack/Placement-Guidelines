"""
config.py
---------
Central configuration shared by every module. Loads GEMINI_API_KEY from
.env (if present) and exposes:
    - USE_LLM        : True if a valid key is configured AND google.generativeai is installed
    - get_model()    : returns a ready-to-use Gemini model, or raises if
                        called while USE_LLM is False (callers should
                        check USE_LLM first and fall back to rule-based
                        logic, which every module in this project does).

Every other module imports USE_LLM / get_model from here instead of
configuring genai itself, so there's exactly one place that knows about
API keys.
"""

import os
from typing import Any

# Safely load local .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Retrieve API key and filter out common placeholder values
_raw_key = os.environ.get("GEMINI_API_KEY", "").strip()
_placeholders = {
    "", "your_api_key", "your_gemini_api_key", "none",
    "placeholder", "xxx", "your_api_key_here", "your_key_here",
}
GEMINI_API_KEY = "" if _raw_key.lower() in _placeholders else _raw_key

# Safely import google.generativeai without raising errors if not installed
genai: Any = None
_GENAI_AVAILABLE = False
try:
    import google.generativeai as _genai  # type: ignore
    genai = _genai
    _GENAI_AVAILABLE = True
except Exception:
    genai = None
    _GENAI_AVAILABLE = False

LLM_MODEL_NAME = "gemini-1.5-flash"
USE_LLM = bool(GEMINI_API_KEY) and _GENAI_AVAILABLE

# Configure genai if an API key and library are present
if USE_LLM and genai is not None:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        USE_LLM = False


def get_model() -> Any:
    """Returns a ready-to-use GenerativeModel instance or raises RuntimeError if unavailable."""
    if not USE_LLM or not _GENAI_AVAILABLE or genai is None:
        raise RuntimeError(
            "Gemini LLM is not available (check GEMINI_API_KEY in .env or install google-generativeai). "
            "Callers should check USE_LLM before calling get_model()."
        )
    return genai.GenerativeModel(LLM_MODEL_NAME)


DB_PATH = os.environ.get("DB_PATH", "placement.db")
