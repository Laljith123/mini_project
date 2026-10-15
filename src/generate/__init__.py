from src.generate.prompts import (
    CV_ANALYSIS_SYSTEM_PROMPT,
    CV_SUGGESTION_USER_PROMPT,
    JD_GENERATION_SYSTEM_PROMPT,
    JD_GENERATION_USER_PROMPT,
)
from src.generate.cv_suggestions import CVSuggestionEngine
from src.generate.jd_generator import JobDescriptionGenerator

__all__ = [
    "CV_ANALYSIS_SYSTEM_PROMPT",
    "CV_SUGGESTION_USER_PROMPT",
    "JD_GENERATION_SYSTEM_PROMPT",
    "JD_GENERATION_USER_PROMPT",
    "CVSuggestionEngine",
    "JobDescriptionGenerator",
]
